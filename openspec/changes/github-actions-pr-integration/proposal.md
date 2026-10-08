# GitHub Actions PR Integration

Add an opt-in RegScope job to the FastAPI template's GitHub Actions CI. On a
default-branch push, CI collects and caches a test-to-function baseline mapping.
On pull requests, CI reuses only the mapping for the exact base commit and runs
the selected tests. If no baseline is available, the RegScope job skips; the
template's existing full backend suite remains authoritative and unchanged.

This integration demonstrates RegScope as one CI signal, not as a replacement
for the complete test suite.
