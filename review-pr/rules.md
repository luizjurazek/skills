# Code Review Rules (baked-in, generic)

Baseline, framework- and language-agnostic checklist applied to every review.
Repo-specific conventions discovered at review time (`CLAUDE.md`, `.cursor/rules/`,
styleguide docs, `CONTRIBUTING.md`, linter/formatter configs — see
[SKILL.md](SKILL.md) §2.4) take precedence over this file on any topic they
cover; this file still applies wherever the repo is silent.

## 1. Correctness & Edge Cases

- Logic errors, off-by-one mistakes, incorrect boundary conditions.
- Null/undefined/None/empty-collection handling.
- Incorrect assumptions about input shape, type, or ordering.
- Race conditions and shared-state mutation across concurrent paths.
- Unhandled promise rejections / async errors.
- Incorrect or swallowed error propagation.
- Unreachable code or dead branches introduced by the change.

## 2. Security

- Missing input validation or sanitization on user-controlled data.
- Injection risks: SQL/NoSQL, command, template, XSS.
- Missing authentication/authorization checks on sensitive routes or actions.
- Secrets, tokens, or credentials committed to code, logs, or config.
- Unsafe deserialization of untrusted data.
- Server-side request forgery (SSRF) via user-controlled URLs.
- Path traversal via user-controlled file paths.
- Obviously outdated or vulnerable dependencies, if evident from the diff.

## 3. Performance

- N+1 query patterns.
- Unnecessary loops, allocations, or recomputation.
- Blocking I/O on hot paths (request handlers, tight loops).
- Missing pagination or streaming for potentially large datasets.
- Unbounded caches or structures that can grow without limit.
- Obviously missing indexes for new query patterns (if schema is visible).
- Redundant network or API calls that could be batched or cached.

## 4. Maintainability & Readability

- Naming that doesn't reflect intent.
- Functions/modules doing more than one thing, or grown too large to follow.
- Duplication that could reuse an existing abstraction.
- Magic numbers or strings without explanation.
- Dead or commented-out code left in the diff.
- Consistency with the rest of the codebase's existing style and idioms.
- Abstraction that fits the actual problem — neither premature nor missing.

## 5. Error Handling

- Errors are caught and surfaced meaningfully, never silently swallowed.
- User-facing error messages are separated from internal/log detail.
- Correct HTTP status codes / process exit codes for the failure mode.
- Timeouts and retries are present for external calls where it matters.

## 6. Test Coverage

- New logic paths have corresponding tests.
- Edge cases identified in §1 are actually exercised by tests.
- No existing tests were deleted or weakened without justification in the diff.
- Flaky-looking or newly-skipped tests are flagged, not ignored.

## 7. General Good Patterns (SOLID-ish)

- Single responsibility at the function/class/module level.
- Sane dependency direction — lower-level code doesn't depend on higher-level policy.
- Avoids tight coupling between otherwise-unrelated modules.
- Doesn't leak implementation details across layer boundaries.
- Reuses existing project patterns/utilities instead of introducing a second way
  to do the same thing.

## 8. Scope & Hygiene

- Changes match the PR/MR's stated purpose; no unrelated functional changes
  smuggled in.
- No unrelated formatting-only diffs mixed into functional changes (makes the
  real diff harder to review).
- No leftover debug logging, `console.log`/`print` statements, or
  commented-out code.
