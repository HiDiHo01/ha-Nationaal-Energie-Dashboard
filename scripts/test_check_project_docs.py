"""Regression tests for repository documentation checks."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_project_docs import INTEGRATION, validate


class DocumentationTests(unittest.TestCase):
    """Exercise documentation and translation validation with temporary files."""

    def setUp(self) -> None:
        """Create a repository-shaped fixture with both required README files."""
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.tracked: set[Path] = set()
        self.write_file("README.md", "[English](README.en.md)\n")
        self.write_file("README.en.md", "[Nederlands](README.md)\n")

    def write_file(self, name: str, content: str) -> None:
        """Write and register a fixture file."""
        path = Path(name)
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        self.tracked.add(path)

    def translations(self, english: str, dutch: str) -> None:
        """Register two translation fixtures with arbitrary JSON contents."""
        self.write_file(str(INTEGRATION / "translations/en.json"), english)
        self.write_file(str(INTEGRATION / "translations/nl.json"), dutch)

    def test_foundation(self) -> None:
        """Allow a foundation without placeholder translations."""
        self.assertEqual(validate(self.root, self.tracked), [])

    def test_missing_link(self) -> None:
        """Reject a local link to a missing file."""
        self.write_file("README.md", "[Missing](missing.md)\n")
        self.assertTrue(validate(self.root, self.tracked))

    def test_untracked_link(self) -> None:
        """Reject a local link to an untracked file."""
        self.write_file("README.md", "[Local](local.md)\n")
        self.write_file("local.md", "Local\n")
        self.tracked.remove(Path("local.md"))
        self.assertTrue(validate(self.root, self.tracked))

    def test_code_and_external_links(self) -> None:
        """Ignore link examples and destinations outside the link-check scope."""
        self.write_file(
            "README.md",
            "```md\n[x](missing.md)\n```\n`[x](missing.md)`\n"
            "[External](https://example.org/page)\n[Section](#section)\n",
        )
        self.assertEqual(validate(self.root, self.tracked), [])

    def test_reference_link(self) -> None:
        """Validate reference-style link destinations."""
        self.write_file("README.md", "[Guide][guide]\n\n[guide]: missing.md\n")
        self.assertTrue(validate(self.root, self.tracked))

    def test_document_pair(self) -> None:
        """Require a counterpart for each user-guide document."""
        self.write_file("docs/user/en/setup.md", "Setup\n")
        self.assertTrue(validate(self.root, self.tracked))
        self.write_file("docs/user/nl/setup.md", "Installatie\n")
        self.assertEqual(validate(self.root, self.tracked), [])

    def test_missing_readme(self) -> None:
        """Require the English README even when no link points to it."""
        self.write_file("README.md", "Dutch README\n")
        self.tracked.remove(Path("README.en.md"))
        self.assertTrue(validate(self.root, self.tracked))

    def test_manifest_requires_translations(self) -> None:
        """Require both translation files once the manifest is introduced."""
        self.write_file(str(INTEGRATION / "manifest.json"), "{}")
        self.assertEqual(len(validate(self.root, self.tracked)), 2)

    def test_translation_pair(self) -> None:
        """Accept matching nested translation keys and reordered placeholders."""
        self.translations(
            json.dumps({"config": {"title": "{name} at {time}"}}),
            json.dumps({"config": {"title": "Om {time}: {name}"}}),
        )
        self.assertEqual(validate(self.root, self.tracked), [])

    def test_invalid_translations(self) -> None:
        """Reject absent keys, mismatched placeholders and invalid JSON strings."""
        for dutch in (
            '{"other": "Naam {name}"}',
            '{"title": "Naam {device}"}',
            '{"title": "Naam {name} {name}"}',
            '{"title": " "}',
            '{"title": 42}',
            '{"title": "[%key:common::name%]"}',
            '{"title": "Naam {name", "title": "Naam {name}"}',
            '{"title": "Naam {name"}',
            "{}",
            "invalid JSON",
        ):
            with self.subTest(dutch=dutch):
                self.translations('{"title": "Name {name}"}', dutch)
                self.assertTrue(validate(self.root, self.tracked))

    def test_core_strings(self) -> None:
        """Reject Core-only strings.json in the custom integration."""
        self.write_file(str(INTEGRATION / "strings.json"), "{}")
        self.assertTrue(validate(self.root, self.tracked))
