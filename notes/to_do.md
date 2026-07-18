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
