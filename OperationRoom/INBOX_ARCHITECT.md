# INBOX: ARCHITECT

**Owner:** Architect Agent  
**Purpose:** Tasks and requests assigned TO the Architect  
**Protocol:** Check this file BEFORE and AFTER every action

---

## CRITICAL: AUTONOMOUS OPERATION SIGNALS

As Architect, you MUST use these signals in LIVE_CHAT.md:

| Signal | When to Use |
|--------|-------------|
| `[TASK_READY] TASK-EXXX` | After creating complete task for Executor |
| `[ALL_TASKS_ASSIGNED]` | When no more Executor tasks will be created |
| `[SESSION_COMPLETE]` | When ALL work is done (yours + Executor's validated) |
| `[DECISION_NEEDED]` | When User must provide input |

Work CONTINUOUSLY until session complete. Don't stop after small steps.

---

## ⚠️ ERROR REPORTING

If you experience ANY problem:

```
[TIMESTAMP] [ARCHITECT]: [AGENT_ERROR] @USER
Problem: [What's wrong]
Impact: [What this blocks]
Tried: [What you attempted]
Need: [What would help]
```

If Executor is not following protocol:

```
[TIMESTAMP] [ARCHITECT]: [PROTOCOL_BREAK] @USER @EXECUTOR
Issue: [What they're doing wrong]
Expected: [What should happen]
Actual: [What is happening]
```

**STOP and wait for User response before continuing.**

---

## HOW TO USE THIS INBOX

### For Architect (Owner):
1. Check this inbox before starting any work
2. Acknowledge tasks by changing status to `ACKNOWLEDGED`
3. Update status as you work: `IN_PROGRESS` → `COMPLETED`
4. Move completed tasks to COMPLETED_TASKS.md

### For Executor (Sender):
1. Add new tasks at the BOTTOM of the PENDING section
2. Use the task template below
3. Set appropriate priority (P0 = urgent, P1 = high, P2 = normal)

---

## TASK TEMPLATE

```markdown
### TASK-A[XXX]: [Task Title]
- **From:** Executor
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

<!-- New tasks go here. Architect processes from top to bottom. -->

[No pending tasks]

---

## ACKNOWLEDGED TASKS

<!-- Tasks the Architect has seen and will work on -->

[None]

---

## NOTES

- P0 tasks require IMMEDIATE attention (interrupt current work)
- P1 tasks should be started within the current session
- P2 tasks can be queued for later
- Always update LIVE_CHAT.md when acknowledging a task

