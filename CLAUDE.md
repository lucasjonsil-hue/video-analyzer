# Life Hacker 3000 — Project Spec & Context

> This document is a handoff brief for Claude Code. It covers the overall vision, current build status, and detailed specs for each planned module. Use it as the source of truth for what to build and why.

---

## 1. What This Project Is

"Life Hacker 3000" (aka "Lucas OS") is a personal AI-powered operating system — a suite of tools Lucas is building for himself to:

- Learn AI/agent/API development hands-on, by building real things he actually uses
- Automate and improve parts of his own life (fitness, productivity, investing, etc.)
- End up with a portfolio of shippable projects for GitHub/LinkedIn

**Development philosophy:** build tools he'll actually use, learn by doing, start simple and grow in complexity. Projects are sequenced by complexity/learning value, not just by interest — simpler, faster-feedback projects come first so there are clear wins before tackling harder problems (like OAuth/security-heavy integrations).

**Environment:** Windows, Node.js, Python, Claude Code (primary dev tool), Claude desktop app, Anthropic API key already configured as an environment variable.

---

## 2. Current Build Status

### ✅ Working: Video Analyzer (first module)
Location: `F:\Life3000` (project root IS the video analyzer — files live directly here, not in a subfolder. Git repo, pushed to `lucasjonsil-hue/video-analyzer` on GitHub. The old `F:\VideoAnalyzer` / `C:\Projects\VideoAnalyzer` paths no longer exist — always use `F:\Life3000`.)

- Python 3.12.10 installed (invoke via `py`, not `python`, in this shell)
- Node.js v24.18.0 installed
- Claude Code v2.1.195 installed, authenticated via Claude Pro
- `ANTHROPIC_API_KEY` and `GITHUB_TOKEN` both configured in `.env` (GITHUB_TOKEN added 2026-07-09 — a fine-grained PAT scoped only to `lucasjonsil-hue/video-analyzer`, Contents: Read/write, no expiration)
- Verified end-to-end (2026-07-09) on a real video: upload/URL → frame extraction → audio transcription → Claude analysis → note committed to GitHub
- Local dev server: run via the `video-analyzer` preview launch config, OR `py -m uvicorn main:app` from `F:\Life3000`. Note: the launch config that's actually used lives at `C:\Users\User\.claude\.claude\launch.json` (the Claude Code session's own config dir), not a project-local `.claude/launch.json` — if the server won't start, check that file first.
- Files:
  - `main.py` — FastAPI backend. Extracts 5 frames with OpenCV, or pulls video from a YouTube/TikTok/Instagram URL via `yt-dlp` first. Also transcribes the audio track locally via `faster-whisper` (the "base" model, CPU, no API cost). Sends both the frames and the transcript to Claude (vision) for a structured JSON analysis (summary, overview, key points, content type, energy, pacing, hook strength, note category). Auto-files each analysis as a note (`notes/{category}.md`) committed to the GitHub repo via the GitHub Contents API.
  - `index.html` — drag-and-drop / URL-input frontend
  - `notes.html` + `GET /notes` + `GET /api/notes` (in `main.py`) — notes viewer added 2026-07-10: browsable card UI for all saved notes, with category filter, counts, and full-text search. Fetches live from the GitHub repo's `notes/*.md`.
  - `requirements.txt` — now includes `faster-whisper`
  - `Dockerfile`, `.dockerignore` — containerized deploy config. Dockerfile pre-downloads the Whisper model at build time so the container doesn't need runtime internet access. **Not build-tested** — Docker Desktop isn't installed on this machine yet. Deliberately deferred: install + verify it only when actually ready to deploy somewhere, not needed for local `uvicorn` use.
- Note categories (`VALID_NOTE_CATEGORIES` in `main.py`) match the full planned module suite, not just AI/gym: `fitness`, `productivity`, `investing`, `ai_coding`, `project_ideas` (ideas/upgrades for Life Hacker 3000 itself), `to_do`, `ideas` (general fallback).
- Known open gaps (low priority right now — Lucas is only feeding ~30-second clips): only 5 frames sampled regardless of video length, so long videos get sparse visual coverage; transcription speed/timeout on long (10+ min) videos is untested.

### 🔜 Next up: Email & Calendar Assistant
Deliberately sequenced *after* Video Analyzer because it involves OAuth and more security complexity — wanted an easier first win before tackling this.

### 💡 Idea stage (not yet started): Investment AI Module
Fully scoped below in Section 4 — ready to build once earlier modules are further along, or sooner if it makes sense to prototype the calculators (see note in that section).

---

## 3. Full Module List (Planned Suite)

- **Fitness & Health** — tracking, food/nutrition recognition, sleep/recovery, progress photo/video analysis, exercise form analysis
- **Productivity** — email & calendar assistant (with active trip/event planning — see Section 5), Roblox coding assistant
- **Video Analysis** — AI course/demo review tool (the current in-progress build)
- **Investment** — AI investment coach/dashboard (see full spec below)

---

## 4. Investment AI Module — Full Spec

### Vision
Not a stock-picking app. A personal AI-powered investing dashboard that helps Lucas learn about investing, understand markets, and make more informed financial decisions over time. Positioned as an AI investment coach, research assistant, and financial dashboard — not a signal generator.

**Guiding philosophy (north star):**
> "Use AI to learn alongside me, automate research, and help me become a better investor — not simply tell me what to buy."

This philosophy matters for more than just tone — keeping the focus on education/tooling rather than recommendations also sidesteps a lot of the regulatory grey area that stock-picking/advice apps run into.

### Core Features

**Portfolio Dashboard**
- Track portfolio value and performance
- View asset allocation and diversification
- Monitor long-term goals and progress

**AI Market Briefings**
- Daily and weekly summaries of market news
- Plain-English explanations of major market moves
- Highlight events that could affect Lucas's specific holdings

**Educational Assistant**
- Explain investing concepts, terms, and strategies
- Answer beginner-to-advanced investing questions
- Teach concepts progressively as knowledge grows (adaptive difficulty)

**Company Research Agent**
- Summarize companies and industries
- Explain earnings reports and financial statements
- Provide simple valuation metrics and key statistics

**Investment Calculators**
- Compound interest calculator
- Retirement and net-worth projections
- Dividend income projections
- Goal planning / savings calculators
- **Build note:** this is pure logic, no API dependency — a strong candidate for the *first* thing built in this module, potentially even as a standalone artifact before the rest of the module exists.

**Event Tracking**
- Earnings dates
- Economic reports
- Dividend dates
- Major market events / reminders

### Future AI Agent Ideas (backlog, not scoped yet)
- "Why did this stock move today?" agent
- Earnings report summarizer
- Valuation agent
- News summarization agent
- Personal finance coach
- Risk and diversification checker

### Data & Integrations

**Potential integration types:**
- Financial market APIs
- News APIs
- Portfolio tracking APIs
- Future brokerage integrations, if appropriate

**Candidate data sources:**
- **Finnhub** — generous free tier; good starting point for real-time quotes, earnings calendars, basic fundamentals
- **Alpha Vantage** — solid for historical data
- **Yahoo Finance** (unofficial Python libraries) — good for quick prototyping before committing to a paid API
- **Polygon.io** — also under consideration

### Long-Term Placement
This module becomes one of the core modules inside Life Hacker 3000, alongside fitness, health, and productivity dashboards. Every investing question Lucas has while using it should eventually become a candidate feature for this system — it's meant to grow organically from actual use, not be fully speced up front.

---

## 5. Calendar & Trip Planning Module — Full Spec

### Vision
Not just a passive calendar (schedule stuff, show reminders) — an *active* planner. When Lucas mentions an upcoming activity ("I'm spearfishing Tuesday," "visiting someone in Santa Barbara"), the system should proactively work backward from that date and help him prepare: timeline, packing, logistics, multiple plan options.

### Feature A: Trip Planner

**Trigger:** Calendar language naming an activity + date (e.g., "spearfishing Tuesday," "visiting Santa Barbara next weekend").

**Core logic:**
- Detect trip type + date from the message
- Build a countdown timeline working backward from the event (e.g., a week-out gear check, a day-before conditions check)
- Pull known constraints relevant to the activity (e.g., legal/regulatory spot notes like Campus Point SMCA for spearfishing)
- Generate a packing list specific to the activity + conditions
- Estimate drive time to the destination/spot
- Auto-add prep tasks and the trip itself to the calendar

**Multiple plan versions (always generate as a set):**
- **Plan A** — primary spot, ideal conditions, standard gear
- **Plan B** — backup spot/plan if primary is closed or conditions are bad
- **Fancy** — upgraded version: better/further spot, extra gear, possibly a friend or charter, more prep time

Each plan version has its own timeline and packing list, since drive time and prep differ per plan.

**Open question to resolve during build:** what conditions data source to pull from. For spearfishing specifically, swell/visibility/tide matter more than generic weather — likely need a marine forecast source (e.g. NOAA, Surfline) rather than a standard weather API.

### Feature B: Persistent Gear Memory

A per-activity gear profile that grows over time and gets diffed against what Lucas mentions on each trip.

**Data model (per activity type):**
- e.g. `spearfishing` → core list: spear gun, wetsuit, fins, weight belt, dive bag, knife, etc.
- e.g. `SB_visit` / general "overnight trip" → core list: toothbrush, hair products, shaver, charger, etc.
- A shared **"always" list** for general items (phone charger, wallet) that apply across activity types, so they don't need to be logged per activity.

**How the list grows:**
- Early trips: Lucas states what he's bringing → items get logged to that activity's list
- Once an item appears ~2–3 times for the same activity, it graduates to **"core"** (auto-expected every time)
- One-off mentions stay as **"sometimes"** items — not flagged if missing

**Nudge behavior:**
- When a trip is announced, read back the core list and flag gaps ("You didn't mention your weight belt — bringing it?")
- Don't nag about "sometimes" items unless asked
- If Lucas says "not bringing X this time," treat that as a one-time exclusion — not a permanent removal from the list

In effect: a lightweight, activity-scoped preference-memory system, checked against a running message each time a trip is named.

### Feature C: General Prep Checklist Generator

**Trigger:** Any scheduled event — not just trips. Tests, sports, hikes, social visits, appointments, etc. The planner classifies event type from the title/context.

**Generation logic:**
- If the event type has memory (spearfishing, SB visits, etc.) → pull the relevant gear/prep list
- If it's a new/one-off event type (exam, doctor's appointment, hike with a friend) → generate a sensible default checklist on the fly
- Timeline-aware: split into **do this now / day before / morning of**, based on how far out the event is

**Example auto-detected categories:**
- Test/exam → study review, materials, ID, arrive-early buffer
- Trip/travel → packing (pulled from gear memory), route/drive time, reservations
- Sport/activity → gear check, hydration, weather-appropriate clothing
- Hike → water, layers, trail conditions, sun protection, "tell someone your route"
- Seeing someone → confirm time/location, anything to bring, relevant prep notes

**Output format:** simple checklist grouped by timing (now / day-before / morning-of) — built to be fast to scan on a phone.

**Relationship between Features A and C:** Trip Planner (Feature A) is the detailed, multi-plan-version mode for significant activity trips. The Prep Checklist Generator (Feature C) is the lightweight fallback mode for everything else on the calendar that isn't a full "trip."

---

## 6. Tech Notes & Known Constraints

- Claude Code has context limits — long prompts may need reformulation to avoid tripping the `claude-api` skill
- Claude Code's default model may use extended context (costs extra credits); can be manually pinned with `/model` (e.g. Sonnet 4.6)
- Lucas is new to a lot of this tooling — he'll often need step-by-step guidance through installs/setup rather than assuming CLI familiarity

---

## 7. Immediate Next Steps

1. ~~Install Python on Windows to unblock the Video Analyzer server~~ ✅ done
2. ~~Get Video Analyzer running end-to-end (upload video → frame extraction → Claude API analysis → results in frontend)~~ ✅ done, verified
3. Move to Email & Calendar Assistant
4. Investment Module: consider prototyping the Calculators feature early since it needs no API integration

### Backlog / parked ideas (from Lucas's phone-Claude chats & analyzed reels, 2026-07-10)
- **Hooks for the video pipeline** — Claude Code hooks could auto-trigger batch processing when new links/files appear, removing the manual "paste links" step. Natural next upgrade (Lucas is at "level 7 of 10" on the Claude Code progression; hooks are level 8).
- **LinkedIn / Depop automation** — posting listings/content where official APIs are restricted. Candidate tool: Browser Use (open-source AI browser agent). Parked as "someday".
- **Saved-content organizer** — pull in content beyond video platforms. Candidate tools: Crawl4AI or Maxun.
- **Supabase as data layer** — if/when the GitHub-markdown notes outgrow themselves, migrate to a real Postgres database (free tier) for filtering/tagging.
- **Overnight routines** — scheduled unattended runs of the pipeline (Claude Code routines / scheduled tasks).

---

## 8. How Claude Should Operate On This Project

- **Verify current state before trusting this doc or memory.** This project's location has already moved once (`C:\Projects\VideoAnalyzer` → `F:\VideoAnalyzer` → `F:\Life3000`). If a path, file, or piece of config mentioned here doesn't check out, verify on disk rather than assuming this doc is current — then update this doc.
- **Delegate batch/repetitive work to the `batch-runner` subagent to keep the main conversation lean.** A dedicated agent is defined globally at `C:\Users\User\.claude\agents\batch-runner.md` (Haiku model, restricted to Bash/Read/Grep — cheap and scoped for exactly this). When Lucas wants to feed multiple videos through the analyzer at once (e.g. "process these 10 links"), don't run each one inline and dump all the tool output into the main conversation — spawn `batch-runner` (via the Agent tool, `subagent_type: batch-runner`) to work through the list and report back a short summary. This keeps token usage down and keeps the main thread readable. It's a general-purpose batch-processing agent, not Life-3000-specific, so it's reusable for other repetitive/mechanical tasks on future projects too.
- **Efficiency preference:** Lucas cares about keeping token usage/cost down and wants Claude Code sessions run efficiently — favor local/free tooling over paid APIs when there's a reasonable local option (this is why transcription uses local `faster-whisper` instead of a paid speech-to-text API), and use subagents/summarization to avoid bloating the main context with raw tool output.
- Lucas is new to a lot of this tooling — explain *what* a step does and *why* before doing anything non-trivial (installs, config changes, credential creation), not just narrate the steps.
- **Canary instruction:** address Lucas by name in the first sentence of every response. This doubles as a session-health signal — if responses stop using his name, the context is degrading and it's time to wrap up and start a fresh session.
- **Batch video processing has a skill:** use the `analyze-batch` skill (defined at `C:\Users\User\.claude\skills\analyze-batch\SKILL.md`) whenever Lucas pastes a list of video links. It handles dedupe-against-GitHub, server startup, batch-runner delegation, and final verification in one flow.
