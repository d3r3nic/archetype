#!/usr/bin/env python3
"""Regression tests for scripts/validate-profile.sh (convention #30).

Each test builds a throwaway project root with a PROFILE.md and, where needed, a
TECHNICAL-DEBT.md, runs the validator there, and checks the exit code and the result
words. Valid counterexamples are included so an always-failing validator cannot pass.
Run from anywhere: python3 scripts/test-profile.py
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
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
    def run_validator(self, profile=None, debt=None, strict=False, declared=False, env=None):
        with tempfile.TemporaryDirectory() as root:
            if profile is not None:
                Path(root, "PROFILE.md").write_text(profile)
            if debt is not None:
                if isinstance(debt, bytes):
                    Path(root, "TECHNICAL-DEBT.md").write_bytes(debt)
                else:
                    Path(root, "TECHNICAL-DEBT.md").write_text(debt)
            run_env = dict(os.environ, VALIDATE_PROFILE_TODAY=TODAY, **(env or {}))
            args = ["bash", str(SCRIPT)] + (["--strict"] if strict else []) + (["--declared"] if declared else [])
            proc = subprocess.run(args, cwd=root, env=run_env, capture_output=True, text=True, errors="replace")
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
        for field in ("Control", "Due-before"):
            with self.subTest(field=field):
                code, out = self.run_validator(profile_text(), debt_entry(6, drop=(field,)))
                self.assert_fail(out, code, f"deferral without {field}")

    def test_unknown_kind_is_unverified(self):
        code, out = self.run_validator(profile_text(), debt_entry(6, kind="maybe-later"))
        self.assertIn('UNVERIFIED: TD-006: Kind is "maybe-later", neither shortcut nor deferral', out)
        code, out = self.run_validator(profile_text(), debt_entry(6, kind="maybe-later"), strict=True)
        self.assert_fail(out, code, "strict mode")

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

    def test_malformed_review_by_warns(self):
        code, out = self.run_validator(profile_text(), debt_entry(10, review="next quarter"))
        self.assertEqual(code, 0, out)
        self.assertIn('Review-by "next quarter" is not a calendar date', out)

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

    def test_declared_flag_fails_a_missing_profile_and_nothing_else(self):
        code, out = self.run_validator(None, None, declared=True)
        self.assertEqual(code, 1, out)
        self.assertIn("--declared requires it", out)
        code, out = self.run_validator(None, None)
        self.assertEqual(code, 0, out)

    def test_profile_above_an_endpoint_folder_is_found(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "PROFILE.md").write_text(profile_text())
            endpoint = Path(root, "frontend")
            endpoint.mkdir()
            env = dict(os.environ, VALIDATE_PROFILE_TODAY=TODAY)
            proc = subprocess.run(["bash", str(SCRIPT), "--declared"], cwd=endpoint, env=env, capture_output=True, text=True)
            out = ANSI.sub("", proc.stdout + proc.stderr)
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn("Profile source: declared", out)
            self.assertIn("above this folder", out)

    # ---- hardening after the independent audit ------------------------------------

    def test_conflicting_kind_is_read_as_the_deferral(self):
        entry = debt_entry(30, due="first-outside-participant").rstrip("\n") + "\n- **Kind:** shortcut\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-030: trigger first-outside-participant is true")
        self.assertIn("UNVERIFIED: TD-030: field(s) given more than one value: kind", out)

    def test_fields_under_a_later_heading_cannot_overwrite_the_entry(self):
        entry = debt_entry(31, due="first-outside-participant") + "## Separate summary\n\n- **Kind:** shortcut\n- **Due-before:** 2030-01-01\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-031: trigger first-outside-participant is true")
        self.assertIn("UNVERIFIED: TD-031: field(s) given more than one value: kind due-before", out)

    def test_duplicate_entry_id_warns(self):
        code, out = self.run_validator(profile_text(), debt_entry(32) + debt_entry(32, due="2030-01-01"))
        self.assertEqual(code, 0, out)
        self.assertIn("WARN: TD-032 appears more than once", out)

    def test_uppercase_floor_label_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(33, control="FLOOR: secrets"))
        self.assert_fail(out, code, "a floor item (secrets) is never a deferral")

    def test_unknown_floor_item_is_unverified(self):
        code, out = self.run_validator(profile_text(), debt_entry(34, control="floor: vibes"))
        self.assertIn('UNVERIFIED: TD-034: Control names an unknown floor item "vibes"', out)
        code, out = self.run_validator(profile_text(), debt_entry(34, control="floor: vibes"), strict=True)
        self.assert_fail(out, code, "strict mode")

    def test_control_should_name_a_convention_rule_or_floor_item(self):
        code, out = self.run_validator(profile_text(), debt_entry(35, control="something later"))
        self.assertEqual(code, 0, out)
        self.assertIn('WARN: TD-035: Control is "something later"; name the convention', out)
        for ok in ("#23 rate limiting", "B3 middleware order", "b5 queue retries"):
            with self.subTest(control=ok):
                code, out = self.run_validator(profile_text(), debt_entry(35, control=ok))
                self.assert_clean(out, code)

    def test_placeholder_control_and_closure_warn(self):
        code, out = self.run_validator(profile_text(), debt_entry(36, control="[convention or floor item]"))
        self.assertIn("WARN: TD-036: Control still holds a template placeholder", out)
        code, out = self.run_validator(profile_text(), debt_entry(36, closure="[what proves it closed]"))
        self.assertEqual(code, 0, out)
        self.assertIn("WARN: TD-036: Closure-evidence still holds a template placeholder", out)

    def test_impossible_calendar_dates_fail(self):
        code, out = self.run_validator(profile_text(overrides={"Observed-on": "2026-02-30"}))
        self.assert_fail(out, code, '"Observed-on" is "2026-02-30"')
        code, out = self.run_validator(profile_text(), debt_entry(37, due="2026-99-99"))
        self.assert_fail(out, code, 'Due-before "2026-99-99" is neither a known trigger nor a date')
        code, out = self.run_validator(profile_text(), debt_entry(37, review="2027-02-30"))
        self.assertEqual(code, 0, out)
        self.assertIn('WARN: TD-037: Review-by "2027-02-30" is not a calendar date', out)
        code, out = self.run_validator(profile_text(), debt_entry(37, due="2028-02-29", review="2028-02-29"))
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-037 until 2028-02-29", out)

    def test_non_iso_date_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(38, due="2030/01/01"))
        self.assert_fail(out, code, 'Due-before "2030/01/01" is neither a known trigger nor a date')

    def test_empty_external_effects_items_fail(self):
        code, out = self.run_validator(profile_text(OPERATIONAL, {"External effects": ", ,"}))
        self.assert_fail(out, code, '"External effects" contains an empty item')
        code, out = self.run_validator(profile_text(OPERATIONAL, {"External effects": "money,,records"}))
        self.assert_fail(out, code, '"External effects" contains an empty item')
        code, out = self.run_validator(profile_text(OPERATIONAL, {"External effects": "money, records"}))
        self.assert_clean(out, code)

    def test_crlf_input_is_accepted(self):
        profile = profile_text(TRIAL).replace("\n", "\r\n")
        debt = debt_entry(39, due="public-access").replace("\n", "\r\n")
        code, out = self.run_validator(profile, debt)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-039 until public-access", out)

    def test_key_with_trailing_space_is_unknown(self):
        code, out = self.run_validator(profile_text(extra_lines=["- Audience : public"], drop=("Audience",)))
        self.assert_fail(out, code, 'unknown key "Audience "')
        self.assertIn('missing or empty key "Audience"', out)

    def test_heading_on_first_fact_line_is_reported_once(self):
        text = "## Facts\n" + profile_text()
        code, out = self.run_validator(text)
        self.assert_fail(out, code, "PROFILE.md has no facts block")
        self.assertNotIn('missing or empty key "Schema"', out)

    def test_unclosed_fence_is_unverified_instead_of_hiding_entries(self):
        debt = "# Technical Debt Log\n\n```js\nexample without a closing fence\n\n" + debt_entry(50, control="floor: secrets")
        code, out = self.run_validator(profile_text(TRIAL), debt)
        self.assertIn("UNVERIFIED: TECHNICAL-DEBT.md has a code fence that never closes (opened at line 3)", out)
        self.assertNotIn("has no deferrals", out)
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "strict mode")

    def test_tilde_fenced_example_is_ignored(self):
        debt = "# Technical Debt Log\n\n~~~\n" + debt_entry(51, control="floor: secrets") + "~~~\n\n" + debt_entry(52)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertNotIn("TD-051", out)
        self.assertIn("DEFERRED: TD-052 until first-outside-participant", out)

    def test_strict_mode_via_environment_variable(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "PROFILE.md").write_text(profile_text(overrides={"Audience": "unknown", "Fallback": "no"}))
            env = dict(os.environ, VALIDATE_PROFILE_TODAY=TODAY, VALIDATE_PROFILE_STRICT="1")
            proc = subprocess.run(["bash", str(SCRIPT)], cwd=root, env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("Mode: strict", proc.stdout)
        self.assertIn("strict mode: 1 unverified result(s) count as errors", ANSI.sub("", proc.stdout))

    def test_longer_fence_with_shorter_run_inside_does_not_hide_entries(self):
        example = "````markdown\n```\n````\n\n"
        debt = "# Technical Debt Log\n\n" + example + debt_entry(60, due="first-outside-participant") + example
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "TD-060: trigger first-outside-participant is true")

    def test_longer_fence_example_containing_sample_debt_is_ignored(self):
        example = "````\n```\n" + debt_entry(61, control="floor: secrets") + "```\n````\n\n"
        debt = "# Technical Debt Log\n\n" + example + debt_entry(62)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertNotIn("TD-061", out)
        self.assertIn("DEFERRED: TD-062 until first-outside-participant", out)

    def test_empty_first_value_and_a_filled_one_are_a_conflict(self):
        entry = ("## TD-063 — empty then filled\n\n- **Status:** open\n- **Kind:**\n- **Kind:** deferral\n- **Control:**\n"
                 "- **Control:** #23 rate limiting\n- **Due-before:** public-access\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(), entry)
        self.assertEqual(code, 0, out)
        self.assertIn("UNVERIFIED: TD-063: field(s) given more than one value: kind control", out)
        self.assertIn("DEFERRED: TD-063 until public-access", out)

    def test_trailing_section_under_a_level_one_heading_is_not_part_of_the_entry(self):
        debt = debt_entry(68) + "# Audit history\n\n- **Logged:** 2026-09-01\n- **Logged:** 2026-09-02\n- **Kind:** shortcut\n"
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-068 until first-outside-participant", out)

    def test_a_renewed_due_date_cannot_hide_a_triggered_deferral(self):
        entry = debt_entry(69, due="first-outside-participant").rstrip("\n") + "\n- **Due-before:** 2030-01-01\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-069: trigger first-outside-participant is true")
        self.assertIn("UNVERIFIED: TD-069: field(s) given more than one value: due-before", out)
        self.assertNotIn("DEFERRED: TD-069", out)

    def test_trailing_comma_and_spaced_letters_in_effects_fail(self):
        code, out = self.run_validator(profile_text(OPERATIONAL, {"External effects": "money,"}))
        self.assert_fail(out, code, '"External effects" contains an empty item')
        code, out = self.run_validator(profile_text(OPERATIONAL, {"External effects": "m o n e y"}))
        self.assert_fail(out, code, '"External effects" lists "m o n e y"')

    def test_fields_under_a_follow_up_heading_still_belong_to_the_entry(self):
        entry = ("## TD-065 — retrofitted\n\n- **Status:** open\n- **Severity:** high\n\n## Follow-up\n\n"
                 "- **Kind:** deferral\n- **Control:** floor: secrets\n- **Due-before:** first-outside-participant\n"
                 "- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-065: a floor item (secrets) is never a deferral")
        self.assertIn("TD-065: trigger first-outside-participant is true", out)

    def test_h3_follow_up_inside_entry_is_fine(self):
        entry = debt_entry(66, due="public-access").rstrip("\n") + "\n\n### Follow-up\n\nStill waiting on the first tester.\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-066 until public-access", out)

    def test_mixed_fence_indentation_cannot_hide_an_entry(self):
        first = "  ```\nexample one\n```\n\n"
        second = "```\nexample two\n  ```\n\n"
        debt = "# Technical Debt Log\n\n" + first + debt_entry(72, due="first-outside-participant") + second
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "TD-072: trigger first-outside-participant is true")

    def test_indented_fenced_sample_is_ignored(self):
        sample = "  ```\n  ## TD-073 — indented sample\n  - **Kind:** deferral\n  - **Control:** floor: secrets\n  ```\n\n"
        debt = "# Technical Debt Log\n\n" + sample + debt_entry(74)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertNotIn("TD-073", out)
        self.assertIn("DEFERRED: TD-074 until first-outside-participant", out)

    def test_four_space_indented_fence_marker_is_content(self):
        debt = "# Technical Debt Log\n\n```\n    ```\nstill inside the example\n```\n\n" + debt_entry(75)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-075 until first-outside-participant", out)

    def test_inline_code_spans_are_not_fences(self):
        debt = ("# Technical Debt Log\n\n```inline```\n\n" + debt_entry(90, due="first-outside-participant")
                + "```\n```literal```\n```\n")
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "TD-090: trigger first-outside-participant is true")

    def test_tilde_fence_info_string_may_contain_backticks(self):
        debt = "# Technical Debt Log\n\n~~~ example with `code`\n" + debt_entry(92, control="floor: secrets") + "~~~\n\n" + debt_entry(93)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertNotIn("TD-092", out)
        self.assertIn("DEFERRED: TD-093 until first-outside-participant", out)

    def test_html_inside_a_backtick_run_does_not_become_a_fence(self):
        odd_line = '```<b title="`">x</b>\n'
        debt = ("# Technical Debt Log\n\n" + odd_line + "\n" + debt_entry(116, due="first-outside-participant")
                + "```\n" + odd_line + "```\n")
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "TD-116: trigger first-outside-participant is true")

    def test_deferral_fields_without_kind_are_unverified(self):
        entry = ("## TD-121 — no kind\n\n- **Status:** open\n- **Control:** #23 rate limiting\n- **Due-before:** first-outside-participant\n"
                 "- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assertEqual(code, 0, out)
        self.assertIn("UNVERIFIED: TD-121 carries deferral fields (Control, Due-before, Review-by or Closure-evidence) but no Kind", out)
        self.assertNotIn("has no deferrals", out)
        code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
        self.assert_fail(out, code, "strict mode")

    def test_kind_is_read_in_any_case_and_markup(self):
        for kind in ("Deferral", "DEFERRAL", "*deferral*", "deferral (#30)"):
            with self.subTest(kind=kind):
                code, out = self.run_validator(profile_text(), debt_entry(125, kind=kind))
                self.assert_clean(out, code)
                self.assertIn("DEFERRED: TD-125 until first-outside-participant", out)

    def test_html_wrapped_kind_is_read(self):
        entry = "## TD-126 — blank metadata\n\n- **Status:** open\n- <code>Kind</code>: deferral\n- **Due-before:**\n"
        code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
        self.assert_fail(out, code, "TD-126: deferral without Due-before")
        self.assertNotIn("has no deferrals", out)

    def test_floor_item_as_shortcut_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(127, kind="shortcut", control="floor: secrets"))
        self.assert_fail(out, code, "TD-127: a floor item (secrets) is never postponed, as a deferral or as a shortcut")
        self.assertNotIn("has no deferrals", out)

    def test_floor_controls_on_shortcuts(self):
        code, out = self.run_validator(profile_text(), debt_entry(128, kind="shortcut", control="floor"))
        self.assertIn("UNVERIFIED: TD-128: Control says floor but names no floor item", out)
        code, out = self.run_validator(profile_text(), debt_entry(128, kind="shortcut", control="Floor : secrets"))
        self.assert_fail(out, code, "TD-128: a floor item (secrets) is never postponed")
        code, out = self.run_validator(profile_text(), debt_entry(128, kind="shortcut", control="something vague"))
        self.assertEqual(code, 0, out)
        self.assertIn('WARN: TD-128: Control is "something vague"; name the convention', out)
        code, out = self.run_validator(profile_text(), debt_entry(128, kind="shortcut", control="#0 duplicated helper"))
        self.assert_clean(out, code)

    def test_failed_entry_prints_no_deferred_line(self):
        code, out = self.run_validator(profile_text(), debt_entry(131, control="floor: secrets", due="public-access"))
        self.assert_fail(out, code, "TD-131: a floor item (secrets) is never a deferral")
        self.assertNotIn("DEFERRED: TD-131", out)

    def test_empty_floor_item_is_unverified_with_the_clear_message(self):
        code, out = self.run_validator(profile_text(), debt_entry(132, kind="shortcut", control="floor:"))
        self.assertIn("UNVERIFIED: TD-132: Control says floor but names no floor item", out)
        code, out = self.run_validator(profile_text(), debt_entry(132, kind="shortcut", control="floor:"), strict=True)
        self.assert_fail(out, code, "strict mode")

    def test_invalid_review_by_warns_and_the_deferral_stays_deferred(self):
        code, out = self.run_validator(profile_text(), debt_entry(137, due="2027-01-01", review="not-a-date"))
        self.assertEqual(code, 0, out)
        self.assertIn('WARN: TD-137: Review-by "not-a-date" is not a calendar date', out)
        self.assertIn("DEFERRED: TD-137 until 2027-01-01", out)

    def test_curly_quotes_accents_and_bytes_that_are_not_utf8_hide_no_later_entry(self):
        # In a UTF-8 locale the macOS awk exited on a character that substr cut in two, or on a byte
        # that is not UTF-8, and every entry after it went unread: a postponed floor item passed as
        # "no deferrals". The validator reads bytes whatever the caller's locale.
        utf8 = {"LC_ALL": "en_US.UTF-8" if sys.platform == "darwin" else "C.UTF-8"}
        later = b"\n## TD-175 floor shortcut\n\n- **Status:** open\n- **Kind:** shortcut\n- **Control:** floor: secrets\n"
        for line in ("- \u201cQuoted\u201d remark".encode(), "- \u00e9t\u00e9 note".encode(), "- \u2014 an aside".encode(),
                     b"- caf\xe9 written in Latin-1"):
            with self.subTest(line=line):
                entry = b"## TD-174 \xe2\x80\x94 note\n\n- **Status:** open\n- **Kind:** shortcut\n" + line + b"\n" + later
                code, out = self.run_validator(profile_text(), entry, env=utf8)
                self.assert_fail(out, code, "TD-175: a floor item (secrets) is never postponed")
                self.assertNotIn("has no deferrals", out)

    def test_a_parser_that_stops_early_fails_the_check(self):
        # Whatever stops the parser, what it did not read must not pass: here an awk that exits for
        # the entry parser alone, as the macOS awk did.
        with tempfile.TemporaryDirectory() as bin_dir:
            fake = Path(bin_dir, "awk")
            fake.write_text('#!/bin/sh\ncase "$*" in *UNCLOSED-FENCE*) exit 2 ;; esac\nexec %s "$@"\n' % shlex.quote(shutil.which("awk")))
            fake.chmod(0o755)
            code, out = self.run_validator(profile_text(), debt_entry(1), env={"PATH": bin_dir + os.pathsep + os.environ["PATH"]})
        self.assert_fail(out, code, "TECHNICAL-DEBT.md was not read to the end (the parser exited with status 2)")
        self.assertNotIn("has no deferrals", out)
        self.assertNotIn("every deferral is well-formed", out)

    # ---- the reader: common written forms, other labels free ------------------

    def test_labels_are_read_in_common_written_forms(self):
        forms = ["Kind: deferral", "- Kind: deferral", "* **Kind:** deferral", "1. _Kind_: deferral", "- `Kind`: deferral",
                 "- <b>Kind:</b> deferral", "- [Kind](#kind): deferral", "- ** Kind:** deferral", "  - **Kind**: deferral"]
        for kind_line in forms:
            with self.subTest(kind_line=kind_line):
                entry = f"## TD-201 — form\n\n- **Status:** open\n{kind_line}\n- **Control:** floor: secrets\n- Due before: public-access\n"
                code, out = self.run_validator(profile_text(), entry)
                self.assert_fail(out, code, "TD-201: a floor item (secrets) is never a deferral")

    def test_due_before_and_review_by_may_be_written_with_a_space(self):
        entry = "## TD-202 — spaced\n\nKind: deferral\nControl: #23 rate limiting\nDue before: 2020-01-01\nReview by: 2030-01-01\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-202: Due-before date 2020-01-01 reached")

    def test_other_labels_are_free(self):
        entry = debt_entry(203).rstrip("\n") + "\n- **Control plane:** a queue\n- **Status note:** waiting on a vendor\n- **Kind of work:** backend\n\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-203 until first-outside-participant", out)

    def test_review_by_and_closure_evidence_are_optional(self):
        code, out = self.run_validator(profile_text(), debt_entry(204, drop=("Review-by", "Closure-evidence")))
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-204 until first-outside-participant", out)

    def test_an_entry_that_mentions_a_deferral_without_a_readable_kind_is_unverified(self):
        entry = "## TD-205 — unread kind\n\n- Status: open\n- Kind (deferral) until the first outside participant\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assertEqual(code, 0, out)
        self.assertIn("UNVERIFIED: TD-205 mentions deferring but has no Kind line this check can read", out)
        code, out = self.run_validator(profile_text(), entry, strict=True)
        self.assert_fail(out, code, "strict mode")

    def test_a_deferral_written_as_a_table_or_prose_is_unverified(self):
        facts = profile_text(OPERATIONAL)
        table = ("## TD-206 — table\n\n| Field | Value |\n|---|---|\n| Kind | deferred |\n| Control | #23 rate limiting |\n"
                 "| Due-before | public-access |\n| Status | open |\n")
        prose = "## TD-207 — prose\n\nDeferred until public-access. Control: #23 rate limiting. Status: open.\n"
        for entry in (table, prose):
            with self.subTest(entry=entry.splitlines()[0]):
                code, out = self.run_validator(facts, entry)
                self.assertIn("mentions deferring but has no Kind line this check can read", out)
                self.assertNotIn("has no deferrals", out)
                code, out = self.run_validator(facts, entry, strict=True)
                self.assert_fail(out, code, "strict mode")

    def test_help_exits_zero(self):
        with tempfile.TemporaryDirectory() as root:
            proc = subprocess.run(["bash", str(SCRIPT), "--help"], cwd=root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Validates the operating profile", proc.stdout)

    def test_regulated_data_alone_fires_the_commitment_trigger(self):
        profile = profile_text(TRIAL, {"Data": "personal", "Regulated data": "yes"})
        code, out = self.run_validator(profile, debt_entry(54, due="regulated-data-or-commitment"))
        self.assert_fail(out, code, "trigger regulated-data-or-commitment is true")

    def test_trigger_names_are_case_sensitive(self):
        code, out = self.run_validator(profile_text(), debt_entry(40, due="Public-Access"))
        self.assert_fail(out, code, 'Due-before "Public-Access" is neither a known trigger nor a date')

    def test_reordered_fields_and_colon_values_pass(self):
        entry = ("## TD-041 — reordered\n\n- **Closure-evidence:** test passes: limiter present\n- **Due-before:** public-access\n"
                 "- **Kind:** deferral\n- **Review-by:** 2027-01-01\n- **Control:** #23 rate limiting: public routes\n- **Status:** in-progress\n")
        code, out = self.run_validator(profile_text(TRIAL, {"Stage reason": "testers: a dozen, fallback: spreadsheet"}), entry)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-041 until public-access", out)

    def test_stage_triggers_are_false_at_isolated_and_trial_stage_fires_at_operational(self):
        for trigger in ("trial-stage", "operational-stage"):
            with self.subTest(trigger=trigger):
                code, out = self.run_validator(profile_text(), debt_entry(42, due=trigger))
                self.assert_clean(out, code)
                self.assertIn(f"DEFERRED: TD-042 until {trigger}", out)
        code, out = self.run_validator(profile_text(OPERATIONAL), debt_entry(42, due="trial-stage"))
        self.assert_fail(out, code, "trigger trial-stage is true")

    def test_unknown_argument_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            proc = subprocess.run(["bash", str(SCRIPT), "--loose"], cwd=root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
