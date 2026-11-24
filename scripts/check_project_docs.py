"""Validate tracked documentation and the required integration languages."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from string import Formatter
from urllib.parse import unquote, urlsplit

INTEGRATION = Path("custom_components/nationaal_energie_dashboard")
LINK = re.compile(r"\]\(\s*(?:<([^>]+)>|([^\s)]+))")
REFERENCE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|([^\s]+))")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+).*?\1")


def _tracked_files(root: Path) -> set[Path]:
    """Return repository-relative Git index paths, not local untracked files."""
    git = shutil.which("git")
    if git is None:
        raise ValueError("Git is required to validate tracked documentation")
    result = subprocess.run(  # noqa: S603 - fixed Git command and arguments.
        [git, "ls-files", "-z"], cwd=root, check=True, capture_output=True
    )
    return {Path(name) for name in result.stdout.decode("utf-8").split("\0") if name}


def _markdown_links(content: str) -> list[tuple[int, str]]:
    """Extract inline and reference-definition links outside code spans/fences."""
    links: list[tuple[int, str]] = []
    fence = ""
    for number, line in enumerate(content.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            marker = match[1]
            if not fence:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = ""
            continue
        if fence:
            continue
        text = INLINE_CODE.sub("", line)
        for pattern in (LINK, REFERENCE):
            links.extend(
                (number, item[1] or item[2]) for item in pattern.finditer(text)
            )
    return links


def _check_links(root: Path, tracked: set[Path]) -> list[str]:
    """Check repository-local link destinations, excluding fragments and URLs."""
    targets = tracked | {parent for path in tracked for parent in path.parents}
    errors: list[str] = []
    for path in sorted(tracked):
        if path.suffix.lower() != ".md":
            continue
        for number, link in _markdown_links((root / path).read_text(encoding="utf-8")):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            relative = Path(unquote(parsed.path))
            target = root / path.parent / relative
            try:
                resolved = target.resolve().relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path}:{number}: link leaves repository: {link}")
                continue
            if resolved not in targets or not target.exists():
                errors.append(f"{path}:{number}: missing tracked link target: {link}")
    return errors


def _check_document_pairs(tracked: set[Path]) -> list[str]:
    """Require both README languages and paired user-guide paths."""
    errors = [
        f"Missing required user documentation: {name}"
        for name in (Path("README.md"), Path("README.en.md"))
        if name not in tracked
    ]
    for language, other in (("en", "nl"), ("nl", "en")):
        directory = Path("docs/user") / language
        for path in sorted(tracked):
            if path.is_relative_to(directory) and path.suffix == ".md":
                counterpart = Path("docs/user") / other / path.relative_to(directory)
                if counterpart not in tracked:
                    errors.append(f"{path}: missing counterpart {counterpart}")
    return errors


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate JSON keys instead of silently overwriting them."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate translation key: {key}")
        result[key] = value
    return result


def _placeholders(text: str) -> tuple[str, ...]:
    """Return sorted placeholder names, preserving their multiplicities."""
    names: list[str] = []
    for _, name, spec, conversion in Formatter().parse(text):
        if name is not None:
            if not name.isidentifier() or spec or conversion:
                raise ValueError(f"Unsupported translation placeholder: {name}")
            names.append(name)
    return tuple(sorted(names))


def _flatten(
    value: object, prefix: tuple[str, ...]
) -> dict[tuple[str, ...], tuple[str, ...]]:
    """Flatten nonempty translation strings to their placeholder signatures."""
    if isinstance(value, dict) and value:
        result: dict[tuple[str, ...], tuple[str, ...]] = {}
        for key, item in value.items():
            result.update(_flatten(item, (*prefix, key)))
        return result
    if not prefix or not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected nonempty translation at {'.'.join(prefix)}")
    if "[%key:" in value:
        raise ValueError(f"Unresolved Core translation reference at {'.'.join(prefix)}")
    return {prefix: _placeholders(value)}


def _read_translation(path: Path) -> dict[tuple[str, ...], tuple[str, ...]]:
    """Read a translation file and validate its nested strings."""
    content = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
    )
    return _flatten(content, ())


def _check_translations(root: Path, tracked: set[Path]) -> list[str]:
    """Require complete NL/EN pairs when a manifest or translation exists."""
    directory = INTEGRATION / "translations"
    english = directory / "en.json"
    dutch = directory / "nl.json"
    errors: list[str] = []
    if INTEGRATION / "strings.json" in tracked:
        errors.append("Custom integrations must ship translations, not strings.json")
    if INTEGRATION / "manifest.json" not in tracked and not any(
        path.parent == directory and path.suffix == ".json" for path in tracked
    ):
        print("Translation parity not evaluated: no manifest or translations yet.")
        return errors
    for path in (english, dutch):
        if path not in tracked:
            errors.append(f"Missing required translation: {path}")
    if errors:
        return errors
    try:
        en = _read_translation(root / english)
        nl = _read_translation(root / dutch)
    except ValueError as error:
        return [f"Invalid translations: {error}"]
    for key in sorted(en.keys() ^ nl.keys()):
        errors.append(f"Translation key differs: {'.'.join(key)}")
    for key in sorted(en.keys() & nl.keys()):
        if en[key] != nl[key]:
            errors.append(f"Translation placeholders differ: {'.'.join(key)}")
    return errors


def validate(root: Path, tracked: set[Path]) -> list[str]:
    """Return validation errors without modifying files or contacting services."""
    return (
        _check_links(root, tracked)
        + _check_document_pairs(tracked)
        + _check_translations(root, tracked)
    )


def main() -> int:
    """Run the repository checks and return a nonzero status on failure."""
    root = Path(__file__).resolve().parents[1]
    try:
        errors = validate(root, _tracked_files(root))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Documentation validation failed: {error}", file=sys.stderr)
        return 1
    for message in errors:
        print(message, file=sys.stderr)
    if errors:
        return 1
    print("Tracked documentation links and language requirements passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
