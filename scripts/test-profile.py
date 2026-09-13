#!/usr/bin/env python3
"""Regression tests for scripts/validate-profile.sh (convention #30).

Each test builds a throwaway project root with a PROFILE.md and, where needed, a
TECHNICAL-DEBT.md, runs the validator there, and checks the exit code and the result
words. Valid counterexamples are included so an always-failing validator cannot pass.
Run from anywhere: python3 scripts/test-profile.py
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate-profile.sh"
TODAY = "2026-09-12"

ISOLATED = {
    "Schema": "1",
    "Operating stage": "isolated",
    "Stage reason": "owner only, synthetic data, no real effects",
    "Decision authority": "ai-decides",
    "Authority source": "defaulted",
    "Audience": "owner-only",
    "Data": "synthetic-disposable",
    "External effects": "none",
    "Operational reliance": "no",
    "Valuable records": "no",
    "Fallback": "unknown",
    "Contributors": "one",
    "Regulated data": "no",
    "Customer commitments": "no",
    "Monthly running-cost ceiling": "0 USD",
    "AI spend envelope": "the owner's existing subscription, no extra charges",
    "Observed-on": "2026-09-12",
    "Review": "first-outside-participant",
}

TRIAL = dict(ISOLATED, **{
    "Operating stage": "trial",
    "Stage reason": "identified testers with a spreadsheet fallback",
    "Decision authority": "owner-decides",
    "Authority source": "owner-stated",
    "Audience": "identified-participants",
    "Data": "real-nonpersonal",
    "Fallback": "yes",
    "Review": "2027-01-01",
})

OPERATIONAL = dict(ISOLATED, **{
    "Operating stage": "operational",
    "Stage reason": "customers depend on it",
    "Audience": "public",
    "Data": "personal",
    "External effects": "money, messages",
    "Operational reliance": "yes",
    "Valuable records": "yes",
    "Fallback": "no",
    "Contributors": "several",
    "Regulated data": "yes",
    "Customer commitments": "yes",
    "Review": "2027-03-01",
})

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def profile_text(base=ISOLATED, overrides=None, drop=(), extra_lines=(), tail=""):
    facts = dict(base)
    if overrides:
        facts.update(overrides)
    for key in drop:
        facts.pop(key, None)
    lines = ["# Project Profile", ""]
    lines += [f"- {k}: {v}" for k, v in facts.items()]
    lines += list(extra_lines)
    return "\n".join(lines) + "\n" + tail


def debt_entry(num, kind="deferral", control="#23 rate limiting", due="first-outside-participant",
               review="2027-01-01", closure="the rate-limit middleware test passes",
               status="open", drop=()):
    fields = [
        ("Logged", "2026-09-01 by test"),
        ("What", "something postponed"),
        ("Where", "src/"),
        ("Convention", "#23"),
        ("Severity", "medium"),
        ("Proposed fix", "do it"),
        ("Status", status),
        ("Related", "none"),
        ("Kind", kind),
        ("Control", control),
        ("Due-before", due),
        ("Review-by", review),
        ("Closure-evidence", closure),
    ]
    body = [f"## TD-{num:03d} — test entry {num}", ""]
    for k, v in fields:
        if k in drop or v is None:
            continue
        body.append(f"- **{k}:** {v}")
    return "\n".join(body) + "\n\n"


FENCED_EXAMPLE = (
    "# Technical Debt Log\n\n## Example entry\n\n```\n## TD-999 — example inside a fence\n\n"
    "- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n- **Due-before:** public-access\n```\n\n## Entries\n\n"
)

TRIGGER_CASES = {
    # trigger: (facts making it true, facts making it false, facts making it unknown)
    "first-outside-participant": ({"Audience": "identified-participants"}, {"Audience": "owner-only"}, {"Audience": "unknown"}),
    "public-access": ({"Audience": "public"}, {"Audience": "identified-participants"}, {"Audience": "unknown"}),
    "real-data": ({"Data": "real-nonpersonal"}, {"Data": "synthetic-disposable"}, {"Data": "unknown"}),
    "personal-data": ({"Data": "personal"}, {"Data": "real-nonpersonal"}, {"Data": "unknown"}),
    "real-money-or-external-action": ({"External effects": "records"}, {"External effects": "none"}, {"External effects": "unknown"}),
    "operational-reliance": ({"Operational reliance": "yes"}, {"Operational reliance": "no"}, {"Operational reliance": "unknown"}),
    "valuable-records": ({"Valuable records": "yes"}, {"Valuable records": "no"}, {"Valuable records": "unknown"}),
    "second-contributor": ({"Contributors": "several"}, {"Contributors": "one"}, {"Contributors": "unknown"}),
    "regulated-data-or-commitment": ({"Customer commitments": "yes"}, {"Regulated data": "no", "Customer commitments": "no"}, {"Regulated data": "unknown"}),
}


class ValidateProfileTests(unittest.TestCase):
    def run_validator(self, profile=None, debt=None, strict=False):
        with tempfile.TemporaryDirectory() as root:
            if profile is not None:
                Path(root, "PROFILE.md").write_text(profile)
            if debt is not None:
                Path(root, "TECHNICAL-DEBT.md").write_text(debt)
            env = dict(os.environ, VALIDATE_PROFILE_TODAY=TODAY)
            args = ["bash", str(SCRIPT)] + (["--strict"] if strict else [])
            proc = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True)
            return proc.returncode, ANSI.sub("", proc.stdout + proc.stderr)

    def assert_fail(self, out, code, fragment):
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL: " if fragment.startswith("FAIL") else "FAIL", out)
        self.assertIn(fragment, out)

    def assert_clean(self, out, code):
        self.assertEqual(code, 0, out)
        self.assertNotIn("FAIL", out)

    # ---- valid counterexamples -------------------------------------------------

    def test_valid_isolated_profile_with_pending_deferral_passes(self):
        code, out = self.run_validator(profile_text(), FENCED_EXAMPLE + debt_entry(1))
        self.assert_clean(out, code)
        self.assertIn("Profile source: declared", out)
        self.assertIn("OK: PROFILE.md parses (operating stage isolated, decision authority ai-decides, defaulted)", out)
        self.assertIn("DEFERRED: TD-001 until first-outside-participant", out)
        self.assertNotIn("TD-999", out)

    def test_valid_trial_profile_passes(self):
        code, out = self.run_validator(profile_text(TRIAL), debt_entry(2, due="public-access"))
        self.assert_clean(out, code)
        self.assertIn("decision authority owner-decides, owner-stated", out)
        self.assertIn("DEFERRED: TD-002 until public-access", out)

    def test_valid_operational_profile_passes_without_deferrals(self):
        code, out = self.run_validator(profile_text(OPERATIONAL), None)
        self.assert_clean(out, code)
        self.assertIn("operating stage operational is consistent", out)

    def test_template_sections_after_facts_are_ignored(self):
        tail = "\n## How the stage is derived\n\n- `isolated`: only the owner.\n- Mood: not a fact\n\n## Change log\n\n- 2026-09-12: isolated, initial\n"
        code, out = self.run_validator(profile_text(tail=tail))
        self.assert_clean(out, code)

    # ---- parsing ------------------------------------------------------------------

    def test_unknown_key_fails(self):
        code, out = self.run_validator(profile_text(extra_lines=["- Mood: cheerful"]))
        self.assert_fail(out, code, 'unknown key "Mood"')

    def test_duplicate_key_fails(self):
        code, out = self.run_validator(profile_text(extra_lines=["- Audience: public"]))
        self.assert_fail(out, code, 'key "Audience" appears 2 times')

    def test_missing_key_fails(self):
        for key in ISOLATED:
            with self.subTest(key=key):
                code, out = self.run_validator(profile_text(drop=(key,)))
                self.assert_fail(out, code, f'missing or empty key "{key}"')

    def test_empty_value_fails(self):
        code, out = self.run_validator(profile_text(overrides={"Stage reason": ""}))
        self.assert_fail(out, code, 'missing or empty key "Stage reason"')

    def test_template_placeholder_fails(self):
        code, out = self.run_validator(profile_text(overrides={"Audience": "[owner-only / identified-participants / public / unknown]"}))
        self.assert_fail(out, code, '"Audience" still holds the template placeholder')

    def test_invalid_enumerations_fail(self):
        cases = {
            "Operating stage": "prototype",
            "Decision authority": "committee",
            "Authority source": "guessed",
            "Audience": "everyone",
            "Data": "real",
            "Operational reliance": "maybe",
            "Valuable records": "some",
            "Fallback": "sort-of",
            "Contributors": "two",
            "Regulated data": "hipaa",
            "Customer commitments": "verbal",
        }
        for key, bad in cases.items():
            with self.subTest(key=key):
                code, out = self.run_validator(profile_text(overrides={key: bad}))
                self.assert_fail(out, code, f'"{key}" is "{bad}"')

    def test_invalid_external_effects_word_fails(self):
        code, out = self.run_validator(profile_text(overrides={"External effects": "money, fame"}))
        self.assert_fail(out, code, 'lists "fame"')

    def test_malformed_dates_fail(self):
        code, out = self.run_validator(profile_text(overrides={"Observed-on": "yesterday"}))
        self.assert_fail(out, code, '"Observed-on" is "yesterday"')
        code, out = self.run_validator(profile_text(overrides={"Review": "soon"}))
        self.assert_fail(out, code, '"Review" is "soon"')

    def test_wrong_schema_fails(self):
        code, out = self.run_validator(profile_text(overrides={"Schema": "2"}))
        self.assert_fail(out, code, 'Schema is "2"')

    # ---- stage versus facts ---------------------------------------------------------

    def test_isolated_contradictions_fail(self):
        cases = {
            "Audience": ("identified-participants", "Audience is identified-participants"),
            "Data": ("personal", "Data is personal"),
            "External effects": ("money", 'External effects is "money"'),
            "Operational reliance": ("yes", "Operational reliance is yes"),
            "Valuable records": ("yes", "Valuable records is yes"),
            "Customer commitments": ("yes", "Customer commitments is yes"),
        }
        for key, (value, message) in cases.items():
            with self.subTest(key=key):
                code, out = self.run_validator(profile_text(overrides={key: value}))
                self.assert_fail(out, code, f"Operating stage is isolated but {message}")

    def test_trial_contradictions_fail(self):
        cases = {
            "Audience": ("public", "Audience is public"),
            "Operational reliance": ("yes", "Operational reliance is yes"),
            "Fallback": ("no", "Fallback is no"),
        }
        for key, (value, message) in cases.items():
            with self.subTest(key=key):
                code, out = self.run_validator(profile_text(TRIAL, {key: value}))
                self.assert_fail(out, code, f"Operating stage is trial but {message}")

    def test_regulated_data_with_synthetic_data_fails(self):
        code, out = self.run_validator(profile_text(overrides={"Regulated data": "yes"}))
        self.assert_fail(out, code, "Regulated data is yes but Data is synthetic-disposable")

    def test_unknown_facts_are_reported_unverified(self):
        code, out = self.run_validator(profile_text(overrides={"Audience": "unknown", "Valuable records": "unknown"}))
        self.assert_clean(out, code)
        self.assertIn('UNVERIFIED: PROFILE.md: "Audience" is unknown', out)
        self.assertIn('UNVERIFIED: PROFILE.md: "Valuable records" is unknown', out)

    # ---- deferrals -----------------------------------------------------------------------

    def test_each_trigger_true_false_unknown(self):
        for trigger, (true_facts, false_facts, unknown_facts) in TRIGGER_CASES.items():
            with self.subTest(trigger=trigger, state="true"):
                # operational base keeps every true fact consistent with the stage
                code, out = self.run_validator(profile_text(OPERATIONAL, true_facts), debt_entry(1, due=trigger))
                self.assert_fail(out, code, f"trigger {trigger} is true")
            with self.subTest(trigger=trigger, state="false"):
                base = TRIAL if trigger in ("first-outside-participant", "public-access", "real-data", "personal-data") else ISOLATED
                false_profile = dict(base, **false_facts)
                if trigger == "first-outside-participant":
                    false_profile.update({"Operating stage": "isolated", "Data": "synthetic-disposable", "Audience": "owner-only"})
                code, out = self.run_validator(profile_text(false_profile), debt_entry(1, due=trigger))
                self.assert_clean(out, code)
                self.assertIn(f"DEFERRED: TD-001 until {trigger}", out)
            with self.subTest(trigger=trigger, state="unknown"):
                code, out = self.run_validator(profile_text(ISOLATED, unknown_facts), debt_entry(1, due=trigger))
                self.assertEqual(code, 0, out)
                self.assertIn(f"UNVERIFIED: TD-001 is due before {trigger}", out)

    def test_stage_triggers(self):
        code, out = self.run_validator(profile_text(TRIAL), debt_entry(1, due="trial-stage"))
        self.assert_fail(out, code, "trigger trial-stage is true")
        code, out = self.run_validator(profile_text(TRIAL), debt_entry(1, due="operational-stage"))
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-001 until operational-stage", out)
        code, out = self.run_validator(profile_text(OPERATIONAL), debt_entry(1, due="operational-stage"))
        self.assert_fail(out, code, "trigger operational-stage is true")

    def test_operational_stage_makes_operational_reliance_true(self):
        profile = profile_text(OPERATIONAL, {"Operational reliance": "unknown"})
        code, out = self.run_validator(profile, debt_entry(13, due="operational-reliance"))
        self.assert_fail(out, code, "trigger operational-reliance is true")

    def test_each_floor_item_as_deferral_fails(self):
        for item in ("secrets", "trust-boundary", "irreversible-effects", "personal-data", "authorized-reuse", "honest-completion"):
            with self.subTest(item=item):
                code, out = self.run_validator(profile_text(), debt_entry(2, control=f"floor: {item}"))
                self.assert_fail(out, code, f"a floor item ({item}) is never a deferral")

    def test_wont_fix_does_not_clear_triggered_deferral(self):
        code, out = self.run_validator(profile_text(TRIAL), debt_entry(4, due="first-outside-participant", status="won't-fix"))
        self.assert_fail(out, code, "won't-fix does not clear it")

    def test_fixed_deferral_is_ignored(self):
        code, out = self.run_validator(profile_text(TRIAL), debt_entry(5, due="first-outside-participant", status="fixed"))
        self.assert_clean(out, code)

    def test_deferral_missing_each_required_field_fails(self):
        for field in ("Control", "Due-before", "Review-by", "Closure-evidence"):
            with self.subTest(field=field):
                code, out = self.run_validator(profile_text(), debt_entry(6, drop=(field,)))
                self.assert_fail(out, code, f"deferral without {field}")

    def test_unknown_kind_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(6, kind="maybe-later"))
        self.assert_fail(out, code, 'Kind is "maybe-later"')

    def test_unknown_trigger_name_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(7, due="someday"))
        self.assert_fail(out, code, 'Due-before "someday" is neither a known trigger nor a date')

    def test_due_date_reached_fails_inclusive(self):
        code, out = self.run_validator(profile_text(), debt_entry(8, due="2026-09-01"))
        self.assert_fail(out, code, "Due-before date 2026-09-01 reached")
        code, out = self.run_validator(profile_text(), debt_entry(8, due=TODAY))
        self.assert_fail(out, code, f"Due-before date {TODAY} reached")

    def test_future_due_date_is_deferred(self):
        code, out = self.run_validator(profile_text(), debt_entry(9, due="2026-12-01"))
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-009 until 2026-12-01", out)

    def test_past_review_by_warns_only(self):
        code, out = self.run_validator(profile_text(), debt_entry(10, review="2026-01-01"))
        self.assert_clean(out, code)
        self.assertIn("WARN: TD-010: Review-by 2026-01-01 has passed", out)

    def test_malformed_review_by_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(10, review="next quarter"))
        self.assert_fail(out, code, 'Review-by "next quarter" is not a date')

    def test_legacy_entry_without_kind_is_untouched(self):
        legacy = "# Technical Debt Log\n\n## TD-020 — old entry\n\n- **Status:** open\n- **Severity:** low\n"
        code, out = self.run_validator(profile_text(), legacy)
        self.assert_clean(out, code)
        self.assertIn("TECHNICAL-DEBT.md has no deferrals", out)

    def test_shortcut_entries_are_not_deferrals(self):
        code, out = self.run_validator(profile_text(), debt_entry(21, kind="shortcut", due="someday"))
        self.assert_clean(out, code)

    # ---- missing profile and strict mode ---------------------------------------------------

    def test_absent_profile_without_deferrals_is_only_a_warning(self):
        code, out = self.run_validator(None, None)
        self.assertEqual(code, 0, out)
        self.assertIn("Profile source: missing", out)
        self.assertIn("WARN: PROFILE.md not found: reading the strictest profile", out)
        self.assertIn("strictest reading (operational, facts unknown) applied", out)

    def test_absent_profile_with_a_deferral_fails(self):
        for due in ("first-outside-participant", "operational-stage", "2030-01-01"):
            with self.subTest(due=due):
                code, out = self.run_validator(None, debt_entry(12, due=due))
                self.assert_fail(out, code, "a deferral cannot be evaluated without PROFILE.md")

    def test_absent_profile_with_legacy_debt_only_warns(self):
        legacy = "# Technical Debt Log\n\n## TD-020 — old entry\n\n- **Status:** open\n"
        code, out = self.run_validator(None, legacy)
        self.assertEqual(code, 0, out)

    def test_strict_mode_turns_unverified_into_errors(self):
        code, out = self.run_validator(profile_text(overrides={"Audience": "unknown", "Fallback": "no"}), None, strict=True)
        self.assert_fail(out, code, "strict mode: 1 unverified result(s) count as errors")
        code, out = self.run_validator(profile_text(), None, strict=True)
        self.assertEqual(code, 1, out)  # Fallback is unknown in the isolated base
        code, out = self.run_validator(profile_text(overrides={"Fallback": "no"}), None, strict=True)
        self.assert_clean(out, code)

    def test_strict_mode_fails_missing_profile(self):
        code, out = self.run_validator(None, None, strict=True)
        self.assertEqual(code, 1, out)
        self.assertIn("strict mode", out)

    def test_unknown_argument_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            proc = subprocess.run(["bash", str(SCRIPT), "--loose"], cwd=root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
