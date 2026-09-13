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
        self.assert_fail(out, code, 'Review-by "next quarter" is not a real calendar date')

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

    # ---- hardening after the independent audit ------------------------------------

    def test_repeated_field_in_entry_fails(self):
        entry = debt_entry(30, due="first-outside-participant") .rstrip("\n") + "\n- **Kind:** shortcut\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-030: field(s) repeated inside the entry: Kind")

    def test_fields_under_a_later_heading_cannot_overwrite_the_entry(self):
        entry = debt_entry(31, due="first-outside-participant") + "## Separate summary\n\n- **Kind:** shortcut\n- **Due-before:** 2030-01-01\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-031: field(s) repeated inside the entry: Kind Due-before")

    def test_duplicate_entry_id_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(32) + debt_entry(32, due="2030-01-01"))
        self.assert_fail(out, code, "TD-032 appears more than once")

    def test_uppercase_floor_label_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(33, control="FLOOR: secrets"))
        self.assert_fail(out, code, "a floor item (secrets) is never a deferral")

    def test_unknown_floor_item_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(34, control="floor: vibes"))
        self.assert_fail(out, code, 'Control names unknown floor item "vibes"')

    def test_control_must_name_a_convention_rule_or_floor_item(self):
        code, out = self.run_validator(profile_text(), debt_entry(35, control="something later"))
        self.assert_fail(out, code, 'Control is "something later"; name a convention')
        for ok in ("#23 rate limiting", "B3 middleware order", "b5 queue retries"):
            with self.subTest(control=ok):
                code, out = self.run_validator(profile_text(), debt_entry(35, control=ok))
                self.assert_clean(out, code)

    def test_placeholder_control_and_closure_fail(self):
        code, out = self.run_validator(profile_text(), debt_entry(36, control="[convention or floor item]"))
        self.assert_fail(out, code, "TD-036: Control still holds a template placeholder")
        code, out = self.run_validator(profile_text(), debt_entry(36, closure="[what proves it closed]"))
        self.assert_fail(out, code, "TD-036: Closure-evidence still holds a template placeholder")

    def test_impossible_calendar_dates_fail(self):
        code, out = self.run_validator(profile_text(overrides={"Observed-on": "2026-02-30"}))
        self.assert_fail(out, code, '"Observed-on" is "2026-02-30"')
        code, out = self.run_validator(profile_text(), debt_entry(37, due="2026-99-99"))
        self.assert_fail(out, code, 'Due-before "2026-99-99" is neither a known trigger nor a date')
        code, out = self.run_validator(profile_text(), debt_entry(37, review="2027-02-30"))
        self.assert_fail(out, code, 'Review-by "2027-02-30" is not a real calendar date')
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

    def test_unclosed_fence_fails_instead_of_hiding_entries(self):
        debt = "# Technical Debt Log\n\n```js\nexample without a closing fence\n\n" + debt_entry(50, control="floor: secrets")
        code, out = self.run_validator(profile_text(TRIAL), debt)
        self.assert_fail(out, code, "TECHNICAL-DEBT.md has a code fence that never closes (opened at line 3)")
        self.assertNotIn("has no deferrals", out)

    def test_tilde_fenced_example_is_ignored(self):
        debt = "# Technical Debt Log\n\n~~~\n" + debt_entry(51, control="floor: secrets") + "~~~\n\n" + debt_entry(52)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertNotIn("TD-051", out)
        self.assertIn("DEFERRED: TD-052 until first-outside-participant", out)

    def test_colon_outside_bold_markers_still_parses(self):
        entry = ("## TD-053 — mis-emphasized\n\n- **Status**: open\n- **Kind**: deferral\n- **Control**: floor: secrets\n"
                 "- **Due-before**: public-access\n- **Review-by**: 2027-01-01\n- **Closure-evidence**: a test\n")
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-053: a floor item (secrets) is never a deferral")

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

    def test_empty_first_repeated_field_fails(self):
        entry = ("## TD-063 — empty then filled\n\n- **Status:** open\n- **Kind:**\n- **Kind:** deferral\n- **Control:**\n"
                 "- **Control:** #23 rate limiting\n- **Due-before:** public-access\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-063: field(s) repeated inside the entry: Kind Control")

    def test_repeated_ungoverned_field_is_not_an_error(self):
        entry = debt_entry(64).rstrip("\n") + "\n- **Logged:** 2026-09-02 by someone else\n\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_clean(out, code)

    def test_trailing_section_under_a_level_one_heading_is_not_part_of_the_entry(self):
        debt = debt_entry(68) + "# Audit history\n\n- **Logged:** 2026-09-01\n- **Logged:** 2026-09-02\n- **Kind:** shortcut\n"
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertIn("DEFERRED: TD-068 until first-outside-participant", out)

    def test_repeated_governed_field_keeps_the_first_value(self):
        entry = debt_entry(69, due="first-outside-participant").rstrip("\n") + "\n- **Due-before:** 2030-01-01\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-069: field(s) repeated inside the entry: Due-before")
        self.assertIn("TD-069: trigger first-outside-participant is true", out)
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

    def test_entry_heading_at_wrong_level_fails_when_it_carries_fields(self):
        entry = "### TD-067 — wrong level\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, '"### TD-067 — wrong level" carries entry fields but is not a level-two heading')

    def test_entry_heading_at_wrong_level_without_fields_warns(self):
        debt = "### TD-070 — just a note\n\nNothing structured here.\n\n" + debt_entry(71)
        code, out = self.run_validator(profile_text(), debt)
        self.assert_clean(out, code)
        self.assertIn('WARN: TECHNICAL-DEBT.md: "### TD-070 — just a note" is not a level-two heading', out)
        self.assertIn("DEFERRED: TD-071 until first-outside-participant", out)

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

    def test_heading_whitespace_variants_are_entries(self):
        for heading in ("  ## TD-080 — indented", "##  TD-080 — double space", "##\tTD-080 — tab", "## TD-080"):
            with self.subTest(heading=heading):
                body = "\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** #23 rate limiting\n- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n"
                code, out = self.run_validator(profile_text(TRIAL), heading + body, strict=True)
                self.assert_fail(out, code, "TD-080: trigger first-outside-participant is true")

    def test_indented_wrong_level_heading_with_fields_fails(self):
        entry = "  ### TD-091 — indented h3\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "carries entry fields but is not a level-two heading")
        self.assertNotIn("has no deferrals", out)

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

    def test_field_list_formatting_variants_are_read(self):
        variants = ["-  **Kind:** deferral", "-\t**Kind:** deferral", "* **Kind:** deferral", "+ **Kind:** deferral", "   - **Kind:** deferral"]
        for kind_line in variants:
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-094 — formatting\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-094: trigger first-outside-participant is true")

    def test_indented_field_block_is_read(self):
        entry = "## TD-095 — indented fields\n\n" + "\n".join("  " + l for l in debt_entry(95, control="floor: secrets").splitlines()[2:] if l) + "\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-095: a floor item (secrets) is never a deferral")

    def test_td_heading_with_too_many_marks_or_no_space_fails_when_it_carries_fields(self):
        for heading in ("####### TD-088 — seven marks", "##TD-089 — no space"):
            with self.subTest(heading=heading):
                entry = heading + "\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
                code, out = self.run_validator(profile_text(), entry)
                self.assert_fail(out, code, "carries entry fields but is not a level-two heading")

    def test_tab_indented_field_block_fails_loudly(self):
        fields = "\n".join("\t" + l for l in debt_entry(96, control="floor: secrets").splitlines()[2:] if l)
        entry = "## TD-096 — tab indented\n\n" + fields + "\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-096: field label(s) found on lines the validator does not read as fields:")
        self.assertIn("Kind", out)
        self.assertNotIn("has no deferrals", out)

    def test_label_in_running_text_fails_loudly(self):
        entry = "## TD-097 — prose\n\n- **Status:** open\n\nWe set **Kind:** deferral here and **Control:** #23 later.\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-097: field label(s) found on lines the validator does not read as fields: Kind")

    def test_kind_with_value_on_next_line_fails(self):
        entry = ("## TD-098 — wrapped\n\n- **Status:** open\n- **Kind:**\n  deferral\n- **Control:** #23 rate limiting\n"
                 "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
        self.assert_fail(out, code, "TD-098: Kind is present but has no value on its line")
        self.assertNotIn("has no deferrals", out)

    def test_ordered_list_and_underscore_bold_fields_are_read(self):
        for kind_line in ("1. **Kind:** deferral", "2) **Kind:** deferral", "- __Kind:__ deferral", "- __Kind__: deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-099 — other markers\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-099: trigger first-outside-participant is true")

    def test_underlined_td_heading_with_fields_fails(self):
        for underline in ("---", "==="):
            with self.subTest(underline=underline):
                entry = "TD-100 — underlined\n" + underline + "\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
                code, out = self.run_validator(profile_text(), entry)
                self.assert_fail(out, code, "carries entry fields but is not a level-two heading")

    def test_governed_label_in_follow_up_prose_fails_loudly(self):
        entry = debt_entry(101, due="public-access").rstrip("\n") + "\n\n### Follow-up\n\n**Status:** A prose summary.\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-101: field label(s) found on lines the validator does not read as fields: Status")

    def test_html_bold_field_is_read(self):
        entry = ("## TD-102 — html bold\n\n- <b>Status:</b> open\n- <strong>Kind:</strong> deferral\n- <b>Control:</b> floor: secrets\n"
                 "- <b>Due-before:</b> public-access\n- <b>Review-by:</b> 2027-01-01\n- <b>Closure-evidence:</b> a test\n")
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-102: a floor item (secrets) is never a deferral")

    def test_space_inside_bold_markers_is_read_as_the_field(self):
        entry = "## TD-103 — spaced markers\n\n- **Status:** open\n- ** Kind:** deferral\n- **Control:** floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-103: a floor item (secrets) is never a deferral")

    def test_whitespace_inside_label_is_normalized(self):
        for kind_line in ("- **Kind :** deferral", "- **Kind\t:** deferral", "- ** Kind:** deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-104 — label whitespace\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assertEqual(code, 1, out)
                self.assertTrue("TD-104: trigger first-outside-participant is true" in out or "TD-104: field label(s) found" in out, out)

    def test_short_and_wrapped_setext_headings_with_fields_fail(self):
        cases = ["TD-105 underlined\n-\n", "TD-105 underlined\n==\n", "TD-105 title\ncontinued title\n---\n"]
        for head in cases:
            with self.subTest(head=head.replace("\n", "|")):
                entry = head + "\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
                code, out = self.run_validator(profile_text(), entry)
                self.assert_fail(out, code, "carries entry fields but is not a level-two heading")

    def test_italic_label_fails_loudly(self):
        entry = "## TD-106 — italic\n\n- **Status:** open\n- *Kind:* deferral\n- _Control:_ floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-106: field label(s) found on lines the validator does not read as fields: Kind Control")

    def test_html_bold_variants_are_read(self):
        for kind_line in ("- <STRONG>Kind:</STRONG> deferral", '- <strong class="label">Kind:</strong> deferral', "- <b >Kind:</b > deferral", "- <B>Kind:</B> deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-107 — html variants\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-107: trigger first-outside-participant is true")

    def test_inline_markup_around_the_heading_identifier_is_read(self):
        for heading in ("## **TD-108** title", "## `TD-108` title", "## [TD-108](link) title", "## <b>TD-108</b> title", "## _TD-108_ title"):
            with self.subTest(heading=heading):
                entry = (heading + "\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-108: trigger first-outside-participant is true")

    def test_formatted_setext_identifier_with_fields_fails(self):
        entry = "**TD-109** underlined\n---\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "carries entry fields but is not a level-two heading")

    def test_spaced_closing_html_tag_is_read(self):
        entry = ("## TD-110 — spaced closer\n\n- < b >Status:< /b > open\n- <b>Kind:< /b > deferral\n- <b>Control:</b> floor: secrets\n")
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-110: a floor item (secrets) is never a deferral")

    def test_bare_governed_name_with_colon_in_prose_fails_loudly(self):
        entry = "## TD-111 — bare\n\n- **Status:** open\n\nKind: deferral\nControl: floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-111: field label(s) found on lines the validator does not read as fields: Kind Control")

    def test_governed_word_without_colon_in_prose_is_fine(self):
        entry = debt_entry(112, due="public-access").rstrip("\n") + "\n\n### Follow-up\n\nThe status of the control is unchanged; see the Kind of work in the plan.\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_clean(out, code)

    def test_nested_heading_wrappers_are_read(self):
        for heading in ("## **[TD-113](#debt)** title", "## [**TD-113**](#debt) title", "## [`TD-113`](#debt) title", "## _**TD-113**_ title"):
            with self.subTest(heading=heading):
                entry = (heading + "\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-113: trigger first-outside-participant is true")
        entry = "[**TD-114**](#debt) underlined\n---\n\n- **Status:** open\n- **Kind:** deferral\n- **Control:** floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "carries entry fields but is not a level-two heading")

    def test_quoted_attribute_with_angle_bracket_is_read(self):
        for kind_line in ('- <strong title="a > b">Kind:</strong> deferral', "- <b title='x > y'>Kind:</b> deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-115 — quoted attribute\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-115: trigger first-outside-participant is true")

    def test_html_inside_a_backtick_run_does_not_become_a_fence(self):
        odd_line = '```<b title="`">x</b>\n'
        debt = ("# Technical Debt Log\n\n" + odd_line + "\n" + debt_entry(116, due="first-outside-participant")
                + "```\n" + odd_line + "```\n")
        code, out = self.run_validator(profile_text(TRIAL), debt, strict=True)
        self.assert_fail(out, code, "TD-116: trigger first-outside-participant is true")

    def test_label_case_is_ignored(self):
        entry = ("## TD-117 — lower case\n\n- **status:** open\n- **kind:** deferral\n- **CONTROL:** #23 rate limiting\n"
                 "- **due-before:** first-outside-participant\n- **Review-By:** 2027-01-01\n- **closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
        self.assert_fail(out, code, "TD-117: trigger first-outside-participant is true")

    def test_emphasized_label_without_colon_fails_loudly(self):
        entry = "## TD-118 — no colon\n\n- **Status:** open\n    - **Kind** deferral\n    - __control__ floor: secrets\n"
        code, out = self.run_validator(profile_text(), entry)
        self.assert_fail(out, code, "TD-118: field label(s) found on lines the validator does not read as fields: Kind Control")

    def test_closing_markup_before_the_colon_fails_loudly(self):
        for kind_line in ("- *Kind*: deferral", "- _Kind_: deferral", "- <em>Kind</em>: deferral", "- <i>Kind</i>: deferral", "\t**Kind**: deferral", "**Kind**: deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-119 — markup before colon\n\n- **Status:** open\n" + kind_line + "\n- **Control:** floor: secrets\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assertEqual(code, 1, out)
                self.assertTrue("TD-119: field label(s) found on lines the validator does not read as fields" in out, out)

    def test_code_and_link_wrapped_labels_are_read(self):
        for kind_line in ("- **`Kind`:** deferral", "- **[Kind](#kind):** deferral", "- [**Kind**](#kind): deferral"):
            with self.subTest(kind_line=kind_line):
                entry = ("## TD-120 — wrapped label\n\n- **Status:** open\n" + kind_line + "\n- **Control:** #23 rate limiting\n"
                         "- **Due-before:** first-outside-participant\n- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-120: trigger first-outside-participant is true")

    def test_deferral_fields_without_kind_fail(self):
        entry = ("## TD-121 — no kind\n\n- **Status:** open\n- **Control:** floor: secrets\n- **Due-before:** first-outside-participant\n"
                 "- **Review-by:** 2027-01-01\n- **Closure-evidence:** a test\n")
        code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
        self.assert_fail(out, code, "TD-121: carries deferral fields (Control, Due-before, Review-by, or Closure-evidence) but no Kind line")
        self.assertNotIn("has no deferrals", out)

    def test_legacy_entry_with_status_and_severity_only_is_still_legacy(self):
        legacy = "## TD-122 — legacy\n\n- **Logged:** 2026-01-01\n- **Status:** open\n- **Severity:** low\n- **Proposed fix:** later\n"
        code, out = self.run_validator(profile_text(), legacy)
        self.assert_clean(out, code)
        self.assertIn("TECHNICAL-DEBT.md has no deferrals", out)

    def test_mid_sentence_italics_are_not_labels(self):
        entry = debt_entry(123, due="public-access").rstrip("\n") + "\n\n### Follow-up\n\nWe reworked the *control* flow and the *status* banner while waiting; the __kind__ of fix is open.\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_clean(out, code)

    def test_every_stray_label_on_a_line_is_named(self):
        entry = debt_entry(124, due="public-access").rstrip("\n") + "\n\n### Follow-up\n\nSee *Kind*: deferral, _Control_: #23 and **Due-before**: soon.\n\n"
        code, out = self.run_validator(profile_text(TRIAL), entry)
        self.assert_fail(out, code, "TD-124: field label(s) found on lines the validator does not read as fields: Kind Control Due-before")

    def test_unknown_kind_value_suppresses_the_pass_line(self):
        code, out = self.run_validator(profile_text(), debt_entry(125, kind="Deferral"))
        self.assert_fail(out, code, 'TD-125: Kind is "Deferral"; expected shortcut or deferral (lower case)')
        self.assertNotIn("has no deferrals", out)

    def test_blank_deferral_fields_without_kind_still_fail(self):
        for body in ("- <code>Kind</code>: deferral\n- **Due-before:**\n", "- **Control:**\n", "- **Review-by:**   \n", "- **Closure-evidence:**\n", "- **Due-before:**\n- **Control:**\n"):
            with self.subTest(body=body.replace("\n", "|")):
                entry = "## TD-126 — blank metadata\n\n- **Status:** open\n" + body
                code, out = self.run_validator(profile_text(TRIAL), entry, strict=True)
                self.assert_fail(out, code, "TD-126: carries deferral fields (Control, Due-before, Review-by, or Closure-evidence) but no Kind line")
                self.assertNotIn("has no deferrals", out)

    def test_floor_item_as_shortcut_fails(self):
        code, out = self.run_validator(profile_text(), debt_entry(127, kind="shortcut", control="floor: secrets"))
        self.assert_fail(out, code, "TD-127: a floor item (secrets) is never postponed, as a deferral or as a shortcut")
        self.assertNotIn("has no deferrals", out)

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
