# Partner PR Guide

This guide explains how to add your company to the A2A partners list in
[docs/partners.md](https://github.com/a2aproject/A2A/blob/main/docs/partners.md)
and how to get that pull request reviewed and merged.

## Who can join

The partners list is for companies that build a product or service on top of
A2A. The following do not qualify:

- Personal projects.
- New protocols or standards that are separate from A2A. Propose those as
  extensions in a GitHub issue instead.
- Landing pages that require a login before anyone can see the services.

## Steps

1. Fork [a2aproject/A2A](https://github.com/a2aproject/A2A) and create a branch.
2. Add one line to `docs/partners.md` in alphabetical order:

   ```markdown
   - [Your Company](https://your-company-site)
   ```

3. Check that every URL in your change opens without a login.
4. Open a pull request against `main` with the title:

   ```text
   docs: add <Company> to partners list
   ```

5. Fill in the partner section of the pull request template.
6. Reply to reviewer questions within 14 days. Pull requests with no activity
   for 14 days are marked stale and then closed.

## What to include in the pull request

- Company name and a one-sentence description of your A2A offering.
- A public proof of A2A usage: a blog post, press release, or docs page that
  mentions A2A. Examples: [#2033](https://github.com/a2aproject/A2A/pull/2033)
  and [#2136](https://github.com/a2aproject/A2A/pull/2136).
- Your agent card URL, if you have one. The card should be reachable at
  `/.well-known/agent-card.json` and should advertise A2A 1.0. You can keep
  0.3 as a secondary interface if existing clients still need it.
- The `a2a` CLI command you used to test the card, for example
  `a2a card get -a <url>`, and the CLI version.
- The `no-issue` label if the pull request is not linked to an issue.

## Checklist for the contributor

- [ ] My company builds a product or service on A2A.
- [ ] My landing page is public and explains my A2A services.
- [ ] I have a public proof of A2A usage (blog, press release, or docs).
- [ ] My agent card resolves and, if provided, advertises A2A 1.0.
- [ ] I added one line to `docs/partners.md`, in alphabetical order.
- [ ] Every link in the change returns an accepted status (200, 301, 302,
      307, 308, 403, 429, or 503). The `Check PR links` job runs lychee on
      `docs/partners.md`.
- [ ] The pull request title is `docs: add <Company> to partners list`.
- [ ] I searched open pull requests for my company and found no duplicate.

## Checklist for the reviewer

- [ ] Title follows the `docs:` conventional commit format.
- [ ] The `no-issue` label is set or the pull request links an issue.
- [ ] The diff is one line in `docs/partners.md`, alphabetical, in the existing
      format.
- [ ] The company builds a product or service on A2A. It is not a personal
      project or a separate protocol.
- [ ] The landing page is public, and the company's A2A offering is clear.
- [ ] A public proof of A2A usage exists.
- [ ] The agent card resolves, and if provided, advertises A2A 1.0.
- [ ] The `Check PR links` job passes.
- [ ] No other open pull request adds the same company.
- [ ] If questions remain, set `status:awaiting response` and post all
      questions in one comment.
- [ ] Approve and merge, then reply to the contributor.

## Common reasons pull requests stall or close

| Reason | Example |
| --- | --- |
| The link goes to a login screen, not a public page | [#2313](https://github.com/a2aproject/A2A/pull/2313) |
| The company is a personal project | [#2313](https://github.com/a2aproject/A2A/pull/2313) |
| The project is a protocol, not a product on A2A | [#2053](https://github.com/a2aproject/A2A/pull/2053) |
| No public proof of A2A usage was provided at first | [#2136](https://github.com/a2aproject/A2A/pull/2136) |
| The agent card only advertised 0.3 | [#2294](https://github.com/a2aproject/A2A/pull/2294) |
| A link returned a status the link checker rejects | [#2114](https://github.com/a2aproject/A2A/pull/2114) |
| A duplicate pull request was open | [#2016](https://github.com/a2aproject/A2A/pull/2016) was replaced by [#2039](https://github.com/a2aproject/A2A/pull/2039) |
| No reply for 14 days | [#2343](https://github.com/a2aproject/A2A/pull/2343) was marked stale |
