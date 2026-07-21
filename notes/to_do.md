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
