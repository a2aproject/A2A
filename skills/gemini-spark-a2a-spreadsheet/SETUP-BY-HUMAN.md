# Setting Up a Spreadsheet A2A Lane - a Human Procedure

This file is for the humans who own the two agents, not for
either agent. No agent is asked to create a schedule, install a
script, or share a document on sight. Each step is done, or
explicitly approved, by the human who owns that side.

## Step 1 - Agree on the job

Name one concrete reason the two agents will exchange requests
over the sheet. If there is no job, there is nothing to set up.

## Step 2 - Each human gives their own agent the skill

Paste the SKILL.md in this folder into that agent's chat, or
share the repository link and ask the agent to save the skill
for later use. Saving a skill sends nothing and changes nothing.

## Step 3 - The owner creates the shared spreadsheet

The spreadsheet owner creates the sheet with the Requests,
Results, Notes, and Card tabs from the spec, installs Code.gs
as the sheet's bound Apps Script with an On change trigger,
and shares the sheet with exactly the two agents' accounts.

## Step 4 - The owner creates the processing schedule

In a pinned session, the owner creates the email-triggered
schedule from gemini-spark-schedule-prompt.txt. The prompt is
thin by design: it only invokes the skill. Pausing or deleting
this schedule stops all unattended processing.

## Step 5 - Add one counterparty

Give the counterparty the filled bridge-sheet.json (spreadsheet
ID and tabs). That is the add-a-counterparty step, separate
from adopting the protocol, in the same way adding a peer by
direct configuration works in upstream A2A discovery.

## Step 6 - Verify together, then decide the standing rules

Run one test.ping and confirm the linked Results row together.
Only then decide, explicitly, which request kinds may run
unattended. Read and query kinds are the default. Any standing
arrangement can be withdrawn at any time.

## Revoking the lane

Delete the processing schedule and its trigger, and unshare
the spreadsheet. That is the whole revocation, and either
human can do their side of it at any time.
