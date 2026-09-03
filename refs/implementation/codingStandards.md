---
type: Coding Standards
title: Coding Standards
description: Project-specific coding standards plus mandatory cross-platform path-safety rules.
status: draft
tags: [implementation, coding-standards]
---
# Coding Standards

TEMPLATE_TODO: Define project-specific coding style, safety rules, review expectations, and quality bar.

## Mandatory cross-platform path safety

These rules apply to every initialized project, regardless of language or build system:

- No two tracked repository paths may differ only by letter casing. A pair that works on a case-sensitive Linux checkout can become one ambiguous path on Windows or a default macOS checkout.
- Imports, references, generated manifests, and tooling configuration must match the tracked path's casing exactly.
- Do not distinguish a component and helper only by capitalization. Use semantic filenames such as `GeographicAtlasContextMap.tsx` and `geographicAtlasContextGeometry.ts`, not `GeographicAtlasContextMap.tsx` and `geographicAtlasContextMap.ts`.
- Every project must implement an automated case-collision guard using the Git index as its source of truth. The guard must read `git ls-files`, normalize separators, case-fold each complete path, and fail if distinct tracked paths produce the same folded key.
- A filesystem-only scan is insufficient because case-insensitive filesystems may already have collapsed the conflicting paths.
- Wire the guard into the repository's ordinary validation command. Where the project has typecheck or build scripts, run it before both.
- Test the guard with at least one synthetic collision pair and one non-collision pair.
- Perform case-only renames through a temporary intermediate filename, for example `git mv OldName.ts temporary-name.ts` followed by `git mv temporary-name.ts NewName.ts`. Verify `git status` and the final diff before committing.

A change that introduces or preserves a case-folded path collision is not ready to merge, even when tests pass on Linux.
