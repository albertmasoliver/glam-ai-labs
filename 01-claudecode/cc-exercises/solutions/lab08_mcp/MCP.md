# One capability, two ways to reach it

A reference answer. The absolute numbers move between versions; the ratio is the
finding.

## As an MCP server

**Context cost, from /context all:** 740

**What I asked, and what came back:** "Which books by N. K. Jemisin are on these
shelves?" It came back with the three Broken Earth novels and their years, and
`/context all` attributed the call to `library`. The proof it went through the tool
is that it listed exactly three and stopped -- the model's own knowledge of her
bibliography would have offered *The Hundred Thousand Kingdoms* too, and that book
is not in the database.

## As a CLI wrapped in a skill

**Skill file:** `.claude/skills/library/SKILL.md`

**Context cost, from /context all:** 95

**Did it fire without being named:** yes, on "what have we got by Le Guin" -- the
description carries the phrasings people actually use, which is the only reason it
matched.

## The verdict

**Ratio between the two:** 7.8

**I would ship:** the skill

**Because:** the two capabilities are a SQLite read on the same machine, and the
skill reaches them for an eighth of the resident cost. The server's tool schemas sit
in the window for the whole session whether anyone asks about books or not, and most
sessions never will. Nothing here needs a protocol: there is no other team's system
on the far end, no auth to manage, no schema that changes under me.

**When I would switch to the other one:** when the shelf data stops being a local
file -- if it moves behind a service another team owns, or if a second client that
is not Claude Code needs the same two operations, the protocol starts paying for
itself and the CLI becomes the thing I have to keep in sync twice.
