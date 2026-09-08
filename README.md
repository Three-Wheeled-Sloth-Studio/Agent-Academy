# Agent Academy Refs Harness

This repository contains a reusable `refs/` harness for project memory. It is intentionally project-neutral: copy it into another repository, then fill it with durable facts, decisions, workflows, architecture notes, validation commands, and handoff context for that project.

The harness is designed for human collaborators and coding agents. It gives agents a predictable memory layout plus a bounded re-entry workflow so routine context resets do not require rereading the entire project history.

Agent Academy is compatible with Open Knowledge Format (OKF) v0.2 while retaining stricter deterministic YAML where exact state and validation matter. The compatibility profile is pinned in `refs/okfProfile.yaml` to the canonical `GoogleCloudPlatform/open-knowledge-format` specification.

## Use

1. Copy the `refs/` directory into the target project root.
2. Read `refs/README.md`.
3. Fill the required bootstrap files listed in `refs/templatePolicy.yaml`.
4. Regenerate OKF discovery indexes with `python refs/tools/generate_okf_indexes.py`.
5. Run the validation commands in `refs/testing/validationCommands.yaml`.
6. For routine coding-agent continuation, begin with `python refs/tools/generate_agent_context.py --focus "<task>"` and load deeper context progressively only as needed.
7. Keep project facts current as implementation work changes.

Generated re-entry packets are derived scratch context, not project state. Do not commit them as an alternate source of truth.

Do not store secrets, API keys, passwords, tokens, or machine-only credentials in `refs/`.

## Framework Maintenance

Framework authors should keep file paths stable because the `refs/` layout is the public interface for copied projects. See `refs/MAINTENANCE.md` before adding files, changing schemas, upgrading the OKF profile, or introducing migration steps.
