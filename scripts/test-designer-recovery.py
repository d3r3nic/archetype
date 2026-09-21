#!/usr/bin/env python3
"""Structural integration tests for designer recovery.

These tests run the shipped next-step interface and shipped bootstrap/frontend
metadata against synthetic project decisions, inputs, and documented ledger
events. They do not perform design work, render an interface, capture visuals,
or prove owner approval. Visual workflow proof remains a separate gate.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ENGINE = Path(__file__).resolve().parents[1]
NEXT_STEP = ENGINE / "scripts" / "next-step.sh"
RECOVERY = ENGINE / "scripts" / "step-recovery.py"

DIRECTION = "DEC-001"
CONTEXT = "DEC-002"
API = "DEC-003"
NO_SCREEN = "DEC-006"

DESIGN_CHAIN = {
    "bootstrap.4.4",
    "bootstrap.4.5",
    "scaffold-frontend.2",
    "scaffold-frontend.4",
    "scaffold-frontend.12",
    "scaffold-frontend.13",
}
SKIPPED_DESIGN_CHAIN = {"bootstrap.4.4", "bootstrap.4.5"}
UNRELATED_API = "scaffold-frontend.6"


def decision(
    decision_id: str,
    title: str,
    *,
    status: str = "accepted",
    depends_on: str = "none",
    supersedes: str = "none",
    history: str = "2026-09-19 accepted for the structural fixture",
) -> str:
    return f"""### {decision_id}: {title}
Date: 2026-09-19
Status: {status}
Decision: {title}
Reason: synthetic state needed to exercise shipped recovery metadata
Alternatives: none
Authority: owner
Evidence: structural integration fixture, 2026-09-19
Review: requirement-change
Depends on: {depends_on}
Supersedes: {supersedes}
History: {history}
"""


class DesignerRecoveryIntegration(unittest.TestCase):
    """Exercise framework metadata without claiming the represented work occurred."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="archetype-designer-recovery-")
        self.project = Path(self.temporary.name)
        (self.project / "design").mkdir()
        (self.project / "api").mkdir()
        (self.project / "References.md").write_text("# References\n\n- Decision location: DECISIONS.md\n")
        self.write_decisions()
        (self.project / "design" / "answers.md").write_text(
            "# Interview answers\n\n- Decision basis: DEC-001\n- path: pick-for-me\n"
        )
        (self.project / "design" / "artifact.md").write_text(
            "# Design artifact\n\n- Decision basis: DEC-002\n- Primary context: desktop operations\n"
        )
        (self.project / "design" / "review.md").write_text(
            "# Design review\n\n- Decision basis: DEC-002\n- Result: structural fixture only\n"
        )
        (self.project / "api" / "contract.md").write_text(
            "# API contract\n\n- Decision basis: DEC-003\n- Endpoint: shifts\n"
        )
        (self.project / "design" / "scope.md").write_text(
            "# Screen scope\n\n- Decision basis: DEC-006\n- Screen: none on the prior platform path\n"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_command(self, *command: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            command,
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stdout)
        return result

    def recovery(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run_command("python3", str(RECOVERY), *arguments, expected=expected)

    def next_step(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run_command("bash", str(NEXT_STEP), *arguments, expected=expected)

    def write_decisions(self, *, replace_direction: bool = False, replace_context: bool = False) -> None:
        records = [
            decision(
                DIRECTION,
                "Use the calm operations direction",
                status="superseded" if replace_direction else "accepted",
                history=(
                    "2026-09-20 superseded by DEC-004 after the direction changed"
                    if replace_direction
                    else "2026-09-19 accepted for the structural fixture"
                ),
            ),
            decision(
                CONTEXT,
                "Support the desktop operations context",
                status="superseded" if replace_context else "accepted",
                depends_on=DIRECTION,
                history=(
                    "2026-09-20 superseded by DEC-005 after the context changed"
                    if replace_context
                    else "2026-09-19 accepted for the structural fixture"
                ),
            ),
            decision(NO_SCREEN, "Use a platform path with no custom screen"),
            # Keep the unrelated API decision last before replacements. Appending a
            # design decision must not change this record's fingerprint.
            decision(API, "Use the shifts API contract"),
        ]
        if replace_direction:
            records.append(
                decision(
                    "DEC-004",
                    "Use the high-contrast operations direction",
                    supersedes=DIRECTION,
                    history="2026-09-20 accepted after review of the replacement direction",
                )
            )
        if replace_context:
            records.append(
                decision(
                    "DEC-005",
                    "Support desktop and phone contexts",
                    depends_on=DIRECTION,
                    supersedes=CONTEXT,
                    history="2026-09-20 accepted after the committed context changed",
                )
            )
        (self.project / "DECISIONS.md").write_text("# Decisions\n\n" + "\n".join(records))

    def basis(self, decisions: list[str], inputs: list[str]) -> str:
        arguments = [
            "basis",
            "--project",
            str(self.project),
            "--cwd",
            str(self.project),
        ]
        for value in decisions:
            arguments.extend(("--decision", value))
        for value in inputs:
            arguments.extend(("--input", value))
        return self.recovery(*arguments).stdout.strip()

    def write_ledger(self, *, skipped: bool = False) -> None:
        direction_basis = self.basis([DIRECTION], ["design/answers.md"])
        context_basis = self.basis(
            [CONTEXT], ["design/artifact.md", "design/review.md"]
        )
        api_basis = self.basis([API], ["api/contract.md"])
        lines = ["# Progress", "", "- Playbooks: bootstrap, scaffold-frontend", "", "## Step history"]
        if skipped:
            skip_basis = self.basis([NO_SCREEN], ["design/scope.md"])
            for step in sorted(SKIPPED_DESIGN_CHAIN):
                lines.append(
                    f"- [-] {step} | 2026-09-19 | rev fixture | cwd . | "
                    f"basis {skip_basis} | skipped (allowed when: product has no screen): "
                    "prior platform path had no custom screen"
                )
        else:
            lines.append(
                f"- [x] bootstrap.4.4 | 2026-09-19 | rev fixture | cwd . | "
                f"basis {direction_basis} | structural integration fixture closure"
            )
            for step in sorted(DESIGN_CHAIN - {"bootstrap.4.4"}):
                lines.append(
                    f"- [x] {step} | 2026-09-19 | rev fixture | cwd . | "
                    f"basis {context_basis} | structural integration fixture closure"
                )
        lines.append(
            f"- [x] {UNRELATED_API} | 2026-09-19 | rev fixture | cwd . | "
            f"basis {api_basis} | structural integration fixture closure"
        )
        (self.project / "PROGRESS.md").write_text("\n".join(lines) + "\n")

    def latest_states(self) -> dict[str, str]:
        states: dict[str, str] = {}
        for line in (self.project / "PROGRESS.md").read_text().splitlines():
            if not line.startswith("- ["):
                continue
            states[line.split(" |", 1)[0][6:]] = line[3]
        return states

    def test_shipped_metadata_names_the_designer_chain_and_basis(self) -> None:
        expected_dependencies = {
            "bootstrap.4.4": {"bootstrap.4.2", "bootstrap.4.3", "bootstrap.2.3"},
            "bootstrap.4.5": {"bootstrap.4.4"},
            "scaffold-frontend.2": {"scaffold-frontend.1", "bootstrap.4.5"},
            "scaffold-frontend.4": {"scaffold-frontend.2", "scaffold-frontend.3"},
            "scaffold-frontend.12": {
                "scaffold-frontend.4",
                "scaffold-frontend.8",
                "scaffold-frontend.9",
                "scaffold-frontend.10",
            },
            "scaffold-frontend.13": {"scaffold-frontend.12", "scaffold-frontend.11"},
        }
        for step, expected in expected_dependencies.items():
            with self.subTest(step=step):
                output = self.recovery(
                    "dependencies", "--engine", str(ENGINE), "--step", step
                ).stdout.strip()
                self.assertEqual(set(output.split("; ")), expected)
                requirement = self.recovery(
                    "requirement", "--engine", str(ENGINE), "--step", step
                ).stdout.strip()
                self.assertEqual(requirement, "decisions and inputs required")

        api_dependencies = self.recovery(
            "dependencies", "--engine", str(ENGINE), "--step", UNRELATED_API
        ).stdout.strip()
        self.assertEqual(api_dependencies, "none")

    def test_direction_replacement_reopens_design_chain_and_retains_api(self) -> None:
        self.write_ledger()
        self.write_decisions(replace_direction=True)

        result = self.next_step(
            "--reopen", DIRECTION, "--reason", "owner selected a replacement direction"
        )
        for step in DESIGN_CHAIN:
            self.assertIn(f"Reopened: {step}.", result.stdout)
        self.assertNotIn(f"Reopened: {UNRELATED_API}.", result.stdout)

        states = self.latest_states()
        self.assertTrue(all(states[step] == "~" for step in DESIGN_CHAIN))
        self.assertEqual(states[UNRELATED_API], "x")

    def test_context_decision_change_makes_design_evidence_stale_only(self) -> None:
        self.write_ledger()
        self.write_decisions(replace_context=True)

        result = self.next_step("--list", expected=1)
        for step in DESIGN_CHAIN - {"bootstrap.4.4"}:
            self.assertIn(
                f"REOPENED: {step}: its declared decision or input basis changed.",
                result.stdout,
            )
        self.assertNotIn(f"REOPENED: bootstrap.4.4:", result.stdout)
        self.assertNotIn(f"REOPENED: {UNRELATED_API}:", result.stdout)
        self.assertIn(f"closed  {UNRELATED_API}  API layer (client side)", result.stdout)

    def test_context_input_change_makes_design_evidence_stale_only(self) -> None:
        self.write_ledger()
        with (self.project / "design" / "artifact.md").open("a") as artifact:
            artifact.write("- Committed contexts: desktop and phone\n")

        result = self.next_step("--list", expected=1)
        for step in DESIGN_CHAIN - {"bootstrap.4.4"}:
            self.assertIn(
                f"REOPENED: {step}: its declared decision or input basis changed.",
                result.stdout,
            )
        self.assertNotIn(f"REOPENED: bootstrap.4.4:", result.stdout)
        self.assertNotIn(f"REOPENED: {UNRELATED_API}:", result.stdout)

    def test_previously_skipped_design_work_reopens_transitively(self) -> None:
        self.write_ledger(skipped=True)

        result = self.next_step(
            "--reopen",
            "bootstrap.4.4",
            "--reason",
            "the project now requires a custom screen",
        )
        for step in SKIPPED_DESIGN_CHAIN:
            self.assertIn(f"Reopened: {step}.", result.stdout)
        states = self.latest_states()
        self.assertTrue(all(states[step] == "~" for step in SKIPPED_DESIGN_CHAIN))
        self.assertEqual(states[UNRELATED_API], "x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
