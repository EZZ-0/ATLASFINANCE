# VALIDATION QUEUE

**Purpose:** Track features awaiting R&D validation.  
**Owner:** R&D Agent  
**Protocol:** Architects/Executor submit here after feature completion.

---

## HOW THIS WORKS

1. **Development agents** complete a feature
2. **Development agents** add entry to PENDING section below
3. **R&D Agent** reviews the queue when called
4. **R&D Agent** creates validation report in this folder
5. **R&D Agent** updates status to VALIDATED or NEEDS_WORK

---

## SUBMISSION TEMPLATE

```markdown
### VALIDATION-[XXX]: [Feature Name]
- **Submitted By:** [Architect/Executor]
- **Submitted:** [YYYY-MM-DD HH:MM]
- **Priority:** P0 / P1 / P2
- **Status:** PENDING

**Description:**
[What was implemented/changed]

**Files Changed:**
- [file1.py] - [description]
- [file2.py] - [description]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Test Instructions:**
[How R&D can verify this works]

**Related:**
- [Task IDs, decisions, documentation]
```

---

## PENDING VALIDATION

<!-- New submissions go here. R&D processes from top to bottom. -->

[No pending validations]

---

## IN REVIEW

<!-- R&D is currently reviewing these -->

[None]

---

## COMPLETED VALIDATIONS

| ID | Feature | Submitted | Validated | Result | Report |
|----|---------|-----------|-----------|--------|--------|
| - | - | - | - | - | - |

---

## VALIDATION RESULTS KEY

| Result | Meaning | Action |
|--------|---------|--------|
| PASSED | Meets all criteria | Feature is production-ready |
| PASSED_WITH_NOTES | Mostly good, minor improvements suggested | Optional follow-up |
| NEEDS_WORK | Issues found | Must address before release |
| BLOCKED | Cannot validate | Missing info or dependencies |

---

## FOR R&D AGENT

When validating:

1. Read the submission carefully
2. Review all changed files
3. Run tests if applicable
4. Check against acceptance criteria
5. Create validation report: `VALIDATION_[FEATURE]_[DATE].md`
6. Update status in this file
7. If NEEDS_WORK: add specific issues to resolve

Report Template Location: Use standard R&D report format with VALIDATION prefix.

---

## NOTES

- P0 validations should be reviewed ASAP
- Validation reports go in this folder (OperationsValidation/)
- R&D research reports go in RnD/ folder (different purpose)
- Always cross-reference with COMPLETED_TASKS.md in OperationRoom/

