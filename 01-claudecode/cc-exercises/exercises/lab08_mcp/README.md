# Lab 08 — what a capability costs

A whole MCP server, in one file, with no dependencies and nothing to leak:
`mcp_server.py` speaks JSON-RPC over stdin and stdout and answers questions about
a local SQLite shelf of books. Half an hour, most of it in the two session resets the comparison needs, and you will connect it, use it,
and then find out what it charged you.

```bash
python3 seed.py                 # writes library.db
python3 library_cli.py shelves  # the same capability, as a command
```

The server is small on purpose. Writing one is not the hard part and not the
lesson. **The lesson is the bill**, and you cannot see the bill until you connect it.

## What to do

**1. Connect it, and confirm it is really there.** Add it as a local stdio server,
then check from inside Claude Code:

```bash
claude mcp add --transport stdio library -- python3 "$PWD/mcp_server.py"
```

Inside the session, `/mcp` should list `library` as connected. If it does not, run
the server by hand and paste it a line of JSON — it answers on stdout, and a server
that answers by hand and not to Claude Code is a configuration problem, not a code one.

**2. Read the bill before you use it.** `/context all` breaks the window down per
MCP tool. Write the number into `MCP.md`. Two tools with short descriptions is the
cheapest possible server, so whatever you see here is close to the floor.

**3. Use it for something it is actually good at.** Ask which books N. K. Jemisin
has on these shelves, and then for the totals per shelf. Both answers have to come
through the tool, not from the model's own knowledge of her bibliography — that is
the difference between a server that works and a server that appears to.

**4. Now do it the other way.** `claude mcp remove library`, then `/clear`. Write a
skill in `.claude/skills/` that wraps `library_cli.py`, which already does the same
two things. The description is the whole interface: write it the way you would say
the question out loud. Ask the same two questions, then read `/context all` again.

**5. Answer the question the module asks.** You now have two numbers for the same
capability. Write down which one you would ship, and why — and if the answer is
"the server", say what it buys that is worth the difference.

> Chapter 7 of Kousen's *Claude Code: Up and Running* covers MCP setup and the
> ecosystem; his text and examples are not reproduced here. This server, the CLI,
> and the measurement are the lab's.

## The trade the module is about

MCP is the right answer when Claude needs structured access to something outside
itself that it cannot otherwise reach: another team's system, a live database, an
API with a schema. It is the wrong answer when a local command would have done,
because every tool definition is resident in the window for the whole session —
you pay for the vocabulary on every turn, whether you use it or not.

That cost is small here, and it is not zero. Multiply it by the number of servers
people connect once and never remove.

## Done when

`python check.py lab08` passes: the server still completes a handshake and answers a
`tools/call`, `.claude/skills/` holds a skill whose frontmatter parses and whose
description names when to use it, and `MCP.md` carries both context readings and a
verdict with a reason.

## One honest caveat

`/context all` moves between versions and between models, and the absolute numbers
mean little on their own. The ratio between your two readings is the finding, and
the ratio is stable.
