# Your prompt

```text
tests/test_web.py::test_create_rejects_empty_title fails: create_note()
accepts a title of "" and returns 200 instead of 400.

A note must have a title with something in it. A missing, empty or
whitespace-only title is rejected with a 400 and an error message.

The handlers are in notes/web.py.

This app already has a validator pattern in notes/validation.py:
a validator returns None when the value is fine and a short error string
when it is not, and the handler turns that string into a 400. Follow it,
so that every path accepting user input is checked the same way rather
than each handler inventing its own rule.

Don't touch notes/formatting.py, notes/legacy_export.py, or the tests.
```

---

## After the run

**Which clause do you think did the most work?**

`so that every path accepting user input is checked the same way`. That is the whole
lab. Without it the prompt names one handler and one field, and the fix lands in
`create_note` alone — `update_note` keeps taking a blank title, because nothing in the
request said it should not.

With it, the request is no longer about a test. It is about a rule, and a rule has to
apply everywhere the rule applies. The reference fix pulls the check into a `_check`
helper and runs it from both handlers, which is not a structure anyone asked for — it
is what following the stated reason produces.

Note what the other four jobs did and did not do. The symptom, the desired behaviour,
the location and the convention pointer all made the fix *correct and cheap*: no
discovery round, no invented error format, no guessing about whitespace. None of them
made it *transfer*. Five jobs get you a good fix in one shot. The reason is what gets
you the second one you never mentioned.

**What did it change that you did not name?**

`update_note`, which appears nowhere in the prompt and in no test the run could see.
That is the result, and it is the reason this lab exists.
