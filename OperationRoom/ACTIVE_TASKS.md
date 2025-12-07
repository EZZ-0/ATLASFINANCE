# ACTIVE TASKS

<!-- 
DATA FILE: Currently in-progress work.
For protocols, see: OPERATION_ROOM_GUIDE.txt
-->

---

## ARCHITECT: CURRENTLY WORKING ON

| Task ID | Description | Started | Status | Notes |
|---------|-------------|---------|--------|-------|
| TASK-A007 | earnings_revisions.py design | 2025-12-08 00:36 | ✅ DONE | Combined with A008 |
| TASK-A008 | Revision tracking logic | 2025-12-08 00:36 | ✅ DONE | In A007 |
| TASK-A009 | Revision visualization | 2025-12-08 00:50 | ✅ DONE | 4 chart functions |
| TASK-A010 | UI integration | 2025-12-08 00:55 | ✅ DONE | Earnings tab updated |
| TASK-A011 | Enhance earnings with FMP | 2025-12-08 02:32 | ✅ DONE | fmp_earnings.py + integration |
| TASK-A012 | Design insider_transactions.py | 2025-12-08 01:35 | ✅ DONE | 770 lines, VALIDATED |
| TASK-A013 | UI integration | 2025-12-08 01:50 | ✅ DONE | Insider tab, VALIDATED |
| TASK-A014 | SEC EDGAR module | 2025-12-08 01:55 | ✅ DONE | sec_edgar.py, VALIDATED |
| TASK-A015 | Institutional ownership module | 2025-12-08 02:10 | ✅ DONE | 635 lines, VALIDATED |
| TASK-A016 | Add Ownership tab to UI | 2025-12-08 02:45 | ✅ DONE | Ownership tab + charts |

## EXECUTOR: PENDING (BATCH READY)

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| TASK-E011 | yfinance research | None | ⬜ PENDING |
| TASK-E012 | FMP research | None | ⬜ PENDING |
| TASK-E013 | Alpha Vantage research | None | ⬜ PENDING |
| TASK-E014 | Live extraction | E011 | ⬜ PENDING |
| TASK-E015 | API comparison | E011-E013 | ⬜ PENDING |
| TASK-E016 | Data summary | E014-E015 | ⬜ PENDING |

---

## EXECUTOR: CURRENTLY WORKING ON

| Task ID | Description | Started | Status | Notes |
|---------|-------------|---------|--------|-------|
| - | [No active tasks] | - | - | - |

---

## BLOCKED TASKS

| Task ID | Owner | Blocked By | Waiting On | Since |
|---------|-------|------------|------------|-------|
| - | - | - | - | - |

---

## HANDOFF IN PROGRESS

| Task ID | From | To | Handoff Time | Context |
|---------|------|-----|--------------|---------|
| - | - | - | - | - |

---

## STATUS LEGEND

| Status | Meaning |
|--------|---------|
| `IN_PROGRESS` | Actively being worked on |
| `PAUSED` | Temporarily stopped (will resume) |
| `BLOCKED` | Cannot proceed without external input |
| `REVIEW` | Completed, awaiting cross-validation |
| `HANDOFF` | Being transferred to other agent |

---

## NOTES

- Only ONE task should be IN_PROGRESS per agent at a time (focus)
- Blocked tasks must have a corresponding entry in BLOCKERS.md
- Cross-validation tasks appear in both agents' sections briefly

