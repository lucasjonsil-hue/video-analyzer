# Handoff: Inventory Viewer + Fact-Check / Flagged Creators

## Step 0 — Do this first
Before building anything: check what Video Analyzer currently captures per video (creator name, source link, date, category, etc.). The features below assume creator name and source link are captured — confirm that's true, and if not, add it to the pipeline first.

## Feature 1: Inventory Viewer
**Goal:** Browsable index of all categorized video-analysis notes. Dropdown/accordion nav by category. Click an item → see full note (Claude's analysis + Lucas's own notes if added).

**UI**
- Category list as dropdowns (e.g. "AI ideas", "Workouts", "Money-making" — pull real category names from existing note folders)
- Expand category → list of note titles inside
- Click note title → renders note content in a panel (no page reload)
- Search/filter box (optional, nice-to-have)

**Implementation**
1. Scan the notes directory, build a JSON index: `{ category: [ {title, filepath, date, creator} ] }`
2. Simple local web viewer (single HTML page + small script) reading that index
3. Re-run the scan whenever new notes are added (or on page load) — no manual re-indexing
4. Read-only for now (view + browse only, no editing from this UI)

**Open questions to flag back to Lucas if unclear**
- Exact folder path for notes
- Whether categories are folder names or a tag inside each note's frontmatter

## Feature 2: Fact-check pass
- Go through video/link notes, evaluate claims for accuracy
- Any note containing false/inaccurate info gets moved (or tagged) into a separate "Flagged / False Info" category — keep original category as secondary tag so it's not lost
- Add a short flag note at the top of the note explaining what's false and why

## Feature 3: Flagged content creators
- Track creator/account name per video note (this is the field Step 0 needs to confirm)
- If a creator has multiple videos flagged as false, add them to a "Flagged Creators / Accounts" list/category
- Each entry: creator name, count of flagged videos, links to the flagged notes
- Purpose: surface repeat offenders, not just one-off bad videos

## Draft index-scanning script
`index.js` (included alongside this file) is a **first-pass draft only** — written without seeing the real notes format. Claude Code should treat it as a starting point to check against the actual pipeline output and rewrite/improve as needed, not as final code. Known gaps marked with `TODO` in the script itself (mainly: confirming the frontmatter field names for creator/source/flagged).
