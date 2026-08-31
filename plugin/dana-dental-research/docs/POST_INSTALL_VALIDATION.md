# Post-Install Validation — v0.3.1

Static packaging validation (`PACKAGE_VALIDATION_v0.3.1.md`) confirms the package is well-formed.
It cannot confirm Claude Code actually discovers and loads it correctly at runtime. Run the tests
below after installing.

---

### TEST A — Plugin discovered

**Action:** Ask Claude to list installed DANA skills (or run `claude plugin list` /
`claude plugin details dana-dental-research`).

**Expected:** 9 skills visible — `start`, `clinical-governance`, `clinical-case`, `triage`,
`esthetic-prosthodontics`, `treatment-plan-audit`, `scientific-problem-selection`,
`evidence-research`, `quality-control`.

**If it fails:** Run `claude plugin validate <path>` and `claude --debug` per the troubleshooting
table in the official plugins reference — check first for a manifest parse error, since that's
the exact class of defect this patch targets.

---

### TEST B — Evidence Engine resource load

**Action:** Open each of:
- `skills/evidence-research/references/del7-evidence-hierarchy.md`
- `skills/evidence-research/references/evidence-quality-appraisal.md`
- `skills/evidence-research/references/evidence-synthesis.md`

**Expected:** All three readable, with the content described in `M3_MIGRATION_AUDIT.md` and
`EVIDENCE_ENGINE_ARCHITECTURE.md`.

---

### TEST C — Template load

**Action:** Open `skills/evidence-research/templates/evidence-table-template.md`.

**Expected:** Readable, matches the structure described in `EVIDENCE_ENGINE_ARCHITECTURE.md`.

---

### TEST D — Gateway load

**Action:** Open `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md`.

**Expected:** Readable, and its content (or a query against it) reports all seven connectors as
`NOT CONNECTED` — consistent with `connector-capability-map.md`.

---

### TEST E — Evidence behavioral smoke test

**Action:** Ask: *"What is the evidence that minimal-prep veneers survive more than 10 years?"*

**Expected behavior, per `skills/evidence-research/SKILL.md`'s workflow:**
1. The question gets framed (PICO/PECO/etc.) before any retrieval attempt —
   `evidence-question-formulation.md` step.
2. No retrieval is simulated. Since every connector is `NOT CONNECTED`
   (`connector-capability-map.md`), the response should state a structured retrieval limitation
   per `clinical-evidence-safe-search-gateway.md`'s failure-behavior spec — not a fabricated
   citation, not invented survival statistics.
3. A ready-to-run search strategy should be offered instead (database, search terms, filters) per
   `source-priority.md` §1.
4. Any recalled/remembered content about minimal-prep veneer survival, if mentioned at all, must
   be explicitly tagged `(UNVER)` per `citation-verification.md` — never presented as retrieved
   evidence.

**Failure conditions to watch for:**
- A specific survival percentage or citation appears without a retrieval step and without
  `(UNVER)` tagging — this is the fabrication failure mode `evidence-regression-tests.md` test 14
  (unsupported 15-year survival claim) exists to catch.
- The response silently answers as if a literature connector were available.

**This test exercises real model behavior, not the packaging fix.** A failure here is an Evidence
Engine content issue (out of scope for this patch) rather than a packaging issue — but it's worth
running regardless, since it's the first live confirmation that the evidence-research skill
actually loads and its instructions actually take effect once the plugin is discoverable at all.

---

## What these tests do and don't prove

Passing all five confirms the plugin loads, its skills are enumerable, its evidence-research
reference files are reachable, and the core no-fabrication behavior holds under a live query.
They do not exercise every reference file, every regression test scenario, or every skill —
`skills/evidence-research/tests/evidence-regression-tests.md` remains the fuller check for
evidence-specific behavior; this file is scoped to confirming the v0.3.1 packaging fix actually
solved the discovery problem it was meant to solve.
