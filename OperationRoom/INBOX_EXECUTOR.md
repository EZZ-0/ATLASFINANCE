# INBOX: EXECUTOR

**Owner:** Executor Agent  
**Purpose:** Tasks and requests assigned TO the Executor  
**Protocol:** Check this file BEFORE and AFTER every action

---

## CRITICAL: AUTONOMOUS OPERATION MODE

When User sends "." you enter **CONTINUOUS WORK MODE**:

1. **If inbox has tasks with [TASK_READY] signal** → Execute them
2. **If inbox has tasks but NO [TASK_READY]** → Wait, task is being written
3. **If inbox is EMPTY** → Post [WAITING_FOR_TASKS], keep checking
4. **NEVER STOP** until you see [SESSION_COMPLETE] from Architect

You DO NOT receive instructions from User directly.
ALL your tasks come from Architect via this file.
Look for [TASK_READY] signal in LIVE_CHAT before starting any task.

---

## ⚠️ ERROR REPORTING

If you experience ANY problem:

```
[TIMESTAMP] [EXECUTOR]: [AGENT_ERROR] @USER
Problem: [What's wrong]
Impact: [What this blocks]
Tried: [What you attempted]
Need: [What would help]
```

If Architect is not following protocol:

```
[TIMESTAMP] [EXECUTOR]: [PROTOCOL_BREAK] @USER @ARCHITECT
Issue: [What they're doing wrong]
Expected: [What should happen]
Actual: [What is happening]
```

**STOP and wait for User response before continuing.**

---

## HOW TO USE THIS INBOX

### For Executor (Owner):
1. Check this inbox before starting any work
2. Acknowledge tasks by changing status to `ACKNOWLEDGED`
3. Update status as you work: `IN_PROGRESS` → `COMPLETED`
4. Move completed tasks to COMPLETED_TASKS.md

### For Architect (Sender):
1. Add new tasks at the BOTTOM of the PENDING section
2. Use the task template below
3. Set appropriate priority (P0 = urgent, P1 = high, P2 = normal)

---

## TASK TEMPLATE

```markdown
### TASK-E[XXX]: [Task Title]
- **From:** Architect
- **Priority:** P0 / P1 / P2
- **Created:** [YYYY-MM-DD HH:MM]
- **Deadline:** [Optional]
- **Est. Time:** [e.g., 2 hours, 30 min]
- **Status:** PENDING

**Dependencies:**
- **Depends On:** [Task IDs that must complete first, or "None"]
- **Blocks:** [Task IDs waiting on this, or "None"]

**Description:**
[Clear description of what needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Context/Files:**
- [Relevant file paths]
- [Related decisions]

**Current State:** (For handoffs)
- [Where previous work stopped]
- [What's already done]
- [What's remaining]

**Expected Output:**
[What should be delivered]

**Rollback Plan:**
[If this breaks something, how to undo - or "N/A" for low-risk tasks]
```

---

## PENDING TASKS

<!-- New tasks go here. Executor processes from top to bottom. -->

[No pending tasks]

---

## ACKNOWLEDGED TASKS

<!-- Tasks the Executor has seen and will work on -->

[None]

---

## NOTES

- P0 tasks require IMMEDIATE attention (interrupt current work)
- P1 tasks should be started within the current session
- P2 tasks can be queued for later
- Always update LIVE_CHAT.md when acknowledging a task
- Complex tasks may be escalated back to Architect

