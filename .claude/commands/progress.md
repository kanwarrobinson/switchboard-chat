# /progress

Views and updates the project progress tracker.

## Usage

```
/progress
/progress done "task description"
/progress add "task description"
/progress issue "description of known issue"
```

## What it does

- **No args**: Read and display `PROGRESS.md`
- **`done "..."`**: Move a pending item to the ✅ Done section in `PROGRESS.md`
- **`add "..."`**: Add a new item to the 📌 Pending section
- **`issue "..."`**: Add to the 🐛 Known Issues section

## File location

`PROGRESS.md` in the project root.

## Notes

- Always read `PROGRESS.md` at the start of a session
- Keep this file up to date — it is the single source of truth for project state
- When completing a task, move it from Pending → In Progress → Done
