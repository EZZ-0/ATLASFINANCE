# BLOCKERS

**Purpose:** Track all issues preventing task completion.  
**Protocol:** Add blocker immediately when encountered. Remove when resolved.

---

## ACTIVE BLOCKERS

<!-- Format: One blocker per section. Most urgent at top. -->

### [No active blockers]

---

## BLOCKER TEMPLATE

```markdown
### BLOCKER-[XXX]: [Title]
- **Reported By:** [Agent]
- **Reported:** [YYYY-MM-DD HH:MM]
- **Blocking:** [Task ID or description]
- **Severity:** CRITICAL / HIGH / MEDIUM
- **Status:** OPEN / INVESTIGATING / WAITING / RESOLVED

**Description:**
[What is the blocker?]

**Impact:**
[What cannot proceed because of this?]

**Attempted Solutions:**
1. [What was tried]
2. [What was tried]

**Needs:**
[What is required to unblock?]

**Owner:** [Who is working on resolution]
```

---

## RECENTLY RESOLVED

| Blocker ID | Title | Resolved | Solution |
|------------|-------|----------|----------|
| - | - | - | - |

---

## ESCALATION PATH

1. **Agent-to-Agent:** Post in LIVE_CHAT.md with [BLOCKED] prefix
2. **Technical:** Check existing documentation and R&D reports
3. **External:** Flag for user attention in MISSION_CONTROL.md

---

## NOTES

- CRITICAL blockers: Stop all work, address immediately
- HIGH blockers: Address within current session
- MEDIUM blockers: Can work around temporarily
- Always update ACTIVE_TASKS.md when blocked

