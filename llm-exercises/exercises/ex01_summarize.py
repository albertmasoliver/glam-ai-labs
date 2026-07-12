"""
Exercise 1 — Summarize with a pipeline.

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 1
Reference: solutions/ex01_summarize.py
"""

from transformers import pipeline

SAMPLE = (
    "The city council approved a plan on Tuesday to convert the abandoned rail "
    "yard on the east side into a public park, ending nearly a decade of debate "
    "over the twelve-acre site. The first phase will clear the derelict tracks "
    "and add walking paths, a playground, and a small amphitheatre, with work "
    "expected to begin next spring. Supporters argued that the neighbourhood has "
    "the least green space in the city and that the park would raise nearby "
    "property values and give families a safe place to gather. A local business "
    "group had pushed instead for a mixed-use development of shops and flats, "
    "warning that the council was passing up badly needed housing and tax "
    "revenue. To address those concerns, the final plan reserves a strip along "
    "the northern edge for future affordable housing and sets aside space for a "
    "weekend market where local vendors can sell produce and crafts. Funding "
    "will come from a mix of municipal bonds and a state grant for brownfield "
    "redevelopment, though officials cautioned that the grant still depends on "
    "an environmental review of soil left contaminated by decades of industrial "
    "use. If that review clears, the council expects the first phase to open to "
    "the public within two years."
)


def solve(text):
    # Fill: the task name for summarization, and the output key.
    summarizer = pipeline(task=____, model="sshleifer/distilbart-cnn-12-6")
    out = summarizer(text, max_length=40)
    return out[0][____]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
