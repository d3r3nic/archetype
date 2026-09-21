#!/usr/bin/env node
/*
 * DOM regression tests for templates/design-interview/index.html.
 *
 * Run with happy-dom available to Node:
 *   node scripts/test-design-interview.mjs
 * Or point to an existing test-only installation without adding a product dependency:
 *   HAPPY_DOM_ENTRY=/absolute/path/to/happy-dom/lib/index.js node scripts/test-design-interview.mjs
 */

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

async function loadHappyDom() {
  try {
    return await import('happy-dom');
  } catch (error) {
    if (process.env.HAPPY_DOM_ENTRY) {
      return import(pathToFileURL(path.resolve(process.env.HAPPY_DOM_ENTRY)).href);
    }
    throw new Error(
      'happy-dom is required only to run this DOM test. Make it available to Node, or set ' +
      'HAPPY_DOM_ENTRY to its lib/index.js. The interview form has no runtime dependencies.',
      { cause: error }
    );
  }
}

const { Window } = await loadHappyDom();
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const formPath = path.join(root, 'templates/design-interview/index.html');
const source = fs.readFileSync(formPath, 'utf8');
const prefillMarker = '<script type="application/json" id="prefill">{}</script>';

function openForm(prefill) {
  assert.equal(
    source.split(prefillMarker).length - 1,
    1,
    'the documented prefill block must remain present exactly once'
  );
  const html = source.replace(
    prefillMarker,
    `<script type="application/json" id="prefill">${JSON.stringify(prefill)}</script>`
  );

  const window = new Window({
    settings: {
      disableJavaScriptEvaluation: false,
      disableJavaScriptFileLoading: true,
      disableCSSFileLoading: true
    }
  });
  window.document.write(html);
  window.document.close();

  // happy-dom does not execute scripts inserted by document.write. Execute the
  // shipped inline script verbatim after parsing the shipped HTML.
  const scripts = [...window.document.querySelectorAll('script:not([type])')];
  assert.equal(scripts.length, 1, 'the form must have one executable inline script');
  window.eval(scripts[0].textContent);

  function choosePath(pathName) {
    const input = window.document.querySelector(`input[name="path"][value="${pathName}"]`);
    assert.ok(input, `path option ${pathName} must exist`);
    input.click();
  }

  function serialize() {
    window.document.getElementById('make').click();
    const output = window.document.getElementById('out').value;
    const fields = {};
    for (const line of output.split('\n')) {
      if (!line.startsWith('- ')) continue;
      const separator = line.indexOf(': ');
      fields[line.slice(2, separator)] = line.slice(separator + 2);
    }
    return fields;
  }

  return {
    window,
    choosePath,
    serialize,
    note: window.document.getElementById('prefill-note')
  };
}

function isShown(element) {
  for (let node = element; node; node = node.parentNode) {
    if (node.hidden) return false;
  }
  return true;
}

const supplied = {
  path: 'pick-for-me',
  business: 'Scratch shift board',
  existing: 'none',
  needs: 'keyboard only',
  languages: 'Spanish',
  rules_gate: 'some',
  rules: 'Parent brand constraints',
  print: 'yes',
  spend: 'free-only'
};
const expectedConstraints = {
  needs: supplied.needs,
  languages: supplied.languages,
  rules: supplied.rules,
  print: supplied.print,
  spend: supplied.spend
};

const unstarted = openForm({});
assert.equal(
  isShown(unstarted.window.document.querySelector('input[name="path"]')),
  true,
  'the path choice must be visible before a path is selected'
);
assert.equal(
  isShown(unstarted.window.document.querySelector('input[name="needs"]')),
  false,
  'practical constraints must wait until a path is selected'
);
unstarted.choosePath('pick-for-me');
assert.equal(
  isShown(unstarted.window.document.querySelector('input[name="needs"]')),
  true,
  'practical constraints must appear on the delegated path'
);

const delegated = openForm(supplied);
assert.equal(delegated.note.hidden, true, 'valid known prefill fields must not warn');
assert.deepEqual(
  Object.fromEntries(Object.entries(delegated.serialize()).filter(([key]) => key in expectedConstraints)),
  expectedConstraints,
  'the delegated path must preserve supplied requirements'
);

delegated.choosePath('my-ideas');
assert.deepEqual(
  Object.fromEntries(Object.entries(delegated.serialize()).filter(([key]) => key in expectedConstraints)),
  expectedConstraints,
  'switching to owner preferences must preserve supplied requirements'
);

delegated.choosePath('pick-for-me');
assert.deepEqual(
  Object.fromEntries(Object.entries(delegated.serialize()).filter(([key]) => key in expectedConstraints)),
  expectedConstraints,
  'switching back to delegation must preserve supplied requirements'
);

for (const pathName of ['pick-for-me', 'my-ideas']) {
  const blankSpend = openForm({ path: pathName, business: 'Scratch shift board', existing: 'none' });
  assert.equal(blankSpend.serialize().spend, 'ask-me', `blank spend must become ask-me on ${pathName}`);
}

const unknown = openForm({ ...supplied, not_a_form_key: 'must warn' });
assert.equal(unknown.note.hidden, false, 'an unknown prefill key must warn');
assert.match(unknown.note.textContent, /not_a_form_key/, 'the warning must name the unknown key');

const inferredRules = openForm({
  path: 'pick-for-me',
  business: 'Scratch shift board',
  existing: 'none',
  rules: 'Parent brand constraints'
});
assert.equal(inferredRules.note.hidden, true, 'a supplied rules fact must infer its omitted gate');
assert.equal(inferredRules.serialize().rules, 'Parent brand constraints', 'inferred rules must serialize');

const conflictingRules = openForm({
  path: 'pick-for-me',
  business: 'Scratch shift board',
  existing: 'none',
  rules_gate: 'none',
  rules: 'Parent brand constraints'
});
assert.equal(conflictingRules.note.hidden, false, 'a rules fact that conflicts with its gate must warn');
assert.match(conflictingRules.note.textContent, /rules_gate/, 'the warning must name the conflicting gate');
assert.equal(
  conflictingRules.serialize().rules,
  'Parent brand constraints',
  'a conflicting gate must not replace supplied rules with none'
);

const singleScheme = openForm({
  path: 'my-ideas',
  business: 'Scratch shift board',
  existing: 'none',
  color_gate: 'i-have-views',
  scheme: 'light'
});
singleScheme.serialize();
assert.equal(
  singleScheme.window.document.getElementById('result').hidden,
  true,
  'a single scheme without its reason must not produce final answers'
);
assert.equal(
  singleScheme.window.document.getElementById('answer-note').hidden,
  false,
  'a missing single-scheme reason must be explained in the form'
);
const schemeReason = singleScheme.window.document.getElementById('scheme_reason');
assert.equal(isShown(schemeReason), true, 'the reason field must appear for a single scheme');
schemeReason.value = 'The workstations are always used in bright rooms';
assert.equal(
  singleScheme.serialize().scheme_reason,
  'The workstations are always used in bright rooms',
  'a supplied single-scheme reason must serialize'
);

for (const scheme of ['both', 'you-choose']) {
  const noReasonNeeded = openForm({
    path: 'my-ideas',
    business: 'Scratch shift board',
    existing: 'none',
    color_gate: 'i-have-views',
    scheme
  });
  const fields = noReasonNeeded.serialize();
  assert.equal(noReasonNeeded.window.document.getElementById('result').hidden, false, `${scheme} must finalize`);
  assert.equal(fields.scheme_reason, undefined, `${scheme} must not emit a scheme reason`);
}

const hiddenScheme = openForm({
  path: 'pick-for-me',
  business: 'Scratch shift board',
  existing: 'none',
  scheme: 'light'
});
const hiddenSchemeFields = hiddenScheme.serialize();
assert.equal(
  hiddenScheme.window.document.getElementById('result').hidden,
  false,
  'a hidden stale scheme must not block the delegated path'
);
assert.equal(hiddenSchemeFields.scheme, undefined, 'a hidden stale scheme must not serialize');
assert.equal(hiddenSchemeFields.scheme_reason, undefined, 'a hidden stale scheme reason must not serialize');

console.log('PASS: delegated and owner-choice paths preserve requirements through path changes');
console.log('PASS: the path choice appears first and reveals shared practical constraints');
console.log('PASS: blank spend serializes as ask-me on both paths');
console.log('PASS: unknown prefill keys remain visible warnings');
console.log('PASS: supplied rules infer their gate and conflicting gates warn without losing the fact');
console.log('PASS: a single scheme requires its reason; both and you-choose do not');
