# LIVE CHAT

**Purpose:** Real-time conversation between Agents and User.  
**Participants:** USER, ARCHITECT, EXECUTOR  
**Protocol:** Check this file BEFORE and AFTER every action you take.

---

## HOW TO USE

### For Agents:
1. **Read** the latest messages when you start any action
2. **Write** your message at the BOTTOM of this file
3. **Format:** `[TIMESTAMP] [AGENT]: Message`

### For User:
1. You CAN write directly in this file to communicate with agents
2. **Format:** `[TIMESTAMP] [USER]: Message`
3. Use `@ARCHITECT` or `@EXECUTOR` to direct message
4. Agents will see your message on their next check

## MESSAGE PREFIXES

| Prefix | Use When |
|--------|----------|
| `[URGENT]` | Immediate attention needed |
| `[Q]` | Question - need response before continuing |
| `[A]` | Answer to a question |
| `[UPDATE]` | Status update |
| `[DONE]` | Task completed |
| `[SYNC]` | Session start - waiting for other agent |
| `[STATUS]` | Requesting/providing full status dump |
| `[LOCK]` | Claiming a file for editing |
| `[UNLOCK]` | Releasing a file |
| `[BLOCKED]` | Cannot proceed, need help |
| `[HANDOFF]` | Transferring work to other agent |
| `[TASK_READY]` | Architect: Task ready for Executor |
| `[WAITING_FOR_TASKS]` | Executor: Inbox empty, standing by |
| `[ALL_TASKS_ASSIGNED]` | Architect: No more tasks coming |
| `[SESSION_COMPLETE]` | Architect: All work done |
| `[AGENT_ERROR]` | Problem occurred - report to @USER |
| `[PROTOCOL_BREAK]` | Other agent not following protocol |

## SYNC PROTOCOL (Session Start)

At the START of each session, both agents must sync:

1. Read MISSION_CONTROL.md for current priorities
2. Post: `[SYNC] Online. Current: [what you're working on]`
3. Wait for other agent's [SYNC] if they're active
4. Check LOCKED_FILES.md before starting work
5. Proceed with work

## STATUS COMMAND

When you need a quick overview, post:
`[STATUS] Request`

The other agent (or yourself) responds with:
```
[STATUS] Dump:
- Current Task: [task ID and description]
- Status: [IN_PROGRESS/BLOCKED/AVAILABLE]
- Files Locked: [list or "none"]
- Blockers: [any blockers or "none"]
- Next: [what you'll do next]
```

## DAILY ARCHIVE

When chat exceeds ~50 messages:
1. Copy everything below "CONVERSATION LOG" line
2. Save to: CHAT_ARCHIVE/CHAT_[YYYY-MM-DD].md
3. Clear this file (keep header + one [SYSTEM] message)

---

## MESSAGE FORMAT EXAMPLES

```
[2025-12-07 14:30] [ARCHITECT]: Starting work on DCF validation module.
[2025-12-07 14:32] [EXECUTOR]: [Q] Should I use the existing validation_engine.py or create new?
[2025-12-07 14:35] [ARCHITECT]: [A] Use existing, add new methods to DataValidator class.
[2025-12-07 14:40] [EXECUTOR]: [UPDATE] Added 3 new validation methods, testing now.
[2025-12-07 14:50] [EXECUTOR]: [DONE] Validation methods complete. See lines 150-220.
[2025-12-07 14:51] [ARCHITECT]: [URGENT] Found bug in line 180, division by zero possible.
```

---

## CONVERSATION LOG

<!-- New messages go BELOW this line. Most recent at bottom. -->

[2025-12-07 21:00] [SYSTEM]: Operation Room initialized. Agents may begin communication.

[2025-12-07 21:15] [SYSTEM]: Guide updated to v3.0 - AUTONOMOUS OPERATION. Key changes:
- Both agents work CONTINUOUSLY until [SESSION_COMPLETE]
- Executor WAITS for tasks if inbox empty (doesn't stop)
- Key signals: [TASK_READY], [WAITING_FOR_TASKS], [ALL_TASKS_ASSIGNED], [SESSION_COMPLETE]
- User only needs to intervene for [DECISION_NEEDED] or [BLOCKED]
- Minimal stop-start, maximum autonomous work

[2025-12-07 21:30] [SYSTEM]: Error reporting protocol added:
- [AGENT_ERROR] @USER = Problem with own function, STOP and report
- [PROTOCOL_BREAK] @USER @OTHER_AGENT = Other agent not following protocol
- Both agents must IMMEDIATELY report any problems to User and each other


