# leetcode-sync

> Sync your LeetCode accepted submissions into a Git repository.

Whenever you solve and successfully submit a LeetCode problem, `leetcode-sync` detects the new accepted submission, fetches its metadata and submitted code, organizes it into a Git repository, generates documentation, updates topic indexes, and optionally commits + pushes to GitHub.

## Architecture

```
LeetCode Accepted Submission
        ↓
leetcode-sync
        ↓
Fetch problem metadata + submitted code
        ↓
Determine problem topics
        ↓
Create/update files
        ↓
Update topic indexes
        ↓
Update repository statistics
        ↓
git add → git commit → git push
```

## Installation

```bash
# Clone the repository
git clone https://github.com/user/leetcode-sync.git
cd leetcode-sync

# Install with uv
uv sync --all-extras

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

```bash
# 1. Initialize a new project
leetcode-sync init

# 2. Set up authentication
leetcode-sync auth

# 3. Sync your submissions
leetcode-sync sync

# 4. Push to GitHub
leetcode-sync push
```

## Authentication

`leetcode-sync` uses browser session cookies for authentication. **It never asks for your password.**

1. Log in to [leetcode.com](https://leetcode.com) in your browser
2. Open Developer Tools (F12)
3. Go to Application → Cookies → leetcode.com
4. Copy `LEETCODE_SESSION` and `csrftoken` values
5. Add them to your `.env` file:

```env
LEETCODE_SESSION=your_session_cookie_here
LEETCODE_CSRF_TOKEN=your_csrf_token_here
```

## Configuration

Environment variables (set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LEETCODE_SESSION` | - | LeetCode session cookie |
| `LEETCODE_CSRF_TOKEN` | - | CSRF token |
| `LEETCODE_REPO_PATH` | - | Path to solutions repository |
| `GIT_AUTO_COMMIT` | `false` | Auto-commit after sync |
| `GIT_AUTO_PUSH` | `false` | Auto-push after commit |
| `WATCH_INTERVAL` | `120` | Polling interval in seconds |

## CLI Commands

| Command | Description |
|---------|-------------|
| `leetcode-sync init` | Initialize a new project |
| `leetcode-sync auth` | Show authentication instructions |
| `leetcode-sync sync` | Sync accepted submissions |
| `leetcode-sync sync --dry-run` | Preview changes without applying |
| `leetcode-sync status` | Show current sync status |
| `leetcode-sync git-status` | Show git status |
| `leetcode-sync commit` | Commit synced changes |
| `leetcode-sync push` | Push to remote |
| `leetcode-sync watch` | Watch for new submissions |
| `leetcode-sync version` | Show version |

## Generated Repository Structure

```
leetcode/
├── 0001-two-sum/
│   ├── solution.py
│   └── README.md
├── 0020-valid-parentheses/
│   ├── solution.py
│   └── README.md
├── 0121-best-time-to-buy-and-sell-stock/
│   ├── solution.py
│   └── README.md
└── ...

topics/
├── array.md
├── hash-table.md
├── linked-list.md
├── dynamic-programming.md
└── ...

.leetcode-sync/
└── state.json
```

## Example Workflow

```bash
$ leetcode-sync sync

Checking LeetCode...

Found 2 new accepted submissions.

✓ #121 Best Time to Buy and Sell Stock
  Difficulty: Easy
  Topics: Array, Dynamic Programming

✓ #206 Reverse Linked List
  Difficulty: Easy
  Topics: Linked List, Recursion

Generated:
leetcode/0121-best-time-to-buy-and-sell-stock/
leetcode/0206-reverse-linked-list/

Done.
```

## Watch Mode

```bash
# Poll every 2 minutes
leetcode-sync watch --interval 120

# Auto-commit and push
leetcode-sync watch --auto-commit --auto-push
```

Press `Ctrl+C` to stop gracefully.

## Git Integration

- Never force pushes
- Never resets the repository
- Never overwrites unrelated files
- Warns before staging unrelated modifications

## Security

- `.env` is always gitignored
- Cookies are never logged or exposed
- Credentials are never committed to Git
- README never contains secrets

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linter
uv run ruff check src/ tests/

# Run type checker
uv run mypy src/
```

## Project Structure

```
src/leetcode_sync/
├── __init__.py
├── cli.py              # CLI commands
├── config.py           # Configuration management
├── models.py           # Pydantic data models
├── leetcode/
│   ├── client.py       # LeetCode API client
│   ├── graphql.py      # GraphQL queries
│   └── submissions.py  # Submission processing
├── generator/
│   ├── solution.py     # Solution file generator
│   ├── readme.py       # README generator
│   └── topics.py       # Topic index generator
├── git/
│   └── manager.py      # Git operations
├── storage/
│   └── state.py        # State persistence
└── utils/
    └── slugify.py      # Slugification utilities
```

## Roadmap

- [x] Phase 1: Project structure and CLI skeleton
- [ ] Phase 2: LeetCode authentication and client
- [ ] Phase 3: Problem metadata and source code retrieval
- [ ] Phase 4: File generation and sync
- [ ] Phase 5: Topic indexes and statistics
- [ ] Phase 6: Git manager
- [ ] Phase 7: Watch mode
- [ ] Phase 8: Polish and documentation
- [ ] Future: Browser extension integration
- [ ] Future: AI-powered approach documentation

## License

MIT

<!-- LEETCODE_STATS_START -->
## Progress

| Difficulty | Solved |
|------------|--------|
| Easy | 6 |
| Medium | 14 |
| Hard | 0 |
| Total | 20 |

## Topics

| Topic | Problems |
|-------|----------|
| Linked List | 18 |
| Array | 8 |
| Hash Table | 7 |
| Design | 7 |
| Recursion | 4 |
| Two Pointers | 4 |
| Doubly-Linked List | 4 |
| Stack | 3 |
| Simulation | 3 |
| Math | 2 |
| Heap (Priority Queue) | 2 |
| Hash Function | 2 |
| Data Stream | 2 |
| Greedy | 1 |
| Bit Manipulation | 1 |
| Queue | 1 |
| Monotonic Stack | 1 |
| Ordered Set | 1 |
<!-- LEETCODE_STATS_END -->
