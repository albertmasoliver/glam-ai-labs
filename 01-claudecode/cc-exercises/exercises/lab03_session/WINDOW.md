# What the window actually cost

## The measurement

| | Tokens |
|---|---|
| baseline, before asking anything | <from /context> |
| estimate for sample/, from window.py | <from window.py> |
| after reading all three files | <from /context> |
| **cost** (after - baseline) | <subtract> |

**Estimate error:** <|estimate - cost| / cost, as a percentage>

**Which file dominated, and by how much:** <one line>

## The failure mode with no error message

**What I asked after polluting the session:** <the precise question>

**Was the answer worse:** <yes / no, and what changed about it>

**Space still free at that point:** <from /context>

**Full is not the same as polluted, because:** <one sentence. If this sentence
would still be true with the word "polluted" swapped for "full", write it again.>
