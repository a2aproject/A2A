# Portable package — Gemini Spark A2A (SPREADSHEET binding)

This folder **is** the whole portable package. Zip it as-is
and it uploads as one skill package: `SKILL.md` is the
adoption unit Gemini Spark consumes, and every other file is
a supporting reference the skill points at. Nothing outside
this folder is required to stand the lane up — the full
binding specification lives in the A2A fork at
`spreadsheet-binding/SPEC.md` for implementers, but adopting
agents need only this package.

## Files

| File | What it is |
| :--- | :--- |
| `SKILL.md` | The skill itself: setup, sheet contract (layout v2), the Apps Script build, processing rules, operations, standing rules, compliance checklist. Upload this to Gemini Spark. |
| `PACKAGE.md` | This manifest: file roles and install order. |
| `Code.gs` | The sheet's bound Apps Script doorbell. Pasted into the sheet's Apps Script project during setup; sends the fixed-subject `A2A-Event` wake email on Requests appends, with a 15-second debounce. Write-free; carries no payload. |
| `bridge-sheet.json` | The endpoint config template: spreadsheet ID placeholder, tab names, and the layout v2 column headers for all four tabs, plus `"layout_version": 2`. The counterparty fills in its copy with the real spreadsheet ID. |
| `gemini-spark-schedule-prompt.txt` | The thin processing-schedule prompt. On an incoming `A2A-Event` email it invokes the skill (by name) and nothing more — all processing rules live in `SKILL.md`. If the skill is unavailable, the prompt says to stop rather than improvise. |

## Install order

1. **Upload `SKILL.md` to Gemini Spark** — Settings > Skills
   → upload (or the Gemini Spark sidebar Skills → Upload);
   the skills library is shared between Gemini chats and
   Gemini Spark tasks. Enable the skill.
2. **Create the sheet from `bridge-sheet.json`** — four tabs
   (`Requests`, `Results`, `Notes`, `Card`) with the layout
   v2 headers in the template, row 1 frozen; publish your
   Agent Card in the Card tab (declaring `"sheetLayout": "2"`
   in its SPREADSHEET extension params); share with exactly
   the two agents' operating accounts. (SKILL.md §2.1.)
3. **Build the Apps Script per SKILL.md §2.2** — paste
   `Code.gs` into the sheet's bound script project, set the
   `<YOUR_EMAIL>` doorbell recipient, save, add exactly one
   trigger (`onBridgeChange`, From spreadsheet, On change),
   authorize.
4. **Save `gemini-spark-schedule-prompt.txt` as the
   email-triggered schedule** — in a pinned Gemini Spark
   session, trigger = incoming email matching
   `subject:"A2A-Event"`, state Active; pause any legacy
   hourly queue-check schedule. (SKILL.md §2.4.)
5. **`test.ping` verify** — append a `test.ping` Requests
   row; confirm the `A2A-Event` email arrives, the schedule
   runs immediately, and a Results row comes back linked to
   the ping's `message_id` with the `a2a.token` echoed and
   `status` = `TASK_STATE_COMPLETED`. (SKILL.md §2.5.)

## Notes

- **Placeholders only.** The package ships with
  `<SPREADSHEET_ID>`, `<YOUR_EMAIL>`, and
  `<COUNTERPARTY_EMAIL>` placeholders — fill them in your own
  copies; never commit a filled-in copy back to a public
  package.
- **One sheet, one ordered agent pair.** A deployment sheet
  serves exactly one requester↔responder pair; stand up a
  second pair with a second sheet and a second copy of this
  package.
- **Layout versioning.** The package teaches sheet layout
  **v2** (canonical A2A column names + `metadata_json`).
  Readers also accept legacy layout v1 rows; writers never
  emit them (SPEC Appendix B has the mapping).

- `PROMPTS.md` - staged, ready to paste sharing prompts (review only, save, verify, add a counterparty, operating prompts, revoke).
