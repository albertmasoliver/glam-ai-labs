# Routing: one skill, three descriptions

A reference answer. The wording of the question matters more than anything else
here, so it is quoted exactly as it was typed.

**The question I asked:** Is the trainer package well enough tested to open a pull
request?

**1. Invoked by name:** fired

**2. Description replaced with `helps with code`:** did not fire — the answer came
back as a normal reply that read three test files and guessed, with no skill
mentioned and no coverage run anywhere in it.

**3. Description rewritten in the words someone would say out loud:** fired, on the
same sentence, in the same session shape as state 2.

**The rewritten description, in full:** Report which lines and branches of this
project the test suite never executes, ranked by risk. Use when the user asks what
is untested, where the coverage holes are, whether a change is covered, or whether
the suite is good enough to open a pull request.

**What the generic one was missing:** the question never says "coverage" — it says
"well enough tested" and "open a pull request", and the rewrite carries both of
those phrasings verbatim. `helps with code` matches every question equally, which
is the same as matching none of them; there is nothing in it for the sentence to
be closer to than to the plain answer.
