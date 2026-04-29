#!/usr/bin/env bash
# PR Monitor daily runner. Cron: 0 1 * * * UTC = 09:00 BJT.
# DRY_RUN=0 → really posts to Teams.  NO_ABANDON=1 → still does NOT call ADO abandon.
set -e
cd /home/azureuser/.openclaw/workspace/team/pr-monitor
LOG_DIR=/home/azureuser/.openclaw/workspace/team/pr-monitor/runs
mkdir -p "$LOG_DIR"
DATE=$(date -u +%F)
PR_MONITOR_DRY_RUN=0 PR_MONITOR_NO_ABANDON=1 \
  /usr/bin/python3 run.py >> "$LOG_DIR/$DATE.cron.log" 2>&1
