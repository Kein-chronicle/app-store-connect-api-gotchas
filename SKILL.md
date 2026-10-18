---
name: asc-submission-gotchas
description: Field-tested pitfalls when automating App Store Connect (ASC) - the review-submission API sequence, age-rating declarations (advertising flag auto-rejection, per-field types, live apps), screenshot upload that appends instead of replaces, review-attachment loss on new versions, export-compliance key, verifying ad-ID injection from the built archive, AdMob store linking, and passkey login for automation. Use when scripting ASC/iris API calls, preparing an app update submission, debugging an automated "age rating / advertising" rejection, or verifying what actually shipped inside an archive.
---

# asc-submission-gotchas

Knowledge pack, not a client library (use `fastlane`/the official API for plumbing). These are the
places where the happy path silently does the wrong thing. Status: **doc-only**, observed in real
submissions (2026-09). API shapes can change - treat 409 messages as the source of truth.
**Caution:** some steps below use undocumented web endpoints (the "iris" API) through your own logged-in session. Prefer the official, documented API where it covers the step, check Apple's terms before automating a session, and never commit session files.

## 1. Submitting a version (updates to a live app)

```
archive -> inspect built artifact (see 5) -> exportArchive -> upload build
-> POST /appStoreVersions {versionString}
-> PATCH /appStoreVersionLocalizations/<id> {whatsNew}      # required per locale on updates
-> set build on the version
-> PATCH /appStoreReviewDetails/<id> {notes, demoAccountRequired}
-> POST /appStoreReviewAttachments                          # RE-UPLOAD, see below
-> POST /reviewSubmissions -> POST /reviewSubmissionItems -> PATCH {submitted:true}
```
Submission is `reviewSubmissions` + `reviewSubmissionItems`. The legacy `appStoreVersionSubmissions` is 404.

Silent leaks:
- **A new version record does not inherit the review attachment (screen recording).** If your notes say
  "the recording shows ...", you are now promising a file that is not there - that is a Guideline 2.1 rejection.
- **`ITSAppUsesNonExemptEncryption` missing from the plist** leaves the build's `usesNonExemptEncryption`
  `null`. If you set the key, a later PATCH answering it returns 409 "already set" - that 409 suggests the key took.

## 2. Age rating

- Not reachable via `/apps/{id}`. Read with `GET /appInfos/{appInfoId}?include=ageRatingDeclaration`;
  write with `PATCH /ageRatingDeclarations/{appInfoId}` (declaration id == appInfo id).
- **Apps that ship ads MUST set `advertising: true`.** Apple's automated binary analysis sees the ad SDK
  and rejects *before* a human reviewer ("...did not select Yes for the Advertising content descriptor").
  Setting all 29 questions to "none" in bulk silently turns this off. The descriptor does not raise the
  computed rating (stays 4+). In the author's experience, fixing it while in review did not drop the app from the queue.
- Field types differ per field (about 13-15 strings like `"NONE"`, the rest booleans). Don't guess:
  send booleans, read the 409 `Expected a STRING`, flip only those fields. Converges in one loop.
- Don't send `developerAgeRatingInfoUrl` (a URI) as false/"NONE". Don't send `ageRatingOverride` and
  `ageRatingOverrideV2` together (409). `ageAssurance` is required, boolean.
- **Live (READY_FOR_SALE) apps:** the declaration is editable only while `appInfos` is editable
  (`409 STATE_ERROR ... not editable`). Fixing a wrong "no ads" declaration needs a new version.
- Do not bulk-flip to `true` without checking the binary actually contains ads: the opposite lie is also a lie.
- Re-submitting a rejected version is two steps: cancel the old submission (`{"canceled":true}`, wait for
  `COMPLETE`), then create a new `reviewSubmissions`. Same version keeps its attachments.

## 3. Screenshots

Upload **appends**, it does not replace. Re-uploading a fixed set produced duplicates.
Clear first. Locally, a flat `screenshots/` and a per-locale `screenshots/<locale>/` coexisting means
tools read the stale flat set - "my edits never change the pixels" => check file mtimes first.

## 4. Logging in for automation (passkeys)

> **Warning.** This section describes automating *your own* logged-in App Store Connect session and calling undocumented web endpoints. That may violate Apple's terms, and the saved session file is a full-account credential.
> Prefer the official App Store Connect API with an API key of the least role you need (keys can be revoked), use a dedicated limited account where you can, treat session files as secrets (never commit or share them), and expect sessions to expire.

Driving the "Sign in with passkey" button through CDP (`page.click`) leaves the button spinning forever;
the system dialog never appears. A **real OS-level mouse click** (e.g. `cliclick`) works, with no Touch ID
or 2FA prompt when the passkey is in the keychain and the Mac is unlocked. Re-measure the button
coordinates from a fresh screenshot each time (Retina captures are 2x logical). If Touch ID is asked,
stop and call a human - a click cannot answer it. Save `storageState` (chmod 600) and the iris API runs
from plain Python without a browser. That file is account-owner-grade credentials: never commit it.

## 5. Verify what shipped, from the archive

Verify ad IDs / keys in the **built artifact**, not the source:
`strings <App.app>/<binary> | grep ca-app-pub` and `plutil -extract GADApplicationIdentifier raw <App.app>/Info.plist`.
The same value may live in both Info.plist and `INFOPLIST_KEY_*` build settings. If the ad-unit string is
absent from the binary the ad is dead code (the linker dropped a never-instantiated class) - `strings`
measures *"is that ad alive"*, not just *"is the ID right"*.

## 6. AdMob specifics

- `~` in an ID = app ID, `/` = ad unit. If the "banner id" a user gives equals the app ID, ask - it will
  build and pass review and the banner will never fill.
- Linking an app to its store listing by numeric ID returns 0 results. Search by full URL
  `https://apps.apple.com/us/app/id<ID>`; very new apps may be missing from the US index - use `/kr/`.
- To compare all apps, unlock both filters: "show all apps" (hidden ones) and rows-per-page.
  AdMob has no delete; "hide" is reversible and does not affect serving.
