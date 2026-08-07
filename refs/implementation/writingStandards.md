# Technical Writing Discipline

Use this standard for durable technical prose written by agents or humans. It applies to project
documentation, READMEs, handoffs, pull-request descriptions, release notes, comments, procedures,
and user-facing error messages.

## Core principle

Use a positive writing system instead of a growing list of banned words. A banned-word list treats
visible symptoms but does not prevent vague claims, overloaded sentences, passive constructions, or
empty conclusions.

A writing system must state what good prose does:

- Names each thing consistently.
- Identifies the actor when the actor is known.
- Uses direct verbs for actions.
- Keeps one primary idea in each sentence.
- States conditions before the action they control.
- Connects claims to concrete behavior, evidence, or consequences.

Word bans may support this system, but they are not the system.

## Default technical prose

### Use precise and consistent terms

- Choose one name for each concept and keep that name throughout the document.
- Preserve exact technical nouns when a simpler word would change the meaning.
- Do not rename the same component for variety.
- Keep commands, code, identifiers, API fields, and quoted interface text exact.
- Use American spelling unless the project records another convention.

### Make actions direct

- Prefer active voice when the actor is known.
- Use a verb for an action instead of turning the action into an abstract noun.
- Name the result of an action. Do not claim that a change "improves reliability" without saying
  what failure it prevents or detects.
- Remove throat-clearing phrases that delay the useful statement.
- Remove promotional adjectives unless the document provides evidence for the claim.

### Control sentence and paragraph scope

- Put one primary idea in each sentence.
- Split a sentence when it combines separate actions, conditions, explanations, and exceptions.
- Keep one topic in each paragraph.
- Prefer short declarative sentences, but vary sentence length enough to preserve a natural reading
  rhythm.
- Do not shorten prose until it becomes ambiguous, abrupt, or technically incomplete.

### Structure instructions for action

- Use a numbered vertical list for an ordered procedure.
- Put one action in each numbered step.
- Write the action in imperative form.
- Put a condition before its command.
- Separate required actions from explanation and background.
- State the expected result when success would otherwise be unclear.

## Strict operational profile

Use the strict profile for safety instructions, runbooks, setup procedures, recovery steps, and error
messages. These texts must optimize for correct action under pressure.

- Limit an instruction sentence to 20 words when practical.
- Limit a descriptive sentence to 25 words when practical.
- Use no more than six sentences in one paragraph.
- Avoid contractions and semicolons.
- Use one instruction in each sentence.
- Tell the reader what happened, what limit or condition applied, and what action to take next.

Treat the word limits as review triggers, not as permission to remove necessary facts. A longer
sentence is acceptable when splitting it would distort a technical term or safety condition.

## General documentation profile

Use a less restrictive profile for architecture notes, design rationale, product documentation, and
other explanatory prose. Keep the rules for consistent terms, direct verbs, focused sentences, and
focused paragraphs. Allow a broader vocabulary when it improves precision or preserves a useful
voice.

Do not apply this standard mechanically to marketing copy, fiction, essays, dialogue, or other work
whose purpose depends on a distinct voice. Do not rewrite code or identifiers to satisfy prose rules.

## Substance before style

Clear form cannot make an unsupported statement true. Before polishing prose:

1. Confirm the factual claim.
2. Identify the intended reader and the action or decision the text supports.
3. Remove claims that lack evidence or operational meaning.
4. Preserve uncertainty, tradeoffs, and exceptions that affect the reader.
5. Ask a human to review terminology, judgment, or risk that a mechanical rule cannot resolve.

The final review must test meaning as well as form. A document can be concise and still be wrong,
incomplete, or unhelpful.

## Review checklist

- Does each concept have one consistent name?
- Does each sentence have one primary purpose?
- Does active voice identify the actor where useful?
- Does each action use a direct verb?
- Does every strong claim identify evidence, behavior, or consequence?
- Do procedures put conditions before commands and one action in each step?
- Does the text preserve necessary technical detail and uncertainty?
- Did a human review any judgment that rules alone cannot settle?

## Source and limits

This standard adapts the systems approach in
[`The cure for AI slop is a 1986 aircraft manual`](https://github.com/woosal1337/blog/tree/main/videos/ep01-the-cure-for-ai-slop),
which applies ideas from ASD-STE100 Simplified Technical English to model-generated technical prose.

The source reports directional results from six writing tasks and two model families. Its writing
system reduced heuristic violations by 50 percent or more in those tests, while isolated word bans
produced inconsistent results. The sample is small, the score is heuristic, and the method cannot
judge whether prose is factually sound. Use the evidence as support for a review discipline, not as
proof that one style fits every document.

This standard is not a certified ASD-STE100 profile. Consult the official standard when a project
requires formal Simplified Technical English compliance.
