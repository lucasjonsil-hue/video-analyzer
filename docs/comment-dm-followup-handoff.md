# Life 3000 — Video Analyzer: New Feature + Recommendations

*(Handoff from Lucas's Claude Chat planning conversation, pasted into Claude Code 2026-07-18.)*

## New Feature: Comment-to-DM Detection & Flagging

**Problem:** Some videos say things like "comment X to get the info" or "I'll DM you the link." The analyzer can't get that follow-up info automatically — it lives in a DM, not the video.

**Solution — semi-automated flag & feedback loop:**

1. **Detect:** During Vision analysis, add a check for comment-to-DM CTAs (phrases like "comment X for the link," "DM me," "comment done"). This can run off the transcript/captions or the frame text.
2. **Flag:** File these under a new category — `pending-dm-followup` — noting:
   - The keyword/phrase to comment
   - What's supposedly being offered (guide, link, discount, etc.)
   - Source video link
3. **Lucas acts:** Comment the keyword, wait for the DM, screenshot it.
4. **Feed it back:** Send the screenshot to Claude. It runs through the same Vision analysis pipeline and gets filed as a linked follow-up to the original video's note — so both pieces of info live together.

**Build steps:**
- Add CTA-detection prompt logic to the existing Vision analysis step
- Create the `pending-dm-followup` category/folder
- Add a "linked follow-up" field in the markdown template so DM screenshots attach to the original entry instead of becoming orphaned notes

---

## Other Recommendations (in priority order)

1. **Fix `GITHUB_TOKEN`** — blocks auto-filing entirely if it breaks; highest-leverage fix since everything downstream depends on it.
2. **Speech-to-text transcription** — biggest functionality gap. Most CTAs (including the comment-to-DM ones above) are spoken, not shown on-screen, so without this the new detection feature will miss a lot.
3. **Folder-watching for auto-upload** — removes the manual phone-upload step; pairs naturally with the hands-off save-to-analyze vision.
4. **Fact-check pass + flagged-creators list** — flag false/inaccurate claims into their own category, track repeat offenders.
5. **Inventory/browsing UI** — dropdown-style navigation across all categorized notes so everything is visible at a glance.
6. **Trip prep** — sync repo to GitHub, back up `.env` separately, clone repo on the MacBook before traveling.

---

## Status check against the codebase (Claude Code, 2026-07-18)

- (1) GITHUB_TOKEN: working — 103 notes auto-filed as of tonight. Non-issue currently.
- (2) Speech-to-text: DONE — local faster-whisper transcription has been in the pipeline for a while, and as of tonight the FULL transcript is saved in every note.
- (3) Folder-watching: not built. Related backlog idea: Claude Code hooks for auto-batch intake.
- (4) Fact-check + flagged creators: queued (see inventory-viewer-handoff.md). Creator capture added tonight as the prerequisite.
- (5) Inventory UI: mostly exists as the /notes page (category filter + search); polish queued.
- (6) Trip prep: repo synced both machines, MacBook has push auth (PAT expires 2026-08-10). TODO: back up .env somewhere safe off-repo.
- Comment-to-DM detection: NEW — queued for the next build session alongside the fact-check pass.
