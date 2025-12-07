# DECISIONS LOG

**Purpose:** Record all significant decisions made during development.  
**Protocol:** Log decisions when made. Reference in future discussions.

---

## HOW TO USE

1. Log all architecture, design, and process decisions
2. Include rationale (why this choice?)
3. Note alternatives considered
4. Reference in tasks/discussions for context

---

## DECISION TEMPLATE

```markdown
### DECISION-[XXX]: [Title]
- **Date:** [YYYY-MM-DD]
- **Made By:** [Agent(s)]
- **Category:** Architecture / Design / Process / Data / UI

**Decision:**
[What was decided]

**Rationale:**
[Why this choice was made]

**Alternatives Considered:**
1. [Alternative 1] - [Why rejected]
2. [Alternative 2] - [Why rejected]

**Impact:**
[What this affects]

**References:**
- [Related files/tasks]
```

---

## DECISIONS LOG

<!-- Most recent at top -->

### DECISION-001: Operation Room Protocol Established
- **Date:** 2025-12-07
- **Made By:** User + R&D Agent
- **Category:** Process

**Decision:**
Implement file-based multi-agent coordination system ("Operation Room") for Architect and Executor agents to collaborate.

**Rationale:**
- Cursor agents cannot directly communicate
- File-based coordination simulates real-time collaboration
- Based on established patterns (Blackboard, Contract Net Protocol)

**Alternatives Considered:**
1. Manual copy-paste between chats - Too error-prone
2. External multi-agent framework (CrewAI) - Overkill for 2 agents

**Impact:**
- New folder structure: OperationRoom/, OperationsValidation/
- Agents must follow check-before-after protocol
- R&D validates all completed work

**References:**
- OperationRoom/OPERATION_ROOM_GUIDE.txt

---

### DECISION-002: Architect-Only Git Operations
- **Date:** 2025-12-07
- **Made By:** User
- **Category:** Process

**Decision:**
Only Architect agent can run git commands (add, commit, push). Executor is prohibited from git operations.

**Rationale:**
- Single source of truth for commits
- Clean, organized commit history
- No merge conflicts between agents
- Minimizes coordination overhead
- Architect reviews all changes before committing

**Alternatives Considered:**
1. Both agents commit independently - Risk of conflicts
2. Executor commits with Architect review - Extra coordination

**Impact:**
- Executor marks [DONE], Architect commits the work
- All git operations centralized
- Cleaner repository history

**References:**
- OPERATION_ROOM_GUIDE.txt Rule 7

---

## NOTES

- Reference past decisions to avoid re-discussing settled issues
- Update if a decision is reversed or modified
- Use for onboarding new agents to understand project history

