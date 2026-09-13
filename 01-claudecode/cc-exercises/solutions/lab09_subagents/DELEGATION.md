# What delegating did to the main window

A reference answer. The numbers are from one real run against
`../lab12_landing/invoicing`; yours will differ and the arithmetic still has to
agree.

## The measurement

| | Tokens |
|---|---|
| round A, before the survey | 14,800 |
| round A, after the survey | 31,200 |
| round B, before delegating | 14,900 |
| round B, after the report came back | 17,100 |
| **saving** (round A cost - round B cost) | 14,200 |

**What I surveyed:** `../lab12_landing/invoicing`, eight modules and two test
files -- where is the test coverage missing, and which gap would I close first?

**What delegating did not save:** the subagent read all eight modules and both
test files exactly as the main session had, so the same tokens were spent and
billed; what changed is that they were spent in a context I threw away, and only
the 2,200-token report survived into mine -- the saving is in my window, not on
the invoice.

## What the two rounds felt like

Round A left the main session holding eight files it no longer needed, and the
next question I asked it went through all of them again. Round B left it holding
nine bullet points, which is the whole of what it kept.

The report was also worse. It named a file I had to go and check, and one of its
three findings did not survive the check -- see `TRIAGE.md`. That is the third
cost, and it is the one that does not shrink when you delegate.
