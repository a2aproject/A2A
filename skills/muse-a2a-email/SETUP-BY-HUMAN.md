# Setting Up an A2A Peer — a Human Procedure

This file is for the two humans, not for either agent. It is the
pairing step, in the same way pairing a Muse Home Link is done by
the user in Settings, not by Muse. No agent is asked to change
its own mail settings, install anything on sight, or start a
watch. Each step below is done, or explicitly approved, by the
human who owns that agent.

Keep the shared skill Markdown-only. There is no code to run, no
token to share, and no credential involved at any step.

## Step 1 — Both humans agree on the job

Name one concrete reason the two agents should talk, for example
coordinating schedules between two households. If there is no
job, there is nothing to set up yet.

## Step 2 — Each human gives their own Muse the skill

Either of these, done by that Muse's own user in that Muse's chat:

- Paste the `SKILL.md` in this folder into the chat, or
- Share a link to this repository and ask their Muse to read the
  `muse-a2a-email` skill and save it for later use.

Saving a skill is a local, reversible text file. It takes effect
only when that user later asks their Muse to contact a peer, or
when mail from an established peer arrives. Testing a saved skill
never sends mail on its own.

Each Muse may also keep a separate local note with its own
mailbox, its established peers, and house rules. That local note
is not part of the shared skill and is never shared upstream,
in the same way a Home Link device skill keeps house details in
a separate local footer.

## Step 3 — Nothing to pre-configure in Muse Mail

There is no correspondent list to add anyone to in advance.
Muse Mail recipient permissions are created at send time: when
a user approves their agent's **first email to a recipient**,
the approval card offers an "always allow" choice for that
recipient. Choosing it creates a standing **Recipient
permission** for that address ("Send emails without including
you"), listed in Muse Mail settings under **Manage recipient
permissions**.

- Your agent: <your>@<mail domain>
- The peer agent: <peer>@<mail domain>

Which peer that is gets named later, in the separate add-a-peer
step (see `examples/add-a-peer.md`). No address belongs in the
universal setup itself.

Granting and revoking are things only the user can do, never
the agent: the grant happens on the user's own approval card,
and either human can undo it at any time by revoking that
recipient's entry in Muse Mail settings, which ends the lane.

## Step 4 — One supervised first exchange

The user who wants to start asks their Muse, in plain words:

> Contact <peer mailbox, from your add-a-peer step> and ask for their Agent Card.

That single request is the approval for that single send, and
it is also the moment the recipient permission is created: on
that first send's approval card, each user can choose "always
allow" for the peer's mailbox, so later sends to it no longer
need the user included each time. The reply CARD is cached,
shown to the user, and the two humans confirm to each other,
out of band, that the mailboxes match what they expected.

## Step 5 — Decide the standing arrangement, separately

Only after a first exchange works do the two humans decide,
explicitly, whether their agents may reply to each other within
a task without asking each time, and for what kinds of tasks.
That decision belongs to each user for their own agent, can be
different on each side, and can be withdrawn at any time.

No standing arrangement is implied by steps 1 to 4.
