---
summary: Interface copy — voice and tone, button labels, link text, error messages, empty states, placeholders, settings labels, capitalization, and copy that survives translation
read_when: writing or reviewing any user-facing text — button labels, error messages, empty states, settings, onboarding copy, confirmation dialogs, toasts, or microcopy anywhere
---

# Interface Writing

Copy is design. A page with a perfect type scale and a button labeled "OK!" is not finished. Clear and brief beats clever; consistent beats varied.

The best error message is the interaction redesigned so the error cannot happen.

How copy *renders* — capitalization through `text-transform`, truncation, smart punctuation — is in `typography-and-spacing.md`. How errors are *announced* is in `interface-quality.md`.

---

## Read the Voice Before Writing

Before writing or changing any copy, read what is already there. Note the product's terminology, its conventions, and any style guide.

A deliberate brand voice is not a defect. Raise a departure from plain language only when it creates inconsistency, ambiguity, translation risk, or a tone the stakes cannot carry.

## One Voice, Flexible Tone

The product has one voice, and its existing copy establishes it. A local edit does not get to invent a new one. Keep terms consistent: if it is "Archive" in the menu, it is not "Move to storage" in the toast.

Tone flexes with the stakes.

| Context | Tone |
|---|---|
| Success, onboarding, empty states | Warm, can be light |
| Routine actions, settings | Neutral, minimal |
| Errors, destructive confirmations | Calm, plain, zero playfulness |
| Data loss, security | Serious and explicit |

## Address the Reader Directly

Write "you", not "the user". In errors, avoid "we" — it invites ambiguity and reads as deflection. "Unable to load content" beats "We're having trouble loading this content."

Use possessives sparingly: "Favorites" beats "Your Favorites". Hold one perspective through a whole flow.

## Plain Words Over Clever Ones

Choose words a tired reader gets on the first pass, and delete every word doing no work. No idioms, no colloquialisms, no humor that will not translate.

- Skip unnecessary gender: "Subscribers can post recipes", not "each subscriber can post his or her recipes".
- Match the input device: "tap" on touch, "click" with a pointer, "select" when it could be either.
- **Never assemble a sentence from fragments around a variable.** `"You have " + n + " new messages"` breaks in every language whose word order differs. Use a full templated string with real pluralization.

---

## Buttons Start With a Verb

A button label names the action: "Send", "Save draft", "Delete project". Never "OK!", never "Let's go!", and never a bare "Yes" or "No" on a consequential action.

**A confirmation button repeats the consequence**, so the dialog is answerable without reading the body. "Delete this project?" offers *Delete project* and *Cancel*.

A multi-step flow uses one vocabulary throughout: one word to enter, one to advance, one to finish. Alternating between "Continue" and "Next" makes people wonder whether the two buttons do different things.

## Links Describe Their Destination

Link text has to make sense out of context, because screen-reader users navigate by a list of the page's links. Write "Read the billing docs", not "Click here" — which fails this and the device-verb rule at once.

A bare "Learn more" breaks down the moment two appear on one page. Suffix each: "Learn more about exports".

## One Capitalization Policy

Pick title case or sentence case per element type, then apply it to every instance of that type. Sentence case is the safer default: calmer, no per-word rules to remember, and it localizes cleanly. "Save Changes" sitting beside "Discard changes" reads as sloppiness.

## Settings Describe the On State

Label a toggle for what happens when it is on. "Send read receipts" lets someone infer the off state. The negative — "Don't send read receipts" — turns the toggle into a double negative.

Link straight to a referenced setting rather than describing the path to it.

---

## Errors Say How to Fix, Beside Where It Broke

An error is an instruction, and it belongs next to the field that failed.

| Instead of | Write |
|---|---|
| That password is too short | Choose a password with at least 8 characters |
| Invalid name | Use only letters for your name |
| Oops! Something went wrong. | Unable to save. Check your connection and try again. |

No blame, no "oops", no exclamation marks. Phrase hints positively — "Use only letters", not "Don't use numbers or symbols" — and show them *before* the mistake rather than after.

When the same error keeps firing, redesign the interaction instead of rewording the message.

## Empty States Point Forward

An empty state says what this place is, how to fill it, and offers one clear next action. "No results." is a shrug.

A search or filter empty state names the query and offers an exit: "No results for 'quarterly'. Clear filters."

**Never park persistent information in an empty state.** It disappears the moment content exists, taking the explanation with it.

## Placeholders Are Examples, Not Labels

A placeholder shows the expected format. It vanishes on input, so it is never the only label — every field keeps a visible one.

---

## Before You Finish

| Mistake | Fix |
|---|---|
| "OK" / "Yes" on a consequential action | Name the consequence: "Delete project" |
| Two "Learn more" links on one page | Suffix each with its destination |
| "Save Changes" beside "Discard changes" | One capitalization policy per element type |
| A toggle labeled with a negative | Label the on state |
| An error stating the problem but not the fix | Say what to do about it |
| A string built by concatenating around a variable | One templated string with pluralization |
| "The user" in instructional copy | "You" |
| Error copy using "we" | Impersonal: "Unable to save" |
| Persistent guidance living in an empty state | Move it somewhere it survives content existing |
| The same term rendered two ways across screens | Pick one and use it everywhere |
