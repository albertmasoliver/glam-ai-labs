# What the window actually cost

A reference answer. The numbers are from one real run; yours will differ and the
arithmetic still has to agree.

## The measurement

| | Tokens |
|---|---|
| baseline, before asking anything | 14,200 |
| estimate for sample/, from window.py | 5,670 |
| after reading all three files | 21,800 |
| **cost** (after - baseline) | 7,600 |

**Estimate error:** 25 %

**Which file dominated, and by how much:** `confusables.py` at 5,400 of the 5,670
estimated tokens -- twenty times the other two together, and it is a generated table
nobody will ever ask a question about.

## The failure mode with no error message

**What I asked after polluting the session:** what `union_area` returns for two
rectangles that do not overlap.

**Was the answer worse:** yes. The first time it answered with the sum of the two
areas and named the `intersect` short-circuit that makes it so. After the three
unrelated questions it answered correctly but hedged, offered to re-read the file,
and stopped referring to `intersect` by name -- the reasoning got vaguer while the
fact stayed right.

**Space still free at that point:** 168,000

**Full is not the same as polluted, because:** a full window has run out of room and
says so, while a polluted one has plenty of room left and simply spends most of its
budget re-sending things that are not about the question -- which is why the only
symptom is that the answers quietly get worse.
