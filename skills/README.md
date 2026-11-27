# A2A Adoption Skills

Two installable packages that teach an agent to speak A2A
(Agent2Agent) on the binding its platform can actually run. The
protocol is one — canonical Tasks, Messages, Parts, and Agent
Cards, with the same abstract operations — the **binding is a
per-counterparty capability choice**, declared in each agent's
Agent Card.

| Your agent | Skill | Binding | Why that binding |
| :--- | :--- | :--- | :--- |
| **Muse** | [`muse-a2a-email/`](muse-a2a-email/) (`SKILL.md`) | **EMAIL** v1.0 | Every Muse gets its own mailbox (`<your>@muse.ai`). A mailbox is an endpoint: addressable with no hosted server, store-and-forward like A2A's async task model, and identity-bearing through the mailbox address in its Agent Card. |
| **Gemini Spark** | [`gemini-spark-a2a-spreadsheet/`](gemini-spark-a2a-spreadsheet/) (`SKILL.md`-first; schedule prompt, doorbell script, and sheet template are reference files inside the skill folder) | **SPREADSHEET** v1.0 | Gemini Spark has no agent email address and cannot host an endpoint — but it has first-party Google Workspace access in unattended runs. A shared Google Sheet is its endpoint; a one-line `A2A-Event` email is only the doorbell. |

Specs: `email-binding/SPEC.md` and `spreadsheet-binding/SPEC.md`
in this repository. Reference codecs: `email-binding/reference/`
and `spreadsheet-binding/reference/`.

**Portable package:** the Gemini Spark folder is a complete,
self-contained package — zip
`gemini-spark-a2a-spreadsheet/` as-is and it uploads as one
skill package (`SKILL.md` plus its reference files: the
doorbell `Code.gs`, the layout-v2 `bridge-sheet.json`, the thin
schedule prompt, and `PACKAGE.md`, the manifest with the
install order). Nothing outside the folder is needed to stand
the lane up.

## Install summaries

### Muse (EMAIL)

Skills in this repository are Markdown-only, in the same form as
the Muse Gadget / Home Link device skills: paste a `SKILL.md`
into that Muse's chat, or share the repository link and let that
Muse find the skill it needs. Saving a skill sends nothing and
changes no settings.

Pairing is a separate human procedure, not part of the skill.
See `muse-a2a-email/SETUP-BY-HUMAN.md`: both humans agree on the
job, each does their own Muse Mail allowed-correspondent step
themselves, one supervised `GET_AGENT_CARD` exchange runs first,
and any standing reply arrangement is decided separately after
that.

### Gemini Spark (SPREADSHEET)

Upload `gemini-spark-a2a-spreadsheet/SKILL.md` via Gemini
**Settings > Skills**, or the Gemini Spark sidebar
**Skills -> Upload**; enable it. Saving the skill sends nothing
and changes no settings.

Setup is a separate human procedure, not part of the skill.
See `gemini-spark-a2a-spreadsheet/SETUP-BY-HUMAN.md`: the owner
creates the shared sheet and the processing schedule, adds one
counterparty with `bridge-sheet.json`, verifies with one
`test.ping`, and revokes the lane by deleting the schedule and
unsharing the sheet.

## Prompt libraries

Each skill ships a `PROMPTS.md` beside its SKILL.md: staged,
ready to paste prompts for sharing it (review only, save,
pairing, add a peer, operating prompts, revoke). Start there
when sharing a skill with another agent.

## Pairing Muse ↔ Gemini Spark

A Muse ↔ Gemini Spark pair needs **both** SKILL.md skills **and**
the shared sheet:

+ Gemini Spark runs the SPREADSHEET skill above — it is the
  responder on that lane, and its card declares the SPREADSHEET
  interface.
+ Muse takes the sender side of the same lane: enqueue =
  `SendMessage` (a Requests row, recorded in Muse's own store
  first), poll Results/Notes, commit matched rows, clear them.
  Muse's EMAIL skill does not substitute here — Gemini Spark
  cannot receive A2A by email; the only email in this pairing is
  the payload-free `A2A-Event` doorbell addressed to the account
  Gemini Spark watches.
+ The same two agents may *also* be reachable to each other or to
  others on other bindings (Muse is, by email and possibly HTTP).
  Each counterparty relationship uses the binding that
  counterparty's card declares and both sides support — one pair,
  one lane per conversation, no translation mid-task.
