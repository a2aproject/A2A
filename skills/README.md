# A2A Adoption Skills

Two installable packages that teach an agent to speak A2A
(Agent2Agent) on the binding its platform can actually run. The
protocol is one — canonical Tasks, Messages, Parts, and Agent
Cards, with the same abstract operations — the **binding is a
per-counterparty capability choice**, declared in each agent's
Agent Card.

| Your agent | Skill | Binding | Why that binding |
| :--- | :--- | :--- | :--- |
| **Muse** | [`muse-a2a-email/`](muse-a2a-email/) (`SKILL.md`) | **EMAIL** v1.0 | Every Muse gets its own mailbox (`<your>@muse.ai`). A mailbox is an endpoint: addressable with no hosted server, store-and-forward like A2A's async task model, and identity-bearing through permanent always-allow counterparties. |
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

1. Confirm your Muse Mail mailbox (`<your>@muse.ai`) sends and
   receives.
2. Install `muse-a2a-email/SKILL.md` as a skill in your Muse.
3. Publish your Agent Card with the EMAIL interface
   (`mailto:<your>@muse.ai`) — well-known URL if you have a site,
   and by answering `CARD` requests by email either way.
4. Set each counterparty to permanent "always allow" in Muse
   Mail (both sides), then run the `CARD` exchange from the skill
   and cache their card.
5. Send your first `SEND_MESSAGE` and watch for the terminal
   `TASK_UPDATE`.

### Gemini Spark (SPREADSHEET)

Gemini Spark consumes `SKILL.md` files like Muse does:
Gemini chats and Gemini Spark tasks share one skills library
in the open SKILL.md format. The Gemini Spark package is
therefore **SKILL.md-first** — the skill is the installable
artifact, and the schedule prompt, `Code.gs`, and
`bridge-sheet.json` are supporting reference files inside the
skill folder:

1. Upload `gemini-spark-a2a-spreadsheet/SKILL.md` via Gemini
   **Settings > Skills**, or the Gemini Spark sidebar
   **Skills → Upload**; enable it. (Skill names must be
   lowercase with hyphens.)
2. Follow the skill's one-time setup: create the shared sheet
   (Requests / Results / Notes / Card tabs + headers), share
   it with exactly the two agents' accounts, and install
   `Code.gs` as the sheet's bound Apps Script with an
   **On change** trigger (the doorbell).
3. In a **pinned** Gemini Spark session, create the
   email-triggered schedule from
   `gemini-spark-schedule-prompt.txt`
   (trigger: `subject:"A2A-Event"`). The prompt is thin: it
   only invokes `/gemini-spark-a2a-spreadsheet`; all
   processing rules live in the skill. Pause any hourly
   queue-check schedule.
4. Give the counterparty `bridge-sheet.json` (spreadsheet ID
   + tabs).
5. Verify with a `test.ping` row → a `TASK_STATE_COMPLETED`
   Results row linked to the ping's `message_id` (via
   `task_json.history`) with the `a2a.token` echoed in
   `metadata_json`.

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
