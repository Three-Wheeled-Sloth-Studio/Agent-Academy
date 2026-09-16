# Agent Academy Refs Harness

This repository contains a reusable `refs/` harness for project memory. It is intentionally project-neutral: copy it into another repository, then fill it with durable facts, decisions, workflows, architecture notes, validation commands, and handoff context for that project.

The harness is designed for human collaborators and coding agents. It gives agents a predictable memory layout plus a bounded re-entry workflow so routine context resets do not require rereading the entire project history. It also includes a deterministic generated source catalog so agents can discover relevant files and callable symbols without first reading the repository broadly.

Agent Academy is compatible with Open Knowledge Format (OKF) v0.2 while retaining stricter deterministic YAML where exact state and validation matter. The compatibility profile is pinned in `refs/okfProfile.yaml` to the canonical `GoogleCloudPlatform/open-knowledge-format` specification.

## Use

1. Copy the `refs/` directory into the target project root.
2. Read `refs/README.md`.
3. Fill the required bootstrap files listed in `refs/templatePolicy.yaml`.
4. Generate the source catalog with `python refs/tools/generate_source_catalog.py`.
5. Regenerate OKF discovery indexes with `python refs/tools/generate_okf_indexes.py`.
6. Run the validation commands in `refs/testing/validationCommands.yaml`.
7. For routine coding-agent continuation, begin with `python refs/tools/generate_agent_context.py --focus "<task>"`. The generator refreshes source discovery first, then load deeper context progressively only as needed.
8. Keep project facts current as implementation work changes.

Generated re-entry packets are derived scratch context, not project state. The generated source catalog is committed derived discovery data, not an alternate source of runtime truth. Do not hand-edit catalog output.

Do not store secrets, API keys, passwords, tokens, or machine-only credentials in `refs/`.

## Framework Maintenance

Framework authors should keep file paths stable because the `refs/` layout is the public interface for copied projects. See `refs/MAINTENANCE.md` before adding files, changing schemas, upgrading the OKF profile, or introducing migration steps.
