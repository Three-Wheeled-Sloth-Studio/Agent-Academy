# Agent Academy Refs Harness

This repository contains a reusable `refs/` harness for project memory. It is intentionally project-neutral: copy it into another repository, then fill it with durable facts, decisions, workflows, architecture notes, validation commands, and handoff context for that project.

The harness is designed for human collaborators and coding agents. It gives agents a predictable reading order and gives teams a durable place to store project knowledge that should not live only in chat.

## Use

1. Copy the `refs/` directory into the target project root.
2. Read `refs/README.md`.
3. Fill the required bootstrap files listed in `refs/templatePolicy.yaml`.
4. Run the validation command in `refs/testing/validationCommands.yaml`.
5. Keep project facts current as implementation work changes.

Do not store secrets, API keys, passwords, tokens, or machine-only credentials in `refs/`.

## Framework Maintenance

Framework authors should keep file paths stable because the `refs/` layout is the public interface for copied projects. See `refs/MAINTENANCE.md` before adding files, changing schemas, or introducing migration steps.
