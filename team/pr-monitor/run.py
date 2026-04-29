#!/usr/bin/env python3
"""
PR Monitor — daily checker for Messaging-Connectors active PRs.

Rules: see team/pr-monitor/AGENT.md
DRY_RUN default: 1 (no Teams write, no ADO abandon).
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path

# ---------- config ----------
ADO_ORG = "msdata"
ADO_PROJECT = "Messaging Connectors and Event Streams"
ADO_REPO = "Messaging-Connectors"
ADO_BASE = (
    f"https://dev.azure.com/{ADO_ORG}/"
    f"{urllib.parse.quote(ADO_PROJECT)}/_apis/git/repositories/{ADO_REPO}"
)

BOT_BASE = "https://icm-notification-bot.azurewebsites.net"
TARGET_CONV_ID = "19:785512bc64f946e9b9062b90f176e314@thread.tacv2"

PAT_FILE = Path.home() / ".openclaw/secrets/ado-pat"
SCRIPT_DIR = Path(__file__).resolve().parent
STATE_FILE = SCRIPT_DIR / "state.json"
RUNS_DIR = SCRIPT_DIR / "runs"

DRY_RUN = os.environ.get("PR_MONITOR_DRY_RUN", "1") != "0"

# ---------- helpers ----------
def http(method, url, *, headers=None, body=None, timeout=30):
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode()
            headers = {**(headers or {}), "Content-Type": "application/json"}
        else:
            data = body if isinstance(body, bytes) else str(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

def ado_auth():
    pat = PAT_FILE.read_text().strip()
    return {"Authorization": "Basic " + b64encode(f":{pat}".encode()).decode()}

def fetch_active_prs():
    url = f"{ADO_BASE}/pullrequests?searchCriteria.status=active&$top=200&api-version=7.1"
    code, text = http("GET", url, headers=ado_auth())
    if code != 200:
        raise RuntimeError(f"ADO PR list failed: {code} {text[:300]}")
    return json.loads(text).get("value", [])

def fetch_members():
    url = f"{BOT_BASE}/api/references/{urllib.parse.quote(TARGET_CONV_ID)}/members"
    code, text = http("GET", url)
    if code != 200:
        raise RuntimeError(f"Teams members fetch failed: {code} {text[:300]}")
    return json.loads(text).get("members", [])

# ---------- author matching ----------
_NAME_SUFFIX = re.compile(r"\s*\([^)]*\)\s*$")

def normalize_name(s):
    if not s:
        return ""
    s = _NAME_SUFFIX.sub("", s)
    return s.strip().lower()

def build_member_index(members):
    idx = {}
    for m in members:
        key = normalize_name(m.get("displayName", ""))
        if key and key not in idx:
            idx[key] = m
    return idx

def is_dependabot(author_display):
    if not author_display:
        return False
    a = author_display.lower()
    return "dependabot" in a

def is_security_title(title):
    return bool(title) and "[security]" in title.lower()

# ---------- bucketing ----------
def age_days(creation_iso, now):
    # ADO returns e.g. "2026-04-01T12:34:56.789Z"
    s = creation_iso.replace("Z", "+00:00")
    if "." in s:
        # strip nanos beyond microseconds for fromisoformat
        head, tail = s.split(".", 1)
        # tail like "789+00:00"
        m = re.match(r"(\d+)(.*)$", tail)
        if m:
            frac = m.group(1)[:6]
            s = f"{head}.{frac}{m.group(2)}"
    dt = datetime.fromisoformat(s)
    return int((now - dt).total_seconds() // 86400)

def bucket_pr(pr, now):
    title = pr.get("title", "") or ""
    author = (pr.get("createdBy") or {}).get("displayName", "") or ""
    age = age_days(pr["creationDate"], now)
    urgent = is_dependabot(author) or is_security_title(title)

    if urgent and age >= 30:
        return "abandon", age, urgent
    if age >= 30:
        return "abandon", age, urgent
    if urgent:
        return "urgent", age, urgent
    if 28 <= age <= 29:
        return "ultimatum", age, urgent
    if 5 <= age <= 27:
        return "warn", age, urgent
    return "fresh", age, urgent

# ---------- card rendering ----------
def pr_url(pr):
    pid = pr["pullRequestId"]
    return (
        f"https://dev.azure.com/{ADO_ORG}/"
        f"{urllib.parse.quote(ADO_PROJECT)}/_git/{ADO_REPO}/pullrequest/{pid}"
    )

def short_title(t, n=80):
    t = (t or "").strip()
    return t if len(t) <= n else t[:n - 1] + "…"

def render_card(buckets, mention_index, today_str):
    """Build Adaptive Card body + entities. Returns (activity_dict, unmatched_authors)."""
    body = []
    body.append({
        "type": "TextBlock",
        "text": f"📋 PR Daily Pulse · {today_str}",
        "weight": "Bolder",
        "size": "Large",
        "wrap": True,
    })
    counts = (
        f"Urgent **{len(buckets['urgent'])}**  ·  "
        f"Ultimatum **{len(buckets['ultimatum'])}**  ·  "
        f"Warn **{len(buckets['warn'])}**  ·  "
        f"Abandon (today) **{len(buckets['abandon'])}**  ·  "
        f"Fresh {len(buckets['fresh'])}"
    )
    body.append({"type": "TextBlock", "text": counts, "wrap": True, "spacing": "Small"})

    entities = []
    used_mention_keys = set()
    unmatched = set()

    def at_token_for(author_display):
        key = normalize_name(author_display)
        m = mention_index.get(key)
        if not m:
            unmatched.add(author_display)
            return author_display  # plain text, no entity
        token = f"<at>{m['displayName']}</at>"
        # only add the entity once per author; Teams accepts repeated <at> tags referring to the same entity
        if key not in used_mention_keys:
            entities.append({
                "type": "mention",
                "text": token,
                "mentioned": {"id": m["userId"], "name": m["displayName"]},
            })
            used_mention_keys.add(key)
        return token

    def section(header, items, kind):
        if not items:
            return
        body.append({
            "type": "TextBlock",
            "text": header,
            "weight": "Bolder",
            "size": "Medium",
            "spacing": "Medium",
            "separator": True,
            "wrap": True,
        })
        # group by author
        by_author = {}
        for entry in items:
            a = entry["author"]
            by_author.setdefault(a, []).append(entry)
        for author, group in by_author.items():
            at = at_token_for(author)
            lines = [f"**{at}** — {len(group)} PR(s)"]
            for e in group:
                pr = e["pr"]
                age = e["age"]
                urgent_tag = " ⚠️" if e.get("urgent") else ""
                tag = ""
                if kind == "abandon":
                    tag = "  ·  _will be abandoned today_"
                elif kind == "ultimatum":
                    tag = "  ·  _last warning — abandon at 30d_"
                lines.append(
                    f"- [#{pr['pullRequestId']}]({pr_url(pr)})  "
                    f"`{age}d`{urgent_tag}  {short_title(pr.get('title',''))}{tag}"
                )
            body.append({"type": "TextBlock", "text": "\n".join(lines), "wrap": True})

    section("🚨 Urgent (Dependabot / [SECURITY]) — please merge within 5 days", buckets["urgent"], "urgent")
    section("⛔ Ultimatum (28–29d) — abandon at 30d if not merged", buckets["ultimatum"], "ultimatum")
    section("⏰ Warn (5–27d) — please check in", buckets["warn"], "warn")
    section("🗑️ Abandoned today (≥30d)", buckets["abandon"], "abandon")

    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": body,
    }
    activity = {
        "type": "message",
        "attachments": [
            {"contentType": "application/vnd.microsoft.card.adaptive", "content": card}
        ],
    }
    if entities:
        # Teams shows mentions only when there is a `text` field with the <at> tokens.
        # We add a brief leading text that contains every mention token once,
        # so all @-mentions trigger Activity notifications.
        leading = "PR Daily Pulse — " + " ".join(
            f"<at>{m['displayName']}</at>" for m in
            [mention_index[k] for k in used_mention_keys]
        )
        activity["text"] = leading
        activity["entities"] = entities
    return activity, sorted(unmatched)

# ---------- state ----------
def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ---------- Teams API ----------
def teams_post(activity):
    url = f"{BOT_BASE}/api/activity"
    body = {"conversationId": TARGET_CONV_ID, "activity": activity}
    code, text = http("POST", url, body=body, timeout=60)
    return code, text

def teams_delete(activity_id):
    url = f"{BOT_BASE}/api/activity"
    body = {
        "conversationId": TARGET_CONV_ID,
        "activity": {"type": "messageDelete", "id": activity_id},
    }
    code, text = http("POST", url, body=body, timeout=30)
    return code, text

# ---------- ADO abandon ----------
def ado_abandon(pr_id):
    # 1) post comment thread
    comment_url = (
        f"{ADO_BASE}/pullRequests/{pr_id}/threads?api-version=7.1"
    )
    comment_body = {
        "comments": [{
            "parentCommentId": 0,
            "content": (
                "This PR has been inactive for 30+ days and is being abandoned automatically "
                "by the PR Monitor agent. If still relevant, please reactivate or recreate. "
                "(Rule: see team/pr-monitor/AGENT.md)"
            ),
            "commentType": 1,
        }],
        "status": 1,  # active
    }
    c1, t1 = http("POST", comment_url, headers=ado_auth(), body=comment_body)
    # 2) patch status
    patch_url = f"{ADO_BASE}/pullRequests/{pr_id}?api-version=7.1"
    c2, t2 = http("PATCH", patch_url, headers=ado_auth(), body={"status": "abandoned"})
    return (c1, t1), (c2, t2)

# ---------- main ----------
def main():
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RUNS_DIR / f"{today_str}.md"

    log_lines = [
        f"# PR Monitor Run · {today_str} (UTC {now.strftime('%H:%M')})",
        f"",
        f"DRY_RUN = `{DRY_RUN}`",
        f"",
    ]

    # 1. fetch
    prs = fetch_active_prs()
    members = fetch_members()
    midx = build_member_index(members)

    # 2. PAT owner — best effort: parse from a fresh PR creator? skip; conservative
    #   we just refuse to abandon if creator email == known list. For now, no owner.
    pat_owner = os.environ.get("PR_MONITOR_PAT_OWNER", "").strip().lower()

    # 3. bucket
    buckets = {k: [] for k in ("fresh", "warn", "ultimatum", "urgent", "abandon")}
    for pr in prs:
        author_display = (pr.get("createdBy") or {}).get("displayName", "") or ""
        author_email = ((pr.get("createdBy") or {}).get("uniqueName") or "").lower()
        b, age, urgent = bucket_pr(pr, now)
        entry = {"pr": pr, "age": age, "urgent": urgent, "author": author_display, "email": author_email}
        if b == "abandon" and pat_owner and author_email == pat_owner:
            # safety net
            entry["skip_reason"] = "PAT owner self-PR"
            buckets["warn"].append(entry)
            continue
        buckets[b].append(entry)

    log_lines.append(f"Total active PRs: **{len(prs)}**\n")
    log_lines.append(
        "| Bucket | Count |\n|---|---|\n"
        f"| Urgent | {len(buckets['urgent'])} |\n"
        f"| Ultimatum (28–29d) | {len(buckets['ultimatum'])} |\n"
        f"| Warn (5–27d) | {len(buckets['warn'])} |\n"
        f"| Abandon today (≥30d) | {len(buckets['abandon'])} |\n"
        f"| Fresh (0–4d) | {len(buckets['fresh'])} |\n"
    )

    # 4. render activity
    activity, unmatched = render_card(buckets, midx, today_str)

    # 5. abandon (only if not dry-run)
    abandon_results = []
    for entry in buckets["abandon"]:
        pr = entry["pr"]
        if DRY_RUN:
            abandon_results.append((pr["pullRequestId"], "DRY_RUN: would abandon"))
        else:
            try:
                (c1, _), (c2, t2) = ado_abandon(pr["pullRequestId"])
                ok = (c1 in (200, 201)) and (c2 in (200, 201))
                abandon_results.append((pr["pullRequestId"], f"comment={c1} patch={c2} {'OK' if ok else 'FAIL: ' + t2[:200]}"))
            except Exception as e:
                abandon_results.append((pr["pullRequestId"], f"EXC: {e}"))

    # 6. Teams: delete-then-post
    state = load_state()
    teams_log = []
    if DRY_RUN:
        teams_log.append("DRY_RUN: skipped Teams delete + post")
        # Save activity preview alongside report
        preview_path = RUNS_DIR / f"{today_str}.activity.json"
        preview_path.write_text(json.dumps({"conversationId": TARGET_CONV_ID, "activity": activity}, indent=2))
        teams_log.append(f"Activity preview written: `{preview_path.relative_to(SCRIPT_DIR.parent.parent)}`")
    else:
        prev = state.get("lastActivityId")
        if prev:
            dc, dt = teams_delete(prev)
            teams_log.append(f"DELETE prev `{prev}` → {dc} {dt[:200]}")
        pc, pt = teams_post(activity)
        teams_log.append(f"POST new → {pc} {pt[:300]}")
        if pc == 200:
            try:
                new_id = json.loads(pt).get("activityId")
                state["lastActivityId"] = new_id
                state["lastConversationId"] = TARGET_CONV_ID
                state["lastRunUtc"] = now.isoformat()
                save_state(state)
                teams_log.append(f"State saved: lastActivityId=`{new_id}`")
            except Exception as e:
                teams_log.append(f"State save failed: {e}")

    # 7. write report
    log_lines.append("\n## Buckets\n")
    for name in ("urgent", "ultimatum", "warn", "abandon"):
        items = buckets[name]
        log_lines.append(f"\n### {name} ({len(items)})\n")
        if not items:
            log_lines.append("(empty)\n")
            continue
        for e in items:
            pr = e["pr"]
            log_lines.append(
                f"- #{pr['pullRequestId']} · {e['age']}d · {e['author']} · "
                f"{short_title(pr.get('title',''), 100)}  ([link]({pr_url(pr)}))"
                f"{' · skip: ' + e['skip_reason'] if e.get('skip_reason') else ''}"
            )

    if abandon_results:
        log_lines.append("\n## Abandon results\n")
        for pid, msg in abandon_results:
            log_lines.append(f"- #{pid}: {msg}")

    log_lines.append("\n## Teams\n")
    for line in teams_log:
        log_lines.append(f"- {line}")

    if unmatched:
        log_lines.append("\n## Unmatched authors (no Teams member, sent as plain text)\n")
        for n in unmatched:
            log_lines.append(f"- {n}")

    report_path.write_text("\n".join(log_lines) + "\n")
    print(f"Wrote {report_path}")
    print(f"DRY_RUN={DRY_RUN}")

if __name__ == "__main__":
    main()
