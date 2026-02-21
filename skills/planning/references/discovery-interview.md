# Discovery Interview Guide

## Table of Contents

- [Interview Mindset](#interview-mindset)
- [Question Categories](#question-categories)
- [Strong vs Weak Questions](#strong-vs-weak-questions)
- [When to Stop](#when-to-stop)
- [Handling Uncertainty](#handling-uncertainty)

## Interview Mindset

The discovery interview is not a requirements checklist.
It's a conversation designed to surface things the user hasn't thought about yet.

**Your role**: Think like a senior engineer and product thinker paired together.
You're not just gathering specs — you're stress-testing the idea, identifying gaps, and offering options the user may not know exist.

**Key principles:**

- **Lead with options, not open-ended questions.** Instead of "How should we handle errors?", say "For error handling, I see three approaches: (A) inline validation with field-level errors, (B) toast notifications for transient errors, (C) a combination. I'd recommend C because... What do you think?"
- **State assumptions explicitly.** "I'm assuming this needs to work on mobile. If that's wrong, it changes the approach significantly."
- **Flag non-obvious implications.** "If we go with approach A, that means we'll also need to handle X — are you okay with that scope?"
- **Challenge when appropriate.** If the user's request has a simpler or better solution, say so. "You asked for X, but based on what I see in the codebase, Y might solve the same problem with less complexity. Here's why..."

## Question Categories

Not every category applies to every feature. Use judgment.

### Problem & Goals

Surface the real problem, not just the requested solution.

- What user pain point or business goal does this solve?
- What does success look like? How will you measure it?
- Is there a deadline or dependency driving this?
- What happens if we don't build this?

### Behavior & Interaction

For user-facing features — how should it look and feel?

- What's the happy path? Walk through the user journey step by step
- What should happen on error? (specific scenarios, not generic "show an error")
- Are there loading states, empty states, or progressive disclosure needs?
- How should this interact with existing features? (navigation, data flow, state)
- Are there accessibility requirements beyond baseline? (screen readers, keyboard nav, color contrast)

### Edge Cases & Failure Modes

The questions users rarely think about.

- What happens with extreme inputs? (empty, very long, special characters, unicode)
- What if the network is slow or unavailable?
- What about concurrent users or race conditions?
- What if upstream data is missing, malformed, or stale?
- Are there permission or role-based visibility concerns?
- What if a user is midway through and navigates away?

### Technical Tradeoffs

When multiple approaches exist, surface the decision.

- Present each approach with concrete pros/cons
- Include your recommendation with reasoning
- Flag irreversible decisions — choices that are hard to change later
- Note performance implications if relevant (bundle size, API calls, database queries)
- Consider whether this creates tech debt or resolves it

### Scale & Performance

Only ask when relevant — don't ask about scale for an internal admin tool.

- How much data are we dealing with? (rows, records, file sizes)
- How many concurrent users?
- Are there latency requirements? (real-time, near-real-time, background)
- Does this need pagination, virtualization, or lazy loading?

### Security & Privacy

Especially for anything touching user data, authentication, or external APIs.

- What data is being created, read, updated, or deleted?
- Who should have access? Are there role-based restrictions?
- Is any data sensitive (PII, credentials, financial)?
- Are there compliance requirements (GDPR, SOC2, HIPAA)?

### Migration & Compatibility

For changes that affect existing functionality.

- Does this change break anything for current users?
- Is there existing data that needs migrating?
- Do we need a feature flag or gradual rollout?
- Are there other teams or systems that depend on what we're changing?

## Strong vs Weak Questions

### Weak (Don't Ask These)

| Question | Why It's Weak |
|----------|---------------|
| "What tech stack are you using?" | Read the codebase |
| "Do you want it to look good?" | Obviously yes |
| "Should we handle errors?" | Obviously yes — ask *how* |
| "What's the app about?" | Read the README and codebase |
| "Do you want tests?" | Assume yes — ask about *what* to test if unclear |
| "How should I structure the code?" | That's your job |

### Strong (Ask These)

| Question | Why It's Strong |
|----------|-----------------|
| "For the date picker, I see three options: native HTML date input (simple but inconsistent), a library like react-datepicker (consistent but adds bundle size), or your existing DateField component in `components/forms/`. I'd recommend extending DateField since it already matches your design system. Sound right?" | Concrete options with tradeoffs, recommendation, and codebase awareness |
| "This feature touches the same user data as the settings page. Should they share a data source, or is it okay to have separate queries? Shared means instant consistency; separate means simpler code but potential staleness." | Surfaces a real architectural decision with concrete tradeoffs |
| "I notice your auth middleware doesn't currently handle refresh tokens. This feature will need authenticated API calls — should we add refresh token handling now, or scope this to only work within the current session?" | Flags a dependency the user may not have considered |
| "The form has 8 fields. Should all show at once, or would a multi-step wizard reduce friction? Based on what I see in competitor X, similar forms typically use 2-3 steps." | Brings external research into the question |

## When to Stop

Stop the interview when:

- All meaningful ambiguities have been resolved
- The user says they have nothing more to add
- Further questions would be about implementation details you can decide yourself
- You're asking about edge cases so unlikely they're not worth discussing upfront

**Don't stop just because you've asked "enough" questions.**
If there are genuine open questions, keep going.
If the feature is simple and everything is clear after 2-3 questions, stop there.

Match interview depth to feature complexity.

## Handling Uncertainty

When the user doesn't know the answer:

- Offer your recommendation with reasoning
- State it as an assumption that can be revised
- "Let's go with approach A for now — it's the simplest to change later if we need to switch."
- Document the assumption in the plan so it's visible

When you don't know the answer:

- Say so honestly
- Suggest research: "I'm not sure about the browser compatibility here — I'll research this in the next phase"
- Don't guess at constraints you can verify
