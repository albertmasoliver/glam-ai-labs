# The slice

**One sentence:** <what this pull request does. If it needs "and", it is two slices.>

**Left in the backlog:** <the bullets from #39 you are not doing, by name>

## Postconditions

What must be true after, each with the test that proves it.

- <an observable behaviour>
  `tests/test_<file>.py::<test name>`

## Preconditions

What must already be true for this to make sense. Prose; nothing to run.

- <a precondition>

## Invariants

What must not change. These are the existing tests you are promising to keep green.

- <something that must still hold>
  `tests/test_cart.py::<an existing test>`

## Negative criteria

What must explicitly not happen. Prose.

- <something you are deliberately not doing>
