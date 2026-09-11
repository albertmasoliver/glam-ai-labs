---
paths:
  - "tests/**/*.py"
---

# Testing rules

- Tests must not touch the filesystem, stdout, or a real clock.
- Pass a fake storage object; never construct a `JsonFileStorage` in a unit test.
- One behaviour per test, named for the behaviour rather than the function.
