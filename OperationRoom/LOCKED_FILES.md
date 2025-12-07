# LOCKED FILES

**Purpose:** Prevent merge conflicts by claiming files before editing.  
**Protocol:** ALWAYS claim a file before editing. Release when done.

---

## HOW TO USE

### Before Editing Any File:

1. Check if file is already locked below
2. If locked by other agent: WAIT or coordinate in LIVE_CHAT
3. If not locked: Add your lock entry
4. Notify in LIVE_CHAT: "[LOCK] Claimed [file] for [purpose]"

### After Finishing:

1. Remove your lock entry from this file
2. Notify in LIVE_CHAT: "[UNLOCK] Released [file]"

---

## CURRENTLY LOCKED FILES

| File | Locked By | Since | Purpose | ETA Release |
|------|-----------|-------|---------|-------------|
| - | - | - | - | - |

---

## LOCK RULES

1. **One agent per file** - No exceptions
2. **Lock before first edit** - Not after
3. **Release promptly** - Don't hoard files
4. **Communicate** - Always post [LOCK]/[UNLOCK] in LIVE_CHAT
5. **Emergency override** - If agent unresponsive 30+ min, other can claim with [FORCE_UNLOCK]

---

## LOCK TEMPLATE

```
| usa_backend.py | ARCHITECT | 2025-12-07 14:30 | Adding Treasury API | ~1 hour |
```

---

## CONFLICT RESOLUTION

If both agents need same file:

1. Check who has higher priority task (P0 > P1 > P2)
2. Higher priority gets the file
3. Lower priority waits or works on different task
4. If same priority: Architect decides

---

## FORCE UNLOCK PROTOCOL

Only use if:
- Other agent hasn't responded in 30+ minutes
- Urgent need (P0 task blocked)

Process:
1. Post in LIVE_CHAT: "[FORCE_UNLOCK] Taking [file] - [reason]"
2. Remove their lock, add yours
3. Document in BLOCKERS.md if concerning

