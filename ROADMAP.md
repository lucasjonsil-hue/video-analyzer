# Life Hacker 3000 — Roadmap

> Written 2026-07-10 during an autonomous build session. This is the forward plan for every module:
> what's done, what's next, and exactly what each next step needs. Sequenced so the easiest wins come first.
> Companion to `CLAUDE.md` (which holds the full specs — this file is the ordered to-do view).

---

## ✅ Done (working today)

| Feature | Where | Status |
|---|---|---|
| Video Analyzer (upload/URL → frames + Whisper → Claude → GitHub note) | `main.py`, `index.html` | Verified end-to-end |
| Notes viewer (search, category filter) | `/notes` | Working |
| Planner v1 — trips (Plan A/B/Fancy) + event checklists | `/planner` | Verified end-to-end |
| Planner: gear memory (Feature B) | `planner_memory.json`, `main.py` | Built 2026-07-10 |
| Planner: live weather + wave forecast in plans | Open-Meteo (free, no key) in `main.py` | Built 2026-07-10 |
| Investment Calculators (compound, goal, dividend, retirement) | `/invest` | Built 2026-07-10 — first piece of the Investment module |
| Email intake code (inbox → video pipeline) | `email_intake.py` | **Written but blocked — see the one thing only Lucas can do, below** |
| notes-checker agent (cross-references questions against saved notes) | `C:\Users\User\.claude\agents\notes-checker.md` | Active from next Claude Code session |

---

## 🔑 The ONE thing only Lucas can do (5 minutes)

Everything email/calendar is blocked behind this one-time Microsoft registration (requires your login, so no AI can do it):

1. Go to https://portal.azure.com and sign in with lucasjonsil@outlook.com
2. Search **App registrations** → **New registration**
3. Name: `Life3000` · Supported account types: **Personal Microsoft accounts only** · leave Redirect URI empty → **Register**
4. In the app: **Authentication** → Advanced settings → **Allow public client flows: Yes** → Save
5. **Overview** page → copy **Application (client) ID** → add to `F:\Life3000\.env` as `MS_CLIENT_ID=<that id>`

Then run `py email_intake.py` (with the analyzer server up), sign in once at microsoft.com/devicelogin, and it works forever after.

---

## 📬 Email & Calendar Assistant — next steps (in order)

1. **[Lucas]** Azure registration above → unblocks everything below.
2. Verify `email_intake.py` end-to-end (send yourself a "video" email with a reel link).
3. Add `Calendars.Read` scope → pull upcoming events into the planner ("what's coming up this week?" auto-plans).
4. Add `Calendars.ReadWrite` → planner writes prep tasks + the event itself back to the calendar (spec §5 Feature A).
5. Email triage v1: summarize unread inbox into a morning digest note (read-only, safe).
6. Scheduled run: Windows Task Scheduler or Claude Code routine runs intake every morning (see Automation below).

## 🗓️ Planner — next steps

1. **Gear memory growth**: it now learns from gear you mention when saving plans — just start saying what you're bringing ("spearfishing Tuesday, bringing the speargun and the 7mm wetsuit").
2. Location awareness: let the message override the Santa Barbara default for forecasts (parse destination → geocode via Open-Meteo's free geocoding API).
3. Calendar wiring (after email module unblocks): plans auto-land on the real calendar.
4. Tide data for spearfishing specifically (NOAA CO-OPS API, free, no key — station 9411340 is Santa Barbara).
5. Plan history view: render `notes/planner.md` nicely inside `/planner` (the raw entries already show in `/notes`).

## 💰 Investment module — next steps

1. ✅ Calculators (done — the no-API starting point the spec called for).
2. Portfolio tracker v1: a simple `portfolio.json` (ticker, shares, cost basis) + free quotes via `yfinance` (no API key) → dashboard page showing value/allocation.
3. Market briefing: daily Claude summary of holdings-relevant news (needs a news source — Finnhub free tier is the spec's pick; needs a free API key, ~2 min signup).
4. Educational assistant: "explain this concept" chat grounded in Lucas's actual holdings.
5. Event tracking: earnings/dividend dates for held tickers (Finnhub free tier covers this too).

## 🏋️ Fitness module — not started; suggested order

1. Cheapest start: a `fitness` note category already exists — analyze workout reels (already works via the analyzer).
2. Workout logger: simple page + JSON storage (no API, like gear memory).
3. Progress-photo analysis: reuse the analyzer's frame-extraction + Claude vision on uploaded photos.
4. Wearable integration (the health-coach reel pattern from your notes): pick a wearable with an API first — this decides everything else. Parked until Lucas owns one.

## ⚙️ Automation upgrades (the "levels 8-10" from your saved reel)

1. **Hooks (level 8)**: auto-run batch analysis when new links land in a watch file — natural next Claude Code skill upgrade.
2. **Headless/scheduled (levels 9-10)**: morning routine — email intake → analyze new links → planner digest of the week ahead. Needs the Azure step first to be worth it.
3. **Supabase data layer**: only when the markdown notes get unwieldy (they're fine for now — don't do this early).

## 🧊 Parked / someday (from CLAUDE.md backlog)

- LinkedIn/Depop posting automation (Browser Use) — wait until there's a real listing workflow to automate.
- Saved-content organizer beyond video (Crawl4AI/Maxun).
- Docker deploy — only when actually deploying off this machine; Docker Desktop not installed yet.
- Roblox coding assistant.

---

## Suggested order of attack for the next few sessions

1. Azure registration (you, 5 min) → verify email intake (one session)
2. Portfolio tracker v1 with yfinance (one session, no keys needed)
3. Calendar read scope + weekly-planner digest (one session)
4. Morning-routine automation (one session, after 1 and 3)
