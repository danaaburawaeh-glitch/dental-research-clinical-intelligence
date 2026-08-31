# User Guide — English

## 1. How to think about this assistant

It is a colleague who refuses to guess. Ask it a clinical question and it will tell you what it can
conclude from what you gave it, what it cannot, what is missing, and which decision each gap would
change. It will not fill a silence with a plausible answer.

That is the whole design. Most of what follows is a consequence of it.

## 2. Starting a session

```
/dana-dental-research:start
```

Then describe your question in plain language, English or Arabic. The assistant selects the right
workflow. You can name one explicitly if you prefer — the nine skills are listed in `INSTALLATION.md`.

## 3. A clinical case

Give what you have. Incomplete is normal.

The response follows a fixed sequence: clinical question → data ledger with each item tagged →
missing data ranked by decision value → sufficiency verdict → problem list → differential →
risk → prognosis → confidence → patient factors → objectives → phased plan → alternatives →
irreversibility check → evidence → verification required → **next single step**.

Each finding is tagged:

| Tag | Meaning |
|---|---|
| `[Reported]` | The patient said it, or a record carries it — not yet clinically observed |
| `[Observed]` | Directly examined, or a documented examination finding |
| `[Inferred]` | A reasonable deduction — never a confirmed fact, and always shown with its basis |
| `[Unknown]` | Not stated, and not guessed |

**An inference never becomes a finding**, however obvious it looks. If you see `[Inferred]`, the
basis is stated next to it — check whether you agree.

## 4. Why it sometimes refuses

The assistant will block a definitive plan when:

- **Data is insufficient** for the act you asked for. Prescribing support needs allergies,
  medications, medical history and pregnancy status; any unknown among them blocks it.
- **The red-flag sweep is incomplete.** All 14 checks must be answered explicitly. A flag never
  answered is *not assessed*, not *absent*.
- **A red flag is present.** Escalation comes first, at the top of the response.
- **Prognosis is undetermined** for a tooth you want to restore.
- **The case is out of scope** — outside fixed prosthodontics and esthetic restorative dentistry.

A block is not a malfunction. It cannot be argued past, and repeating the request will not change
it. Resolve the stated cause, or refer.

## 5. Prognosis

Reported as **favorable**, **guarded**, **poor** or **undetermined** on five separate axes: tooth,
periodontal, restorative, prosthetic, and functional/occlusal. Each carries its basis, the findings
for and against, what is missing, and a confidence level.

The overall prognosis is the **worst** axis, not an average — a tooth that is periodontally sound
and restoratively hopeless is not "guarded overall".

**No percentages are ever produced.** A survival figure derived from a chairside dataset would be
an invented statistic.

## 6. Treatment planning

Plans are phased: emergency → stabilisation and disease control → re-evaluation → reversible test
phase → definitive → maintenance.

Four rules are enforced rather than suggested:

1. **Disease control before definitive prosthetics.** No definitive restoration over active caries
   or active periodontal disease.
2. **Prognosis before prosthesis.** No restoration planned onto a tooth of undetermined prognosis.
3. **A reversible test phase before irreversible esthetic work** — wax-up and mock-up, with the
   patient's approval documented.
4. **Alternatives always include no treatment and monitor/defer.**

Anything irreversible must also state expected service life, failure mode, early warning signs,
retreatability, maintenance obligation, and the cost of being wrong.

## 7. How evidence is handled

Every consequential claim carries a source tier — current guideline, systematic review, clinical
study, consensus, manufacturer instructions, clinical judgment, or unverified. Bench and in-vitro
data is marked and never supports a clinical superiority claim. Regulatory clearance is marked and
never treated as proof of efficacy.

Citations are verified across PubMed and Crossref. Retracted papers are excluded from synthesis,
not footnoted. A trial and the paper reporting it count as one study.

**If a source cannot be verified, it is labelled unverified and you are given the search to run.**
No citation is ever invented.

## 8. Saudi regulatory questions

Every regulatory statement carries one of four states: verified, requires verification, not
applicable, or unknown/conflict.

Today, SFDA lookup is not authenticated, so a Saudi product question returns **requires
verification**. FDA and CE status will be reported separately and marked non-transferable. That is
the correct answer, not a failure — verify with SFDA before purchase or clinical use.

## 9. Privacy

De-identify before you type. Use a case reference, not a name. Remember that radiographs and scans
carry hidden identifiers and that cropping a photograph does not remove its metadata.

Publication consent is separate from treatment consent, and separate again per channel. The
assistant will not produce marketing content from clinical material without you confirming, in the
same exchange, that specific written publication consent exists.

## 10. When something looks wrong

Ask it to show its reasoning and its sources. The assistant is built to disagree with you when the
data does not support a conclusion, and not to soften a safety concern because you pushed back. If
it agrees with everything you say, something is wrong — report it.

Never include patient-identifying information in a problem report.
