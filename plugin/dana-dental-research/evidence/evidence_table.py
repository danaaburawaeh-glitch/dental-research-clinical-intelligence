"""
evidence/evidence_table.py  —  STANDARDIZED EVIDENCE TABLE (v1.2)

One row per source, with the fourteen columns the brief specifies:

    Study · Year · Design · N · Intervention · Comparator · Follow-up · Outcome · Effect ·
    Verification · Risk of Bias · Certainty · Directness · Key Limitation

NO CELL IS EVER BLANK
---------------------
A blank cell in an evidence table is read as "nothing notable" far more often than as "not
established", and the two are opposite meanings. Every unfilled cell therefore renders as an
explicit marker:

    NOT REPORTED  — the source was read and does not state it
    NOT AVAILABLE — the source was not read at that depth (no full text was retrieved)
    NOT ASSESSED  — this system did not assess it

The distinction is carried through from `appraisal.py` and `sr_extraction.py` rather than being
re-derived, so the table cannot claim more completeness than the extraction behind it.
"""
import _paths  # noqa: F401

import appraisal as ap
import certainty as ce
import citation_verification as cv
import directness as dr
import study_design as sd
from shared.normalization import surname as _surname

COLUMNS = ("Study", "Year", "Design", "N", "Intervention", "Comparator", "Follow-up",
           "Outcome", "Effect", "Verification", "Risk of Bias", "Certainty", "Directness",
           "Key Limitation")

NOT_REPORTED = "NOT REPORTED"
NOT_AVAILABLE = "NOT AVAILABLE"
NOT_ASSESSED = "NOT ASSESSED"


class EvidenceTableRow:
    def __init__(self, record, design_classification=None, appraisal=None,
                 certainty_assessment=None, directness_assessment=None,
                 verification=None, intervention=None, comparator=None, outcome=None,
                 effect=None, full_text_retrieved=False):
        self.record = record or {}
        self.design_classification = design_classification
        self.appraisal = appraisal
        self.certainty_assessment = certainty_assessment
        self.directness_assessment = directness_assessment
        self.verification = verification
        self.intervention = intervention
        self.comparator = comparator
        self.outcome = outcome
        self.effect = effect
        self.full_text_retrieved = full_text_retrieved

    @property
    def _absent(self):
        return NOT_REPORTED if self.full_text_retrieved else NOT_AVAILABLE

    def _field(self, name):
        """Read an appraisal field, rendering its absence with the right marker."""
        if self.appraisal is None:
            return NOT_ASSESSED
        field = getattr(self.appraisal, name, None)
        if field is None or not field.known:
            return self._absent
        return str(field.value)

    def study(self):
        record = self.record
        authors = record.get("authors") or []
        first = _surname(authors[0]) if authors else None
        first = first.title() if first else None
        ident = record.get("pmid") and f"PMID {record['pmid']}" or record.get("doi") or ""
        if first:
            return f"{first} et al. {ident}".strip()
        return record.get("title") or ident or "unidentified record"

    def year(self):
        return str(self.record.get("publication_year") or self._absent)

    def design(self):
        if self.design_classification is None:
            return NOT_ASSESSED
        text = self.design_classification.design
        if self.design_classification.provenance == sd.INFERRED:
            text += " (inferred from text)"
        if self.design_classification.registry_only:
            text += f" — {sd.REGISTRY_LABEL}"
        elif self.design_classification.lab_firewall:
            text += " — LAB"
        return text

    def n(self):
        for name in ("sample_size", "number_of_participants"):
            value = self._field(name)
            if value not in (NOT_REPORTED, NOT_AVAILABLE, NOT_ASSESSED):
                return value
        return self._absent

    def follow_up(self):
        return self._field("follow_up")

    def risk_of_bias(self):
        if self.appraisal is None:
            return NOT_ASSESSED
        field = self.appraisal.risk_of_bias
        if not field.known:
            return NOT_ASSESSED
        value = field.value
        if isinstance(value, dict):
            tool = value.get("tool")
            overall = value.get("overall") or NOT_REPORTED
            return f"{overall} ({tool})" if tool else f"{overall} (no formal tool applied)"
        return str(value)

    def certainty(self):
        if self.certainty_assessment is None:
            return NOT_ASSESSED
        rating = self.certainty_assessment.rating
        if self.certainty_assessment.author_grade is not None:
            return (f"{rating} (this system) · "
                    f"{self.certainty_assessment.author_grade.rating} "
                    f"({ce.AUTHOR_GRADE_LABEL})")
        return rating

    def directness(self):
        if self.directness_assessment is None:
            return NOT_ASSESSED
        verdict = self.directness_assessment.verdict
        if self.directness_assessment.was_capped:
            verdict += f" (capped from {self.directness_assessment.capped_from})"
        return verdict

    def verification_state(self):
        if self.verification is None:
            return NOT_ASSESSED
        state = self.verification.get("state") if isinstance(self.verification, dict) \
            else self.verification
        if isinstance(self.verification, dict) and \
                state == cv.VERIFIED_WITH_METADATA_DISCREPANCY:
            fields = ", ".join(d["field"] for d in self.verification.get("discrepancies", []))
            return f"{state} ({fields})"
        return state

    def key_limitation(self):
        value = self._field("major_limitations")
        if value in (NOT_REPORTED, NOT_AVAILABLE, NOT_ASSESSED):
            # A design-level limitation is always available even when nothing was extracted.
            if self.design_classification is not None and \
                    not self.design_classification.supports_clinical_outcome_claims:
                return (sd.REGISTRY_LABEL if self.design_classification.registry_only
                        else "Laboratory evidence — no patient outcomes")
        return value

    def cells(self):
        return {
            "Study": self.study(),
            "Year": self.year(),
            "Design": self.design(),
            "N": self.n(),
            "Intervention": self.intervention or self._absent,
            "Comparator": self.comparator or self._absent,
            "Follow-up": self.follow_up(),
            "Outcome": self.outcome or self._absent,
            "Effect": self.effect or self._absent,
            "Verification": self.verification_state(),
            "Risk of Bias": self.risk_of_bias(),
            "Certainty": self.certainty(),
            "Directness": self.directness(),
            "Key Limitation": self.key_limitation(),
        }


class EvidenceTable:
    def __init__(self, rows=None, question=None):
        self.rows = list(rows or [])
        self.question = question

    def add(self, row):
        self.rows.append(row)
        return row

    def to_dict(self):
        return {"question": self.question, "columns": list(COLUMNS),
                "rows": [r.cells() for r in self.rows],
                "blank_cell_policy": (
                    "No cell is left blank. NOT REPORTED means the source does not state it; "
                    "NOT AVAILABLE means the source was not read at that depth; NOT ASSESSED "
                    "means this system did not assess it.")}

    def to_markdown(self):
        lines = []
        if self.question:
            lines += [f"**Question:** {self.question}", ""]
        lines.append("| " + " | ".join(COLUMNS) + " |")
        lines.append("|" + "|".join("---" for _ in COLUMNS) + "|")
        for row in self.rows:
            cells = row.cells()
            lines.append("| " + " | ".join(
                str(cells[c]).replace("|", "\\|").replace("\n", " ") for c in COLUMNS) + " |")
        lines += ["", "_No cell is left blank. NOT REPORTED = the source does not state it; "
                      "NOT AVAILABLE = the source was not read at that depth; NOT ASSESSED = "
                      "this system did not assess it._"]
        return "\n".join(lines)

    def audit(self):
        """Every row must carry a verification state, a certainty and a directness — the three
        columns that stop the table being a bibliography with extra whitespace."""
        problems = []
        for row in self.rows:
            cells = row.cells()
            for column in ("Verification", "Certainty", "Directness"):
                if cells[column] == NOT_ASSESSED:
                    problems.append({
                        "study": cells["Study"], "column": column,
                        "reason": (f"{column} was never assessed for this row. A source in an "
                                   f"evidence table without it cannot be weighed by the reader."),
                    })
        return {"result": "FAIL" if problems else "PASS", "problems": problems}
