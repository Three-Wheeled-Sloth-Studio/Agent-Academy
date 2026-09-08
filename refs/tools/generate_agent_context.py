#!/usr/bin/env python3
"""Generate a compact, derived re-entry packet for coding-agent sessions."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python -m pip install pyyaml") from exc

DEFAULT_MAX_CHARS = 8_000
DEFAULT_MAX_ITEMS = 8
DEFAULT_MAX_HANDOFF_SNIPPETS = 6
DEFAULT_MAX_CHANGED_PATHS = 12

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_STOPWORDS = {
    "add",
    "agent",
    "and",
    "change",
    "code",
    "current",
    "for",
    "from",
    "into",
    "issue",
    "make",
    "project",
    "the",
    "this",
    "tool",
    "use",
    "with",
    "work",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_git(repo_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _ref_exists(repo_root: Path, ref: str) -> bool:
    return _run_git(repo_root, "rev-parse", "--verify", "--quiet", ref) is not None


def _resolve_base_ref(repo_root: Path, requested: str | None, branch: str) -> str | None:
    candidates: list[str] = []
    if requested:
        candidates.append(requested)
    candidates.extend(["dev", "main", "master", "origin/dev", "origin/main", "origin/master"])
    for candidate in candidates:
        if candidate == branch or _ref_exists(repo_root, candidate):
            return candidate
    return None


def collect_git_context(repo_root: Path, *, base_ref: str | None = None) -> dict[str, Any]:
    branch = _run_git(repo_root, "branch", "--show-current") or "detached"
    head = _run_git(repo_root, "rev-parse", "--short=12", "HEAD") or "unknown"
    resolved_base = _resolve_base_ref(repo_root, base_ref, branch)
    status = _run_git(repo_root, "status", "--short") or ""
    dirty_paths = [
        line[3:].strip()
        for line in status.splitlines()
        if len(line) > 3 and line[3:].strip()
    ]
    changed_paths: list[str] = []
    if resolved_base and branch != resolved_base:
        changed = _run_git(repo_root, "diff", "--name-only", f"{resolved_base}...HEAD") or ""
        changed_paths = [line.strip() for line in changed.splitlines() if line.strip()]
    return {
        "branch": branch,
        "head": head,
        "base_ref": resolved_base or "unresolved",
        "changed_paths": changed_paths,
        "dirty_paths": dirty_paths,
    }


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _is_placeholder(value: Any) -> bool:
    return "TEMPLATE_TODO" in str(value)


def _clean(value: Any) -> str:
    text = " ".join(str(value or "").split()).strip()
    return "" if _is_placeholder(text) else text


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall(value.casefold())
        if len(token) > 2 and token not in _STOPWORDS and not token.startswith("template")
    }


def _relevance(value: str, focus_tokens: set[str]) -> int:
    return len(_tokens(value) & focus_tokens) if focus_tokens else 0


def _truncate(value: str, limit: int = 320) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _rank_records(
    records: list[tuple[str, str]],
    focus_tokens: set[str],
    limit: int,
) -> list[tuple[str, str]]:
    if not records:
        return []
    ranked = sorted(
        records,
        key=lambda item: (_relevance(f"{item[0]} {item[1]}", focus_tokens), item[0]),
        reverse=True,
    )
    if focus_tokens:
        matched = [
            item
            for item in ranked
            if _relevance(f"{item[0]} {item[1]}", focus_tokens) > 0
        ]
        if matched:
            return matched[:limit]
    return ranked[:limit]


def _accepted_decisions(path: Path, focus_tokens: set[str]) -> list[tuple[str, str]]:
    payload = _read_yaml(path)
    records: list[tuple[str, str]] = []
    for item in payload.get("decisions") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").casefold() != "accepted":
            continue
        decision_id = _clean(item.get("id")) or "decision"
        decision = _clean(item.get("decision"))
        if decision:
            records.append((decision_id, decision))
    return _rank_records(records, focus_tokens, DEFAULT_MAX_ITEMS)


def _active_todos(path: Path, focus_tokens: set[str]) -> list[tuple[str, str]]:
    payload = _read_yaml(path)
    active = {"open", "in_progress", "in-progress", "active", "blocked"}
    records: list[tuple[str, str]] = []
    for item in payload.get("todos") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").casefold() not in active:
            continue
        todo_id = _clean(item.get("id")) or "todo"
        summary = _clean(item.get("summary"))
        area = _clean(item.get("area"))
        detail = " — ".join(part for part in [area, summary] if part)
        if detail:
            records.append((todo_id, detail))
    return _rank_records(records, focus_tokens, DEFAULT_MAX_ITEMS)


def _active_roadmap(path: Path, focus_tokens: set[str]) -> list[tuple[str, str]]:
    payload = _read_yaml(path)
    active = {"planned", "in_progress", "in-progress", "active"}
    records: list[tuple[str, str]] = []
    for item in payload.get("roadmap") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").casefold() not in active:
            continue
        roadmap_id = _clean(item.get("id")) or "roadmap"
        summary = _clean(item.get("summary"))
        horizon = _clean(item.get("horizon"))
        detail = " — ".join(part for part in [horizon, summary] if part)
        if detail:
            records.append((roadmap_id, detail))
    return _rank_records(records, focus_tokens, DEFAULT_MAX_ITEMS)


def _markdown_blocks(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    section = "Overview"
    blocks: list[tuple[str, str]] = []
    paragraph: list[str] = []
    in_frontmatter = False
    in_code = False

    def flush() -> None:
        if not paragraph:
            return
        text = " ".join(item.strip() for item in paragraph if item.strip()).strip()
        paragraph.clear()
        if text and not _is_placeholder(text):
            blocks.append((section, text))

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "---" and not blocks and not paragraph:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if line.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            flush()
            section = heading.group(1)
            continue
        if line.startswith("# "):
            flush()
            continue
        if not line:
            flush()
            continue
        if line.startswith(("- ", "* ")):
            flush()
            text = line[2:].strip()
            if text and not _is_placeholder(text):
                blocks.append((section, text))
            continue
        if re.match(r"^\d+\.\s+", line):
            flush()
            text = re.sub(r"^\d+\.\s+", "", line)
            if text and not _is_placeholder(text):
                blocks.append((section, text))
            continue
        paragraph.append(line)
    flush()
    return blocks


def _handoff_snippets(path: Path, focus_tokens: set[str]) -> list[tuple[str, str]]:
    excluded = {"Read before implementation", "Validation", "Validation boundary"}
    blocks = [item for item in _markdown_blocks(path) if item[0] not in excluded]
    if not blocks:
        return []
    priority_words = {
        "next": 5,
        "gap": 5,
        "current": 4,
        "follow": 4,
        "constraint": 3,
        "accepted": 3,
        "landed": 2,
        "summary": 1,
    }

    def score(item: tuple[str, str]) -> int:
        section, text = item
        base = _relevance(f"{section} {text}", focus_tokens) * 10
        folded = section.casefold()
        return base + sum(weight for word, weight in priority_words.items() if word in folded)

    ranked = sorted(
        enumerate(blocks),
        key=lambda pair: (score(pair[1]), -pair[0]),
        reverse=True,
    )
    if focus_tokens:
        matched = [
            item
            for _index, item in ranked
            if _relevance(f"{item[0]} {item[1]}", focus_tokens) > 0
        ]
        if matched:
            return matched[:DEFAULT_MAX_HANDOFF_SNIPPETS]
    return [item for _index, item in ranked[:DEFAULT_MAX_HANDOFF_SNIPPETS]]


def _file_hints(path: Path, focus_tokens: set[str]) -> list[tuple[str, list[str]]]:
    payload = _read_yaml(path)
    hints: list[tuple[int, str, list[str]]] = []

    for item in payload.get("common_tasks") or []:
        if not isinstance(item, dict):
            continue
        label = _clean(item.get("task"))
        paths = [_clean(value) for value in item.get("look_in") or []]
        paths = [value for value in paths if value]
        if label and paths:
            score = _relevance(f"{label} {' '.join(paths)}", focus_tokens)
            hints.append((score, label, paths))

    areas = payload.get("areas") or {}
    if isinstance(areas, dict):
        for area_name, item in areas.items():
            if not isinstance(item, dict):
                continue
            label = _clean(area_name)
            paths: list[str] = []
            for key in ("guidance", "source_roots"):
                values = item.get(key) or []
                if isinstance(values, list):
                    paths.extend(_clean(value) for value in values)
            paths = [value for value in paths if value]
            notes = _clean(item.get("notes"))
            searchable = f"{label} {notes} {' '.join(paths)}"
            if label and (paths or notes):
                hints.append((_relevance(searchable, focus_tokens), label, paths))

    hints.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if focus_tokens and any(score > 0 for score, _label, _paths in hints):
        hints = [item for item in hints if item[0] > 0]
    return [(label, paths) for _score, label, paths in hints[:3]]


def _validation_commands(path: Path) -> list[tuple[str, str]]:
    payload = _read_yaml(path)
    records: list[tuple[str, str]] = []
    for item in payload.get("commands") or []:
        if not isinstance(item, dict):
            continue
        command_id = _clean(item.get("id")) or "validation"
        command = _clean(item.get("command"))
        if command:
            records.append((command_id, command))
    return records[:DEFAULT_MAX_ITEMS]


def _project_identity(path: Path) -> tuple[str, str]:
    payload = _read_yaml(path)
    identity = payload.get("identity") or {}
    name = _clean(identity.get("name")) or "Project"
    phase = _clean(identity.get("current_phase")) or "unspecified"
    return name, phase


def _infer_issue(branch: str) -> int | None:
    match = re.match(r"(?:agent|codex|issue)[/-](\d+)(?:-|$)", branch)
    return int(match.group(1)) if match else None


def build_packet(
    repo_root: Path,
    *,
    focus: str = "",
    issue: int | None = None,
    base_ref: str | None = None,
    git_context: dict[str, Any] | None = None,
) -> str:
    refs = repo_root / "refs"
    git = git_context or collect_git_context(repo_root, base_ref=base_ref)
    focus_tokens = _tokens(focus)
    issue_number = issue or _infer_issue(str(git.get("branch") or ""))
    project_name, phase = _project_identity(refs / "project.yaml")
    decisions = _accepted_decisions(refs / "planning/decisions.yaml", focus_tokens)
    todos = _active_todos(refs / "planning/todos.yaml", focus_tokens)
    roadmap = _active_roadmap(refs / "planning/roadmap.yaml", focus_tokens)
    handoff = _handoff_snippets(refs / "handoffs/currentHandoff.md", focus_tokens)
    file_hints = _file_hints(refs / "implementation/fileMap.yaml", focus_tokens)
    validation = _validation_commands(refs / "testing/validationCommands.yaml")

    lines = [
        f"# {project_name} — Generated Agent Re-entry Context",
        "",
        "> Derived orientation only. Authoritative refs and source remain the source of truth.",
        "",
        "## Session",
        f"- Branch: `{git.get('branch', 'unknown')}`",
        f"- HEAD: `{git.get('head', 'unknown')}`",
        f"- Base ref: `{git.get('base_ref', 'unresolved')}`",
        f"- Current phase: {phase}",
    ]
    if issue_number is not None:
        lines.append(f"- Issue: #{issue_number}")
    if focus.strip():
        lines.append(f"- Focus: {focus.strip()}")

    changed = list(
        dict.fromkeys(
            [
                *(git.get("changed_paths") or []),
                *(git.get("dirty_paths") or []),
            ]
        )
    )
    if changed:
        lines.extend(["", "## Changed paths"])
        for value in changed[:DEFAULT_MAX_CHANGED_PATHS]:
            lines.append(f"- `{value}`")
        if len(changed) > DEFAULT_MAX_CHANGED_PATHS:
            lines.append(f"- … {len(changed) - DEFAULT_MAX_CHANGED_PATHS} more")

    if handoff:
        lines.extend(["", "## Current handoff highlights"])
        for section, text in handoff:
            lines.append(f"- **{section}:** {_truncate(text)}")

    if decisions:
        lines.extend(["", "## Relevant accepted decisions"])
        for decision_id, decision in decisions:
            lines.append(f"- **{decision_id}:** {_truncate(decision)}")

    if todos:
        lines.extend(["", "## Active todos"])
        for todo_id, detail in todos:
            lines.append(f"- **{todo_id}:** {_truncate(detail)}")

    if roadmap:
        lines.extend(["", "## Active roadmap"])
        for roadmap_id, detail in roadmap:
            lines.append(f"- **{roadmap_id}:** {_truncate(detail)}")

    if file_hints:
        lines.extend(["", "## File-map hints"])
        for label, paths in file_hints:
            if paths:
                lines.append(f"- **{label}:** " + ", ".join(f"`{value}`" for value in paths))
            else:
                lines.append(f"- **{label}**")

    if validation:
        lines.extend(["", "## Validation commands"])
        for command_id, command in validation:
            lines.append(f"- `{command_id}` — `{command}`")

    lines.extend(
        [
            "",
            "## Context discipline",
            "- Start here, then load deeper roadmap, architecture, history, or source only when the task requires it.",
            "- Treat accepted decisions as inputs; reopen them only when new runtime/test evidence contradicts them.",
            "- Continue diff-first from the accepted checkpoint instead of reconstructing unchanged repository state.",
            "- Use the file map, targeted searches/ranges, deterministic diagnostics, and tests before broad reads.",
            "- If substantially the same diagnostic/search/transformation is performed twice, make it reusable before doing it a third time.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--focus", default="", help="Short task phrase used to select relevant context.")
    result.add_argument("--issue", type=int, help="Optional issue number to display in the packet.")
    result.add_argument("--base-ref", help="Optional integration/base ref used for changed-path context.")
    result.add_argument("--output", type=Path, help="Optional local scratch file; stdout is the default.")
    result.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    result.add_argument(
        "--check",
        action="store_true",
        help="Validate packet generation and the configured size budget without printing the packet.",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    if args.max_chars < 2_000:
        raise SystemExit("--max-chars must be at least 2000")
    repo_root = _repo_root()
    packet = build_packet(
        repo_root,
        focus=args.focus,
        issue=args.issue,
        base_ref=args.base_ref,
    )
    if len(packet) > args.max_chars:
        raise SystemExit(
            f"Generated packet is {len(packet)} characters; budget is {args.max_chars}. "
            "Tighten the selectors or source material instead of increasing routine reset context."
        )
    if args.check:
        print(f"agent context check ok: {len(packet)} characters")
        return 0
    if args.output is not None:
        output = args.output if args.output.is_absolute() else repo_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(packet, encoding="utf-8")
        print(f"Wrote generated agent context: {output}")
        return 0
    print(packet, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
