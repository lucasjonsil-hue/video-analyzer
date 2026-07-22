# AI Founder Playbook — Lucas / Life Hacker 3000

> Drop this file in `F:\Life3000\` (e.g. as `PLAYBOOK.md`, linked from `CLAUDE.md`) so Claude Code always has the full operating context. Update it as you learn — this is a living doc, not a one-time brainstorm.

---

## 1. Mission

Solo founder, $0 revenue, building toward an AI Personal Operating System ("Life Hacker 3000"). Revenue comes first — it funds and validates the long-term ecosystem. Every module should either (a) make money on its own, or (b) directly feed the Life 3000 core.

**Operating rules:**
- Optimize for paying customers, not polish.
- Ship in days, not weeks.
- Claude Code writes 80%+ of the code. You direct, test, and sell.
- Every idea gets challenged before it gets built.
- Kill ideas fast; don't fall in love with them.

---

## 2. Why the Original Framework Needed Work

The original doc had good bones but three structural problems, fixed below:

1. **No sequencing.** Four prompts were listed but nothing said *when* to run which, or what triggers moving to the next stage. → Fixed with the **Stage Gate Workflow** (Section 3).
2. **No scoring math.** "Rank by revenue potential, difficulty, AI leverage..." with no actual formula means everything ends up "medium." → Fixed with a **numeric scoring rubric** (Section 4).
3. **Re-interviews from zero every time.** Prompt 2 has Claude interview you from scratch, which wastes days re-discovering things you've already told Claude. → Fixed with a **living Profile Snapshot** (Section 5) Claude Code should read first, and only ask *delta* questions.

---

## 3. Stage Gate Workflow (run in this order, every cycle)

```
STAGE 0 — Context Load        Claude Code reads Section 5 (Profile Snapshot) + current revenue status
STAGE 1 — Signal Capture       Daily Opportunity Engine (Section 6) — 5 min/day, log don't analyze
STAGE 2 — Weekly Idea Sprint    Friday: turn the week's signals into 5-10 scored ideas (Section 4)
STAGE 3 — Gate Check           Idea must answer "who pays" and "smallest MVP" before any code is written
STAGE 4 — Build                Claude Code builds MVP in ≤1 week; you handle anything Claude Code can't (accounts, payments, posting)
STAGE 5 — Sell                 Get ONE real paying customer or real click-through before building more
STAGE 6 — Review               Weekly CEO Meeting (Section 7) — keep, kill, or double down
```

**Gate rule:** nothing moves from Stage 3 to Stage 4 without a one-line answer to "who pays and why." No exceptions — this is what kills scope creep.

---

## 4. Idea Scoring Rubric (use this instead of vague ranking)

Score each idea 1–5 on each axis. Total out of 30. Anything under 18 gets discarded, not "kept for later."

| Axis | 1 | 3 | 5 |
|---|---|---|---|
| Revenue speed | months to first $ | weeks | days |
| Claude Code leverage | mostly manual | Claude Code does half | Claude Code does ~80%+ |
| Uses an asset you already have | none | some overlap | direct reuse of Video Analyzer / spearfishing niche / clipping skillset |
| Competition | saturated, no wedge | crowded but a wedge exists | clear underserved niche |
| Your motivation | you'd resent building it | neutral | you'd do it even unpaid |
| Path to $10k/mo | no visible path | plausible with pivots | clear scaling path |

---

## 5. Profile Snapshot (Claude Code: read this before asking anything)

*This replaces re-running "Interview Me" from scratch. Only ask questions that fill genuine gaps below.*

- Solo developer, based in Orange, CA — business undergrad at Chapman University. Fall 2026 term starts **Aug 24**, which is a real constraint on available hours from that date. Works across claude.ai and Claude Code (desktop app, not CLI) on a Windows PC — project at `F:\Life3000`.
- **Existing built asset #1:** Video Analyzer pipeline — pulls video URLs/uploads, extracts frames (OpenCV), transcribes audio locally via `faster-whisper` (no API cost), sends both to Claude Vision, auto-files structured notes to GitHub. Working end-to-end since 2026-07-09; `GITHUB_TOKEN` is configured and notes commit reliably. Remaining gap: no folder-watching automation (email-agent intake + `video_backlog.txt` queue covers most of it).
- **Existing built asset #2 (§9 step 1 — DONE 2026-07-20):** Clip-and-caption pipeline — **spun out of Life3000 on 2026-07-21 into its own project, `F:\Clipfarm` (repo `clipfarm`)**. `py pipeline.py <url>` → yt-dlp ingest, local Whisper word-level transcript, one Claude call picks 5 viral moments, ffmpeg cuts vertical 1080x1920 and burns bold word-timed captions. Tested end-to-end: 5 usable clips in ~85s. Only paid step is a single Sonnet call (~cents/video). **This is built — the open problem is distribution and getting paid for it, not code.** Clipfarm is a revenue project with its own deps and credentials; Life3000 stays personal tooling. The video analyzer routes anything it learns about clipping into `F:\Clipfarm\notes\clipping.md`.
- Other built modules (see `CLAUDE.md` for detail): gym notepad + progress table, local calendar, planner with wave alerts, portfolio tracker, scheduled email agent.
- **Stated #1 revenue priority: clipping/UGC** — cutting clips (including AI-assisted) from longer videos and posting via clipping programs to earn per-view revenue.
- **Faceless-first (decided 2026-07-21).** Lucas is not putting his face on camera for now. This is a *decided* constraint, not an open question — do not re-litigate it or quietly propose plans that assume on-camera work.
  - Clipping needs no face at all (it's someone else's footage) — this is the primary path and it is unaffected.
  - Faceless UGC formats that still pay: voiceover + product b-roll, hands-only demos/unboxing, screen recordings for app/software brands. Fewer listings and lower rates than on-camera UGC, but real.
  - On-camera brand UGC ($50–150/video on JoinBrands/Billo) is deliberately **deferred**, not rejected. Revisit only if Lucas raises it.
- **Real-world niche knowledge:** intermediate freediver/spearfisherman on the California coast (targets: sheephead, calico bass, yellowtail, abalone), has already built a detailed ranked dive-spot decision framework (visibility, swell, wind, temp, kelp, tide) — this is genuine expert content most creators don't have.
- Other interests: outdoor/wellness activities, red light therapy, PC gaming (Valheim), DIY home gym (rice-sandbag weights), geographic/location-reasoning puzzles (GeoGuessr-style).
- Someday-list (blocked on API access, not a near-term build): LinkedIn and Depop automation.

**Still genuinely unknown (fair game for Claude Code to ask, one at a time, not a full re-interview):**
- Budget for tools/APIs per month
- Hours per week available outside day-to-day life (note: Chapman Fall term starts Aug 24 — assume a drop from then)
- Any existing audience/followers to launch to, or starting from zero

**Answered — do not ask again:**
- ~~Appetite for being on camera~~ → **faceless-first, decided 2026-07-21.** See the bullet above.

---

## 6. Daily Opportunity Engine (5 minutes, not a brainstorm session)

Log answers in `/logs/daily-signals.md` — one line each, no analysis yet:

- What annoyed you today?
- What did you spend money on?
- What did you Google twice?
- What took >15 min that should've taken 2?
- What would you pay $20/mo to never do again?
- Any AI tool/news that launched today worth reacting to fast?

Claude Code's job on Fridays: read the week's log, cluster repeats, and score anything that shows up more than once using Section 4.

---

## 7. Weekly CEO Meeting (Friday, 20 minutes)

Claude Code runs the exec panel (CEO / CTO / Sales / Finance) on this week's ideas and the current build:

1. What shipped this week?
2. What's the current build's real usage/revenue number? (Not a vanity metric — clicks, DMs, $ received.)
3. Kill list: what are we stopping?
4. Double-down list: what's working, what's the next smallest step?
5. One new idea to test next week, gate-checked per Section 3.

---

## 8. First-Pass Idea Generation (already scored against your real assets)

Rather than 100 generic ideas, here are the ones that actually clear the bar in Section 4 for *you specifically* — high reuse of Video Analyzer + your spearfishing niche + your stated clipping priority. Use these as Week 1 candidates, not a final answer.

| Idea | Who pays | Smallest MVP | Score |
|---|---|---|---|
| **Spearfishing/dive-spot report service** — turn your existing ranked dive-spot framework into a paid daily/weekly conditions report (swell, visibility, tide) for a specific CA coast segment | Local divers/spearfishers who'd pay to skip manual condition-checking | A simple scraped-data + Claude-written daily Telegram/email digest for one region | 24 |
| **Clip-and-caption pipeline reusing Video Analyzer** — feed long-form videos in, get auto-generated clips + captions + a "why this clip works" score, so you (or clients) can post faster | You, first — then other creators/clippers as a paid tool | Extend Video Analyzer to auto-suggest clip timestamps from a transcript | 23 |
| **"Flagged creator" fact-check feed** (already a planned Video Analyzer feature) productized as a public newsletter/X account calling out inaccurate outdoor/fitness content, monetized via affiliate gear links | Audience interested in outdoor/fitness accuracy; affiliate brands | Manually curate 1x/week using your existing flagging feature | 19 |
| **DIY home-gym content** (sandbag/rice-weight builds) as short-form clips, monetized via clipping-program payouts | Clipping platforms pay per view | Batch-produce 10 short clips using your existing gym-notes feature as source material | 20 |
| **GeoGuessr-style location content** — short clips solving/explaining location puzzles, leaning on your stated interest in geographic reasoning | Clipping platforms / puzzle audience | 5 test clips, see what a clipping program pays out | 18 |

~~Recommendation: start with the **clip-and-caption pipeline**~~ — **done 2026-07-20, see §5.** The build was the easy half. Per the Stage 5 gate, nothing else gets built until this pipeline produces **one real payout or one real click-through**. That means picking ONE actual clipping campaign (Whop/Vyro) with written permission + payout terms and running its content through Clipfarm (`F:\Clipfarm`). The remaining rows in the table above are content *sources* to feed it, not new builds.

---

## 9. Long-Term Roadmap (Life Hacker 3000)

Sequence modules so each funds or feeds the next — don't build them in parallel:

1. ~~**Clip-and-caption pipeline**~~ — ✅ **BUILT 2026-07-20**, spun out 2026-07-21 to its own project at `F:\Clipfarm`. Revenue engine #1, tracked in that repo now. **Not yet monetized** — blocked at Stage 5 (sell), not Stage 4 (build). Next step is a real campaign, not more code.
2. **Spearfishing conditions report** — validates "niche expert content as a product" pattern, reusable for other hobbies later. *Do not start until step 1 earns a dollar.*
3. **Fact-check/flagged-creator feed** — builds on Video Analyzer's filing system, adds an audience/newsletter asset
4. **Saved-content organizer + inventory UI** (already planned) — becomes the personal dashboard that ties modules together
5. **Full hands-off phone-to-filed-note pipeline** (auto-transcription, folder-watching) — mostly covered already by local Whisper + the email-agent intake queue; remaining piece is folder-watching

> **Standing risk (2026-07-21):** the failure mode here is building module 2 because it's fun while module 1 sits unmonetized. Every module in this list is a build; none of them is a sale. Revenue comes from step 1's *distribution*, which is the one thing Claude Code can't do for you.

---

## 10. Executive Team Prompts (Claude Code — paste as needed)

### Weekly Idea Sprint
```
You are my executive team (CEO, CTO, Head of Sales, Head of Marketing).
Read PLAYBOOK.md sections 4 and 5 first.
Using this week's entries in /logs/daily-signals.md, generate 5-10 ideas.
Score each using the Section 4 rubric. Show the math, not just a verdict.
Discard anything under 18. For anything ≥18, answer: who pays, why, and smallest MVP.
```

### Build Gate Check
```
Before writing any code for [idea name]: answer who pays and why, and the
smallest possible MVP, in one line each. If you can't answer both in one
line, we're not ready to build — ask me the one question that would unblock it.
```

### CEO Weekly Review
```
Run the Section 7 Weekly CEO Meeting format against this week's build and
/logs/daily-signals.md. Give me a kill list and a double-down list.
```

---

*Keep this file updated as facts change — it's meant to save you from re-explaining yourself every session, and to keep Claude Code from re-litigating decisions you already made.*
