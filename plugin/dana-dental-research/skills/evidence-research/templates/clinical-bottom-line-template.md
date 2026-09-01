# Clinical Bottom Line

Every evidence synthesis ends here. Seven sections, per `evidence/bottom_line.py`.

## CLINICAL BOTTOM LINE

**Question:** [the framed question]

**1. What is well established**
> Requires HIGH certainty and at least PARTIALLY DIRECT evidence.

**2. What is reasonably supported**
> Requires MODERATE certainty and at least PARTIALLY DIRECT evidence.

**3. What remains uncertain**

**4. Where evidence conflicts**
> Per `evidence-conflict-resolution.md`. Never averaged.

**5. Which option currently has the strongest support**

**6. Important limitations**

**7. What additional information would change the conclusion**

---

## Why fixed sections rather than a paragraph

A prose summary of a mixed evidence base gravitates toward its strongest sentence. The parts a
clinician most needs — what is still uncertain, where good sources disagree, what would change the
answer — are the parts a fluent paragraph smooths over, because they interrupt it. Fixed sections
make omission visible: an **empty section renders an explicit statement**, so "no conflict was
identified" is a claim that conflicts were looked for.

## Sections 1 and 2 are gated by certainty, not by citation

A claim backed by a perfectly VERIFIED citation to a single small cohort belongs in section 3.
`ClinicalBottomLine.validate()` **moves** a claim that does not meet a section's certainty,
directness and citation-state requirements, and reports why it moved.

## Every number is gated

`numeric-evidence-gate.md` runs over the rendered text. Any survival %, failure %, risk ratio,
odds ratio, mean difference or confidence interval that is not registered against a retrieved,
verified source **fails the whole bottom line**.

## Each claim carries its links

Per `claim-evidence-linking.md`: design · citation state · certainty · directness · citation.
