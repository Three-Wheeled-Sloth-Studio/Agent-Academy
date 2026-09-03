---
type: Framework Guide
title: Refs Initialization Guide
description: Initialize and maintain the Agent Academy project-memory harness and its OKF discovery surface.
status: stable
tags: [agent-academy, project-memory, okf]
---
# Refs Initialization Guide

This folder is a reusable project-memory harness for coding agents and human collaborators. It is intentionally generic until copied into a real project.

The `refs/` directory is also an Open Knowledge Format (OKF) v0.2 bundle. Agent Academy keeps deterministic YAML state where exact schemas and machine behavior matter, while Markdown knowledge documents use OKF frontmatter and generated `index.md` files provide portable discovery.

## Setup Workflow

1. Copy this `refs/` folder into the target project root.
2. Read `refs/templatePolicy.yaml` to identify required bootstrap files and allowed template placeholders.
3. Replace `TEMPLATE_TODO` and `TEMPLATE_TODO_DATE` in required bootstrap files with project facts.
4. Regenerate the OKF discovery indexes:

   ```powershell
   python refs/tools/generate_okf_indexes.py
   ```

5. Run validation from the project root:

   ```powershell
   python refs/tools/validate_refs.py --mode initialized
   ```

6. Keep durable project knowledge in `refs/` instead of only in chat.
7. Do not store secrets, API keys, tokens, passwords, or machine-only credentials in `refs/`.

## Required Bootstrap Files

Fill these first after copying the harness:

- `refs/project.yaml`: project identity, purpose, stack summary, source-of-truth links.
- `refs/agents.yaml`: instructions agents must follow before editing the project.
- `refs/planning/roadmap.yaml`: current direction and sequence.
- `refs/planning/todos.yaml`: durable task list.
- `refs/architecture/overview.md`: how the system is shaped.
- `refs/implementation/fileMap.yaml`: where important code lives.
- `refs/handoffs/currentHandoff.md`: current state and next-agent context.
- `refs/testing/validationCommands.yaml`: commands agents should run before finishing work.

## OKF Compatibility

- `refs/okfProfile.yaml` pins the supported OKF version and defines where Agent Academy is intentionally stricter or richer.
- Every non-reserved Markdown file under `refs/` is an OKF concept and must retain a non-empty `type` in YAML frontmatter.
- `index.md` files are deterministic generated discovery artifacts. Commit them, but do not hand-edit them.
- Structured YAML remains the authoritative representation for deterministic Agent Academy state.
- Passing tests, Git history, or refs validation does not by itself make a concept `verified` in OKF terms.
- See `refs/implementation/okfCompatibility.md` for the authority boundary and `refs/operations/okfMigration.md` for adoption guidance.

## Template Placeholders

Use only these sentinel placeholders in the blank harness:

- `TEMPLATE_TODO`: value intentionally left blank for the destination project.
- `TEMPLATE_TODO_DATE`: date intentionally left blank for the destination project.

Use `refs/fileGuide.yaml` for file-by-file guidance and `refs/MAINTENANCE.md` for framework maintenance.
