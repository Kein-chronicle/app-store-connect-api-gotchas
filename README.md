# app-store-connect-api-gotchas

**Field-tested App Store Connect automation pitfalls: review-submission sequence, age-rating advertising flag, screenshot append bug, attachments lost on new versions.**

[![test](https://github.com/Kein-chronicle/app-store-connect-api-gotchas/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/app-store-connect-api-gotchas/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg)

## Why

The happy path of the review-submission API silently does the wrong thing in several places: a new version does not inherit the review attachment, ad apps need `advertising: true` or are rejected before a human looks, and a screenshot upload appends instead of replacing.

> **Status: doc-only.** A knowledge pack, not a client: use fastlane or the official API for plumbing. Observed in 2026-09; API shapes change, so treat 409 messages as the source of truth. Parts rely on undocumented web endpoints and on automating your own logged-in session. Prefer the documented API, check Apple's terms, and never commit session files.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/app-store-connect-api-gotchas.git ~/.claude/skills/asc-submission-gotchas
```

For a single project, clone into `<project>/.claude/skills/asc-submission-gotchas` instead, then start a new Claude Code session.

**Just read it:** the whole skill is [SKILL.md](SKILL.md). It is plain Markdown; copy any part into your own `CLAUDE.md` or prompts.

**Requires:** nothing to read it; Python 3.10+ only to run `validate.py`.

## What it covers

- Submitting an update to a live app, in order, with the silent leaks.
- Age rating: field types, the advertising descriptor, live-app limits.
- Screenshots, logging in for automation, verifying ad IDs from the built archive, AdMob specifics.

## Limits

- A knowledge pack, not a client: use fastlane or the official API for plumbing. Observed in 2026-09; API shapes change, so treat 409 messages as the source of truth.
- Parts rely on undocumented web endpoints and on automating your own logged-in session. Prefer the documented API, check Apple's terms, and never commit session files.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **fastlane**: release automation for iOS
- **App Store Connect API (official)**: the documented API

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**safe-delete-sole-copy-check**](https://github.com/Kein-chronicle/safe-delete-sole-copy-check): Before you delete a project folder: is any of it the only copy? Checks the live remote, unpushed commits and tags, untracked and ignored files, and verifies copies by hash.
- [**exif-orientation-guard**](https://github.com/Kein-chronicle/exif-orientation-guard): Find and fix images whose stored size differs from their displayed size because of an EXIF orientation tag.
- [**macos-tcc-automation-permissions**](https://github.com/Kein-chronicle/macos-tcc-automation-permissions): Make unattended macOS automation survive permission resets: AppleScript -1743/-1728, launchd jobs, screen recording, and real vs synthetic clicks.

## Development

```sh
python3 validate.py
```

This only validates the skill file (frontmatter and referenced paths). See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: app-store-connect, ios, app-store, api, automation, admob, release, claude-skills</sub>
