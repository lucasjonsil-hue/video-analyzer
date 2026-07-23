# To Do Notes

## 2026-07-09 18:48 UTC
Source: https://www.instagram.com/reel/DX8F_9zTuMf/?igsh=NTc4MTIwNjQ2YQ==

A young man in a suit presents five free certifications that students can add to their CV to become more employable in the near future. The certifications span AI, digital marketing, software tools, and cybersecurity. Each certification is briefly explained with context on why employers value it.

The presenter, dressed professionally in a navy suit and yellow tie, addresses students directly, claiming these five free certifications will be critical for future employability. He covers: (1) Google AI Essentials – a free course completable in under two hours focused on artificial intelligence skills; (2) HubSpot Digital Marketing Certification – widely recognised by employers, especially valuable in marketing roles; (3) GitHub Foundations – demonstrates proficiency in the version control platform most businesses use to store and manage code; (4) Cored Certified Architect – shows understanding of AI tools beyond basic chat functions, proving confident and capable AI usage; (5) IBM Skills Build Certification – a cybersecurity credential showing employers you understand computing and internet safety. The video is framed as career advice for students and ends with a call to follow the creator.

- Google AI Essentials is free and can be completed in under two hours
- HubSpot Digital Marketing Certification is widely recognised by employers
- GitHub Foundations shows employers you can use the tool most businesses rely on for code
- Cored Certified Architect demonstrates advanced AI tool usage beyond basic chat
- IBM Skills Build Certification covers cybersecurity fundamentals
- All five certifications are free and suitable for adding to a CV

## 2026-07-09 18:51 UTC
Source: https://www.instagram.com/reel/DZ8DNSOR16-/?igsh=NTc4MTIwNjQ2YQ==

A young content creator presents 10 free AI certifications that students should add to their resumes, highlighting offerings from Microsoft/LinkedIn, IBM, and Google Cloud. The video emphasizes the growing importance of AI credentials in today's job market and promises to share links to all certifications via comment engagement.

The creator introduces a 'niche edition' list of 10 free AI certifications recommended for student resumes. He highlights three specific certifications: (1) Microsoft and LinkedIn's 'Career Essentials in Generative AI' (4.5 hours, covers Computer Ethics, AI, and Generative AI), noting that 66% of CEOs won't hire without AI experience; (2) IBM's Artificial Intelligence Fundamentals, described as longer but providing an IBM credential recognized by employers; and (3) Google Cloud's 'Introduction to Responsible AI,' which takes only 15 minutes and is highly relevant in today's market. The video ends with a call-to-action asking viewers to follow and comment 'resume' to receive links to all 10 certifications plus 20 more.

- Microsoft & LinkedIn Career Essentials in Generative AI is a free 4.5-hour certification
- 66% of CEOs say they won't hire candidates without AI experience
- IBM AI Fundamentals provides an employer-recognized IBM credential
- Google Cloud's Intro to Responsible AI takes only 15 minutes
- All certifications are free and resume-worthy
- Comment 'resume' to receive links to 10 certs plus 20 more

## 2026-07-18 15:23 UTC
Source: https://www.instagram.com/reel/DYLhCUeoH8o/?igsh=NTc4MTIwNjQ2YQ==
Creator: Arya Patel

This video highlights free certifications that can boost a resume, targeting people who currently have no certifications. It showcases four specific free certification opportunities from Anthropic (Claude), HubSpot, and IBM SkillsBuild, ending with a call to action to follow and comment for links.

The video opens with a relatable hook of someone admitting they have no certifications on their resume. It then walks through four free certification options: #1 is the Claude Certified Architect certification from Anthropic, noted as something Deloitte pays significant money to obtain. #2 is not fully visible but is implied. #3 is HubSpot Academy's Digital Marketing Certification Course, a free 5-hour course requiring no student email. #4 is IBM SkillsBuild's 'Getting Started with Generative AI' course, which offers 12 college credits plus 8 more for free. The video ends by asking viewers to follow and comment 'RESUME' to receive the links to these courses.

- Anthropic Claude Certified Architect certification is valued by companies like Deloitte
- HubSpot Digital Marketing Certification is free, takes 5 hours, and needs no student email
- IBM SkillsBuild offers Generative AI certification with 12+ college credits for free
- All certifications listed are 100% free with no credit card required
- Aimed at job seekers with no current certifications on their resume

<details><summary>Full transcript</summary>

Okay

</details>

## 2026-07-18 17:04 UTC
Source: email assistant setup session

Send the Chapman IT app-approval request. The email is ready and waiting in the Outlook Drafts folder (personal account), addressed to servicedesk@chapman.edu. Best sent from the Chapman address (lusilva@chapman.edu) — copy the text over when sending. It asks IT to approve the Life3000 app so the email assistant can read the school mailbox directly; until then, school mail reaches the assistant via auto-forwarding.

- Draft location: Outlook Drafts, subject "Student request: app approval..."
- If approved: rerun py email_intake.py --add-account with the school account

## 2026-07-18 20:40 UTC
Source: claude session

Done this session: read the two "life 3000 update" .md emails Lucas sent from his phone and filed both into notes/project_ideas.md (gym notepad feature spec; photos-to-Claude via Drive/Dropbox camera-upload sync). Confirmed Lucas sent the Chapman IT app-approval request himself — ticket IST-151079, auto-ack received, human reply pending. Found and fixed a bug: email_agent.py had crashed on every scheduled run since ~13:27 (UnicodeEncodeError on emoji in subjects under cp1252); fixed with utf-8 stdout/stderr reconfigure and verified with a clean full run (25 emails triaged). Created the /jarvis wake-word skill.

Next move: build the gym notepad feature (step 1 of its build order: notepad textarea + local storage in the gym section). Also pending Lucas's call: connect Google Drive vs Dropbox for photo sync; commit the email_agent.py fix + notes changes (uncommitted locally).

## 2026-07-18 20:56 UTC
Source: claude session

Gym notepad step 1 BUILT and verified: new gym.py router (GET /gym, GET/POST/DELETE /api/gym/notes) + gym.html (dark-theme page: textarea, optional exercise/weight quick-add with autocomplete, timestamped note cards, delete). Data persists in local gym_data.json (gitignored, shape {routine, notes} so the planner can later read the routine to estimate session length). Zero AI tokens at capture; the future "Review notes" step should keyword-match notes/fitness.md summary bullets only (never transcripts) to stay cheap. Linked from the analyzer homepage.

Next move: gym notepad step 2 — "Review notes" button (pull routine + unreviewed notes into one prompt, suggest routine edits as approve/reject cards). Also still pending: Drive vs Dropbox choice for photo sync; Chapman IT ticket IST-151079 human reply (expect Mon/Tue).

## 2026-07-19 04:23 UTC
Source: https://www.tiktok.com/t/ZTSoH1vEp/
Creator: phillie_cheez

A man warns Snapchat users that their memories will be deleted in October and advises them to export their data via Snapchat settings. He then promotes a service called 'Snap Easy' that helps organize the exported files for $10 lifetime access.

The creator alerts viewers about a Snapchat policy change that will delete saved memories in October. He walks through the steps to export memories: go to Settings > My Data > Export Memories > select All Time > enter email > submit. He warns that Snapchat sends the exported data in around 30 disorganized files with captions and filters separated. He then promotes his own tool called 'Snap Easy' which consolidates all exported files back into organized memories for a one-time $10 lifetime fee, compared to an alternative $24/year option. The video ends urging users to save memories to camera roll so they won't need Snapchat memories again.

- Snapchat is reportedly deleting all user memories in October
- Users can export memories via Settings > My Data > Export Memories
- Exported files arrive in ~30 disorganized chunks via email
- Snap Easy tool consolidates the files for $10 lifetime access
- Users should save memories to camera roll after export

⚠️ Reliability (hype: mild):
- [unverifiable] Snapchat is deleting all user memories in October — No widely confirmed Snapchat policy announcement supports this specific claim of mass memory deletion.
- [unverifiable] Snap Easy costs $10 for lifetime access vs $24/year for an alternative — The pricing and the competing product cannot be independently verified from the video alone.

<details><summary>Full transcript</summary>

For those of you that didn't get this message, it only means that Snapchat is deleting your memories in October of this year. That means parties, vacations, kids, wives, husbands, memories all gonna be gone. For you not to lose those memories, you have to go to settings and Snapchat, go to my data, then you go export your memories, only my memories. Then you put all time to make sure you get all of them. Your email, click submit. That's it. You just wait anywhere from a couple hours to a couple days for that email to come in. The only problem is that Snapchat sends it to you in like 30 different files and they're all jumbled up and all mixed up your captions. So if your filter is your location, everything is gonna be separate. That's when you go to snap easy. You just input all of those files into our converter and it spits out all your memories attached with everything. Just the way you save them, just the way you took them. And it's only 10 bucks for lifetime access instead of $24 a year and then multiply that by five by 10 by 20. Because if you don't do this, you're gonna lose your memories forever. Then you just hit save to camera roll after every memory. That way you don't have to use Snapchat memories ever again.

</details>

## 2026-07-19 05:13 UTC
Source: claude session

Big session. Done: (1) Gym notepad steps 2-4 — "Review notes" button reviews session notes + saved fitness videos, suggests routine edits and "try this workout from this video" cards with approve/reject; verified end-to-end. (2) Photo sync DONE — Dropbox connected (Drive can't auto-upload camera roll on iPhone), camera uploads verified readable by Claude. (3) ANALYZER_MODEL env knob added (set claude-haiku-4-5-20251001 in .env for ~3x cheaper video analysis; default unchanged). (4) Hermes Agent is REAL (Nous Research, open-source) — memory corrected; decided not to adopt (Claude Code setup already covers it); OmniRoute real but skipped (ToS/privacy risks). (5) Fact-checked email links: Snapchat memories = real policy but only >5GB at risk, deadline ~Sept 2026, skip "Snap Easy"; MarketPulse Robinhood auto-trader = avoid; Intern Dock free-cert list = legit (23 real certs); Angus Sewell = trustworthy creator, zero flagged claims. (6) Portfolio tracker v1 on /invest — local portfolio.json + live yfinance quotes, add/delete verified. (7) Planner wave alert built + verified — 7-day SB swell strip, files deduped reminders via email agent runs; SET TO 3 ft / 9 s, ON.

Next move: add real holdings to the portfolio tracker (Lucas, 2 min on /invest), then calendar wiring (roadmap step 3: Calendars.Read -> weekly planner digest). Later: gym notepad step 5 (weight progression table). Waiting: Chapman IT ticket IST-151079 (Mon/Tue).

## 2026-07-19 20:27 UTC
Source: claude session

Done this session: built the local Calendar module (/calendar page, calendar_module.py, data in local calendar_data.json — no Microsoft/Google) with manual add plus a "just type it" natural-language box (one Haiku call per add); planner now feeds the next 2 weeks of calendar events into plan generation to avoid conflicts. Added a 🏠 Home link to every page and full nav on the homepage. Gym notepad step 5 done: Progress table (per-exercise first/latest/change/history from weight quick-adds, client-side, zero tokens). All committed + pushed (78860b1). Portfolio tracker stays empty on purpose — Lucas has no holdings yet; calculators are example numbers. Created the /saveit shutdown skill (registers from next session).

Next move: normal use — add real events via the calendar's "just type it" box, log gym sessions to grow the Progress table. Candidate next build: Claude Code hooks to auto-trigger batch video processing (backlog). Waiting: Chapman IT ticket IST-151079 human reply (expected Mon/Tue).

## 2026-07-20 05:42 UTC
Source: claude session

Done this session: (1) /jarvis now auto-processes the video backlog — email_agent.py queues failed/skipped links into video_backlog.txt (gitignored) and the jarvis skill batch-retries them in the background after the recap; queue function live-tested. (2) Lucas's main goal (make money) saved to auto-memory and to CLAUDE.md §1 as a standing lens; UGC interest noted. (3) UGC researched (real platforms: JoinBrands/Billo/UGCJobs, beginner rates $50-150/video; Bounty is views-dependent, not the no-follower path) — paste-ready Claude-chat workflow brief at docs/ugc_workflow_brief.md. (4) Clipper pipeline BUILT + tested e2e at clipper/ — py pipeline.py <url>: yt-dlp ingest, local Whisper word-level transcript, one Claude call picks 5 viral moments, ffmpeg cuts vertical 1080x1920, burns bold word-timed captions; test video produced 5 good clips in ~85s. Only-paid-step = 1 Sonnet call (~cents). Media dirs gitignored.

Next move: Lucas pastes docs/ugc_workflow_brief.md into Claude chat to get his week-by-week UGC plan; for clipping, pick ONE real Whop/Vyro campaign (permission + payout terms) and run its content through the clipper. Waiting: Chapman IT ticket IST-151079.

## 2026-07-20 19:15 UTC
Source: claude session

Done this session: (1) Added a permanent email check to /jarvis — new read-only jarvis_email_peek.py lists recent inbox mail, spawned via a batch-runner agent each recap. (2) Processed the "links again" email: 15 Instagram reels analyzed into Life 3000 (the scheduled email_agent already caught them — all 15 notes landed on GitHub; did NOT launch a competing batch). (3) Logged the chest/tri gym session from that email (chest push 160, chest fly 110, elevated chest press 50, tri pushdowns 90, dips 35) to gym_data.json. (4) Built the calendar-from-email flow into /jarvis with a two-tier rule (auto-add important/unambiguous dates + hard deadlines; yes/no confirm for low-stakes) — Lucas's explicit preference. (5) Verified Chapman's real 2026-27 academic calendar and auto-added 15 school dates + 2 health-insurance deadlines (17 events total in calendar_data.json). (6) Saved memories: user-chapman-school (Orange CA, full 2026-27 dates), feedback-lookup-dont-guess (search web for unknown dates, never guess).

Next move: Lucas's call on two open items — (a) archive Dropbox Camera Uploads (2.0 GB, 396 photos, 100% full → sync stalled) to F: then clear Dropbox; (b) dig into the 15 new reel notes for the "how do we build this / make part of life 3000" questions he flagged. Also pending on Lucas: submit the Chapman health-insurance eForm in Student Center before Aug 24 (only he can). Waiting: Chapman IT ticket IST-151079.

## 2026-07-21 22:40 UTC
Source: claude session

Found the AI Founder Playbook Lucas made with Claude/ChatGPT at C:\Users\User\Downloads\AI_FOUNDER_PLAYBOOK.md and installed it as F:\Life3000\PLAYBOOK.md (the doc's own instruction), linked from CLAUDE.md, and seeded logs/daily-signals.md for its Section 6 daily capture habit. Corrected four stale facts in its Profile Snapshot: location is Orange CA / Chapman (not San Anselmo, confirmed by Lucas), Whisper speech-to-text and GITHUB_TOKEN are both working (listed as gaps), and the clip-and-caption pipeline it recommends as priority #1 is already BUILT at clipper/ — so roadmap step 1 is now marked done and reframed as blocked at Stage 5 (sell), not Stage 4 (build). Lucas was surprised to learn UGC usually means being on camera; clarified that clipping needs no face at all and that faceless UGC (voiceover + b-roll, hands-only, screen recordings) is a real paid category. He decided FACELESS-FIRST — recorded in PLAYBOOK.md Section 5 as a decided constraint (not an open question) and saved to auto-memory as user_faceless_first.md. On-camera brand UGC deferred, not rejected.

Also noted: the scheduled email agent filed "Use Paracord Galaxy coupon Lovecord" into notes/reminders.md TWICE from a promo email — exactly the marketing junk the two-tier calendar rule is meant to filter. The agent's reminder-creation path needs the same junk filter the /jarvis calendar step has. Worth a look next session.

Next move: still three open Section 5 gaps to answer (monthly tool/API budget, hours per week — note Chapman Fall term starts Aug 24, and whether he has any existing audience). Then the real one: pick ONE actual clipping campaign (Whop/Vyro) with written permission + payout terms and run content through clipper/pipeline.py — per the playbook's own Stage 5 gate, nothing else gets built until that pipeline earns a dollar or a real click-through.

## 2026-07-22 04:22 UTC
Source: claude session

Done this session: (1) CAMPAIGN FOUND — surveyed the live clipping boards. Whop's Content Rewards board is login-only now (public site pivoted to "create a business"); Vyro had 4 live campaigns with public briefs. Only ONE fits the pipeline: **MrBeast x Joe Rogan** ($1,500/1M views = $1.50 CPM, long-form podcast source, minimal rules, hourly Stripe/PayPal payout). Super Troopers 3 pays more ($2 CPM) but is assets-folder-only with Disney work-made-for-hire terms + mandatory on-screen CTA overlays the pipeline can't produce; Valorant Miks wants trending-audio fan edits, not transcript clips. Both marked fits_pipeline:false with reasons. (2) CLIPPER SPUN OUT to its own project at **F:\Clipfarm** (Lucas's call — it's a revenue business, not personal tooling; named Clipfarm over "LA Clipper" to avoid the NBA trademark). Standalone: own .env, own 142MB Whisper cache copy, common.py no longer resolves paths via a parent dir. Verified imports + Whisper load BEFORE deleting F:\Life3000\clipper. Own git repo, 2 commits, no GitHub remote yet. (3) CLIPPING NOTES ROUTED — analyzer gained a `clipping` note category (payout rates, platforms, campaign rules, clipping scams) that writes to F:\Clipfarm\notes\clipping.md instead of committing to the video-analyzer GitHub repo; CLIPFARM_NOTES_DIR overrides, fails soft if F: unmounted. Route tested, 3 existing clipping videos backfilled from ideas.md/productivity.md. (4) campaigns.json created in Clipfarm = Stage 1 shortlist so the research survives the session. (5) /jarvis updated to check BOTH repos, surface recommended campaigns + deadlines inside 14 days, and explicitly NOT propose new Clipfarm features until it earns a dollar. PLAYBOOK.md + auto-memory updated (new project_clipfarm.md).

NOT done: nothing pushed to GitHub — Clipfarm has no remote and Life3000's commit is local. Lucas's call.

Next move: Lucas signs up at app.vyro.com, joins the MrBeast x Joe Rogan campaign, and pastes the source video URL — everything downstream is blocked on that. Then run it through F:\Clipfarm\pipeline.py and check the 5 output clips against the campaign rule list before posting. Note: campaign is already ~5 days old and budget drains (payouts split evenly across clips near the end), so speed matters. Still open from before: 3 PLAYBOOK Section 5 gaps (monthly API budget, hours/week before Aug 24, existing audience); the email agent's reminder path still needs the junk filter (Paracord coupon filed twice). Waiting: Chapman IT ticket IST-151079.

## 2026-07-22 04:30 UTC
Source: claude session

Wrap-up addendum to the 04:22 entry. Pushed Life3000 to GitHub (commit 4b0195a) — the push initially rejected because the scheduled email agent had committed two more "paracord galaxy 10% coupon" reminders remotely; rebased cleanly (no file overlap) and pushed. That promo has now been filed FOUR times into notes/reminders.md — the email agent's reminder path still has no junk filter and the file is degrading with each run. Fix that early next session.

Clipfarm is committed locally (2 commits, clean tree) but NOT on GitHub yet: Lucas chose a PRIVATE repo, and it can't be created from here (gh CLI not installed; GITHUB_TOKEN is a fine-grained PAT scoped to video-analyzer only). Lucas needs to create github.com/lucasjonsil-hue/clipfarm as private with NO README/gitignore/license initialization, then run: git -C F:/Clipfarm remote add origin https://github.com/lucasjonsil-hue/clipfarm.git && git -C F:/Clipfarm branch -M main && git -C F:/Clipfarm push -u origin main

Next move unchanged and still the real blocker: sign up at app.vyro.com, join the MrBeast x Joe Rogan campaign ($1.50 CPM, ~5 days old, budget drains and splits evenly near the end so speed matters), paste the source video URL, then run it through F:\Clipfarm\pipeline.py and check the 5 clips against the campaign rules before posting.

## 2026-07-23 05:53 UTC
Source: claude session

Big multi-project session. (Life3000) Built content_calendar.py — weekly faceless-clip posting plan generated from Clipfarm's live campaigns.json (Haiku, run_content_calendar.bat for Task Scheduler); tested, working. Added capture_link_notes() to email_agent.py so Lucas's notes UNDER links in his self-emails are auto-captured to notes/link_notes.md every run (fixes the /jarvis peek truncating his notes). Read his full "links" email, analyzed all 11 videos, cross-checked each note vs the actual video in link_notes.md — flagged the "Amboras/Claude Fable 5" e-com and market-timing ones as hype; the content-calendar and self-prompting ones as real. Saved 4 pasted master-plans to F:\Life3000\plans\. (New project) Built Auto Job Finder at F:\JobFinder — SQLite + FastAPI dashboard + sources (usajobs/neogov/craigslist/manual), dedupe, new-since-last-check; verified serving. Needs a free USAJobs key; NEOGOV needs Playwright. (Clipfarm) Added long-form mode: pipeline.py + moments.py now auto-scale clip count to video length (full podcast -> ~40 clips) and accept local files. (Vyro — the money) Signed Lucas up (account lucassilvaclips), onboarded as Creator, JOINED the MrBeast x Joe Rogan campaign ($1.50/1M views, min 5k views/clip, max $1000/clip, requires #MrBeast + #paidpartner, no other tags/watermarks, likes+comments on; 58% budget already paid out, ~6d left). Spotted a NEW MrBeast Moments campaign at $3,000/1M (2x) worth checking. Campaign source = a Frame.io folder (f.io/LrfU3lVT, 15.14GB): "Full Podcast" (1 item) + "Premade Clips" (7 items). Frame.io blocks ALL automation (yt-dlp unsupported; in-app browser pane wouldn't composite; claude-in-chrome hard-blocks the domain) — so Lucas manually downloaded the 7 premade clips. They came 16:9 horizontal, so I'm converting all 7 to vertical 1080x1920 (blurred-bg) into F:\Clipfarm\output\premade_vertical\ (conversion still finishing in background at save time).

Next move: post the 7 vertical clips (F:\Clipfarm\output\premade_vertical\) to TikTok/IG/YT with #MrBeast + #paidpartner, likes/comments ON, then SUBMIT each in Vyro immediately (views before submission don't count). After that, optionally grab the Full Podcast (15GB) and run pipeline.py for ~40 more unique clips. Still open: Chapman Master Payment Contract + Proof of Health Insurance eForm (BOTH due Aug 24, Student Center > eForms); JobFinder needs a free USAJobs key; email_agent reminder junk-filter (paracord) still unfixed; Clipfarm still has no GitHub remote (private repo not created).

## 2026-07-23 23:50 UTC
Source: claude session

NEW PROJECT: Archie Pool client site scaffolded at F:\ArchiePool — the first PAYING client for the website-service-masterplan (Downloads\website-service-masterplan.md). Lucas's CLAUDE.md handoff doc was found at C:\Users\User\Downloads\CLAUDE.md (downloaded 2026-07-23 16:33); no repo existed anywhere. Scaffolded Next.js 16.2.11 (App Router, TypeScript, src/, @/* alias) + Tailwind v4 + ESLint 9, verified running clean on localhost:3000 (Turbopack, ready 5.7s, zero console errors). Filled in his CLAUDE.md with the real stack, run instructions, kept the two-dev branch/PR working agreements, and appended 4 open client questions (is "Archie" the owner or the business; cleaning vs repair vs installation; service area; booking vs contact form — the first two change the page structure). Git initialized, 1 commit (5c1c638), clean tree; had to add F:/ArchiePool to git safe.directory (F: doesn't record ownership). Notes: package.json is `archie-pool` (npm rejects capitals) while the folder is `ArchiePool` — pick one before creating the repo. npm audit shows 3 high vulns in postcss/sharp pulled in by Next itself — do NOT run `npm audit fix --force`, it downgrades to Next 9.3.3 and destroys the project. Launch config `archie-pool` added to C:\Users\User\.claude\.claude\launch.json using `npm --prefix F:\ArchiePool run dev` (preview_start rejects an absolute cwd outside the project root).

INSTALLED gh CLI 2.96.0 via winget (C:\Program Files\GitHub CLI\gh.exe). NOT authenticated yet and NOT on PATH in existing shells — Lucas must open a NEW terminal and run `gh auth login` himself (GitHub.com / HTTPS / web browser, ensure `repo` scope). The existing GITHUB_TOKEN is a fine-grained PAT scoped only to lucasjonsil-hue/video-analyzer and cannot create repos.

Also this session: answered "what did the video analyzer actually prove" — the ONE verified win is the $1-1.50/1k-views clipping rate (confirmed by the real Vyro $1.50 CPM campaign); everything else either just validated what Life3000 already does (cron+skills architecture, content calendar, Scrapling is real but hyped) or got debunked. The analyzer's real value is as a bullshit filter: 13 creators / ~20 false claims flagged. FOUND A BUG: content_calendar.py line ~139 feeds the first 2500 chars of Clipfarm/notes/clipping.md into the prompt, and those chars are the hype reels — so this week's plan tells Lucas to cut Rogan-podcast moments that DON'T EXIST (Musa's $3M, the $120K CoD campaign, the $1T ad shift). Cutting to that plan would violate the campaign's "must not misrepresent the video" rule. Fix: point the calendar at the actual podcast transcript instead of clipping.md. NOT fixed yet.

Next move: Lucas runs `gh auth login` in a new terminal, then I run `gh repo create lucasjonsil-hue/archie-pool --private --source F:\ArchiePool --remote origin --push`, add his buddy as collaborator (need their GitHub username), and optionally protect main. Still unblocked and time-sensitive: post the 7 vertical MrBeast clips in F:\Clipfarm\output\premade_vertical\ with #MrBeast + #paidpartner and SUBMIT each in Vyro (campaign ends ~Jul 29, budget splits evenly near the end). Also open: content_calendar.py source bug; Chapman Master Payment Contract + Proof of Health Insurance eForm (both due Aug 24); JobFinder needs a free USAJobs key; Clipfarm still has no GitHub remote; email_agent reminder junk-filter (paracord) still unfixed. Pending Lucas's yes/no: add Chapman Spring 2027 study-abroad Pre-Departure Orientation (Fri Oct 9) to the calendar.
