# AI Website-Building Service — Master Plan

_Saved 2026-07-23 from Lucas's chat. A service business: use AI website builders to
build/launch sites for paying clients — speed + judgment, not just tool access._

## Status / cross-check notes (Claude, 2026-07-23)
- **Money fit:** strong. Real revenue business, faceless-compatible (you build, no camera).
  See [[user-money-goal]] and [[user-faceless-first]].
- **Sales-gated, not build-gated.** Like Clipfarm, the bottleneck is a first paying client,
  NOT the internal tools. Per the PLAYBOOK Stage 5 rule: don't build the ops layer (Section 6)
  until at least one real lead exists. The intake/proposal generator (#1) is the first tool —
  but only once there's someone to send a proposal to.
- **Tool stack (Section 4) is UNVERIFIED against Lucas's notes.** Only builder mentioned in his
  video notes is GoHighLevel; none of Framer/Durable/10Web/Webflow/Duda appear. Do the live
  web-pricing re-check at commit time, not before.

---

## 1. The Offer
"I build you a professional, launch-ready website in days, not months — powered by AI, refined
by a human." Edge = knowing which tool fits which business, handling the whole pipeline (copy,
structure, SEO, domain, launch), and fixing what AI builders get wrong (generic copy, spacing,
information architecture). Selling speed + judgment.

## 2. Client personas (stress-test the workflow against all four)
- **Maria** — restaurant. Menu/hours/map/photos/ordering link. Low-touch, price-sensitive.
- **Coach Dave** — solo trainer. Booking/contact, testimonials, about story, IG embed. Recurring small updates.
- **Whitfield & Cho** — 3-person law firm. Formal, practice-area pages, bios, trust signals. High polish, higher budget.
- **Priya** — real-estate agent. Frequently-updated listings, lead capture, mobile-first. Most frequent ongoing updates.

## 3. Service tiers
- **Starter** (Coach Dave): 1-page, AI copy edited by you, contact form, 1 revision.
- **Standard** (Maria): multi-page, custom domain, basic SEO, 2 revisions. Most clients land here.
- **Pro** (Whitfield & Cho, Priya): + more pages, CMS for self-serve updates, stronger copy, priority turnaround.
- **Retainer** (add-on): monthly small edits + uptime/domain checks. The real long-term money.
Price after building 2-3 real sites and knowing your time-per-site.

## 4. Tool stack (mid-2026, re-check before committing)
Framer AI (best design, Pro tier) · Durable (fast 1-page, Starter) · 10Web (WordPress/WooCommerce
clone-a-site) · Webflow AI (clean design-system output, Standard/Pro) · Duda (agency white-label,
once volume justifies). Split: Durable/Framer for Starter, Webflow/Framer for Standard/Pro, 10Web
for WordPress/e-comm. Evaluate Duda at volume.

## 5. Client workflow
Lead → Discovery (structured intake → same-day one-page proposal) → Build (right tool per client,
draft from YOUR prompt template not client's raw words, human pass, internal QA) → Launch (domain,
SSL, SEO pass, mobile test, walkthrough) → Retainer (monthly touchpoint + site health check).

## 6. Internal tools to build (solo-operator, keep simple)
1. Intake form + auto-proposal generator (build first — used before first client).
2. Prompt-template library, one per niche (restaurant/coach/legal/real-estate) — your core IP.
3. Client + project tracker (personal CRM: name, tier, stage, dates, notes).
4. Pre-launch QA checklist tool.
5. Retainer reminder system (piggyback Life3000's scheduled-automation approach; ping if a site check breaks).

## 7. Pre-launch QA checklist
Contact info correct+clickable · every link/button goes somewhere real · mobile correct · no
lorem/placeholder · real photos not stock · page titles + meta descriptions filled · forms
deliver submissions · domain + SSL active.

## 8. Build order
1. Intake + proposal generator. 2. One prompt template (niche of first lead) + timed end-to-end run.
3. QA checklist tool. 4. Client/project tracker (once >1 client). 5. Retainer reminders (once first retainer signs).

## 9. Notes
Tools 1-5 are solo-operator utilities — simple over polished. Client sites are built in 3rd-party
AI builders, not custom-coded; Claude Code builds the OPERATIONS layer. Phase 2: a custom-coded
tier for higher-paying clients — keep the tracker flexible for a "custom build" project type later.
