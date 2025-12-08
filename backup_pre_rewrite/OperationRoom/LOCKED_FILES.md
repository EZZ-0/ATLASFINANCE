# LOCKED FILES

<!-- 
DATA FILE: Files currently claimed for editing.
For locking protocol, see: OPERATION_ROOM_GUIDE.txt
-->

---

## CURRENTLY LOCKED FILES

| File | Locked By | Since | Purpose | ETA Release |
|------|-----------|-------|---------|-------------|
| - | - | - | - | - |

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

