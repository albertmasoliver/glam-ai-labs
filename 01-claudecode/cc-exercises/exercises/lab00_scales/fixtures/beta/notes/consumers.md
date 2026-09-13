# Who depends on this

| Service | What it does with a slug | Owner |
|---|---|---|
| content-api | Builds permalinks. Old slugs must keep resolving. | platform |
| search-index | Uses the slug as a document id. | discovery |

A change to slug output is a data migration in two services, not a patch here.
