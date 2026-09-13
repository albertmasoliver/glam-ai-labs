# Order review step with an itemised breakdown

Closes part of #39.

## What this is

An itemised review of the cart, shown before payment: one row per line, with
shipping and the total as separate figures. It reads prices from `orders.cart`
and calculates nothing of its own.

## Boundary

**In scope:** the review page's data -- rows, subtotal, shipping, total.

**Out of scope:** progress indicator, save cart for later, discount codes, email
confirmation, analytics, multiple payment methods, mobile responsive design. All
of them are still in #39.

## Verification

```
  proven   The review shows one row per cart line, in cart order.
  proven   The rows the buyer reads add up to the subtotal the buyer reads.
  proven   Shipping appears as its own figure and the total is the sum of the two.
  proven   Reviewing an empty cart is refused rather than shown as a zero order.
  proven   Rounding stays at the line, so finance keeps reconciling against the pr...
  proven   The subtotal remains the sum of the printed lines and not a separate ca...
  proven   The free-shipping threshold is untouched.

  7 contract lines, all proven. The gate is green.
```

## The plan I had to correct

**What it proposed:** recomputing the subtotal inside `review()` by summing
`unit_price * quantity`, "to avoid the extra call".

**Which contract line it broke:** the invariant that rounding stays at the line.
Summing the raw products and rounding once at the end differs from the sum of the
rounded rows by a cent on carts like this one, and the rows are what finance
reconciles against.

**What I asked for instead:** read every figure from `orders.cart` and let the
review own no arithmetic at all -- which is now a negative criterion, so the next
session cannot reintroduce it by being helpful.

## Headless, with and without --bare

**Command:** `claude -p "$(cat prompts/pr-readiness.md)" --output-format json --bare`

**Difference:** I deleted `.claude/runs.log`, ran the gate prompt headless, and the log
came back with a line in it. The `Stop` hook in this folder had run, and nothing asked me
whether it should.

With `--bare` on the same prompt the log stayed absent. There are no MCP servers
configured here, so that half of the claim is untested and I am not going to assert it
from a diagram — the hook is the part I could observe, and the hook ran. On a project
with a `.mcp.json` the servers go the same way, and that is the part worth fearing.
