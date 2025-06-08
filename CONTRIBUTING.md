# Contributing Guidelines

Thank you for considering contributing to this project. We welcome improvements of all kinds.

## Commit Messages

Use concise commit messages following the pattern:

```
<module>: short summary
```

- Replace `<module>` with the area or file affected.
- Summaries should be in the imperative mood (e.g., "update logger", "fix bug").
- When helpful, add a blank line and include **why** the change is needed in the commit body.

Examples:

```
logger: improve file rotation

enables daily log cleanup
```

```
ui: fix chart rendering when data empty
```

## Pull Requests

- Keep changes focused; unrelated fixes should be in separate commits.
- Update tests when you modify functionality and ensure `pytest` passes.

We appreciate your help!
