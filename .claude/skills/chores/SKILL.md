---
name: chores
description: "Update README.md, CHANGELOG.md, CLAUDE.md, and VERSION based on recent changes in the current branch."
user_invocable: true
---

You are updating the project's documentation and version files to reflect recent work on the current branch. Follow these steps precisely.

---

## Step 1: Gather recent changes

Run these commands to understand what changed on the current branch since it diverged from `main`:

```bash
git log main..HEAD --oneline
git diff main..HEAD --stat
git diff main..HEAD
```

Read the full diffs carefully. Identify:
- New files and modules added
- Functions/classes added, changed, or removed
- Bug fixes
- Refactors or renames
- Test additions or changes
- Config/CI changes

---

## Step 2: Determine the version bump

Read the current `VERSION` file. Decide the bump based on the changes:
- **Patch** (0.1.2 → 0.1.3): Bug fixes, minor improvements, test additions, doc updates
- **Minor** (0.1.2 → 0.2.0): New features, new modules, new public API functions
- **Major** (0.1.2 → 1.0.0): Breaking changes to existing public API

Ask the user to confirm the version bump before proceeding. Show them what changed and your recommendation.

---

## Step 3: Update VERSION

Write the new version string to `VERSION` (single line, no trailing newline beyond what's standard).

---

## Step 4: Update CHANGELOG.md

Read the current `CHANGELOG.md`. Add a new section under `## [Unreleased]` or replace it with the new version heading. Follow the existing format exactly (Keep a Changelog style):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Removed
- ...
```

Rules:
- Use today's date.
- Only include sections (Added/Changed/Removed/Fixed) that apply.
- Each entry should be a concise, user-facing description — not a commit message.
- Reference module paths where helpful (e.g., "`brokers.alpaca.performance_ops`").
- Move any existing `[Unreleased]` items into the new version section if they are covered by the branch changes. Leave `## [Unreleased]` as an empty heading at the top for future work.

---

## Step 5: Update README.md

Read the current `README.md`. Update only the sections affected by the branch changes:

- **Features list**: Add or update bullet points for new/changed features.
- **Usage Examples**: Add examples for new public functions. Follow the existing code example style (imports, comments, print statements).
- **Library Structure**: Update the tree if files were added or removed.
- **Core Modules**: Add/update function signatures and descriptions for new/changed public API.
- **Test Coverage**: Update the test file list if new test files were added.

Rules:
- Do NOT rewrite unchanged sections.
- Match the existing tone, formatting, and level of detail.
- Keep examples minimal but complete (copy-pasteable).

---

## Step 6: Update CLAUDE.md

Read the current `CLAUDE.md`. Update only what's affected:

- **Commands**: Update if build/test/run commands changed.
- **Architecture**: Update if new modules, key classes, or patterns were added.
- **Key patterns**: Update if new conventions or important design decisions were introduced.
- **CI**: Update if workflow changed.

Rules:
- Keep it concise — CLAUDE.md is for orientation, not exhaustive docs.
- Don't duplicate what's easily discoverable from the code.

---

## Step 7: Present a summary

Show the user a brief summary of all changes made across the four files. Do NOT commit — let the user decide when to commit.
