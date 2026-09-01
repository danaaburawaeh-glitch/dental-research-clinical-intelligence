"""
evidence/search_builder.py  —  SEARCH QUALITY (v1.2)

Builds PubMed queries that stay attached to the question they came from.

THE FAILURE THIS FIXES
----------------------
v1.1.0's live validation recorded it precisely (connector-capability-map.md, T1 test 7): the
query "zzqxdental unobtainium periodontal flurbotron" returned 149,830 matches over the remote
transport, because the terms were OR-expanded rather than phrase-searched. A large result count
on a nonsense phrase is not a body of evidence; it is the search falling apart quietly, in the
one direction that looks like success.

Two structural rules prevent it:

  1. **OR within a concept, AND between concepts.** Synonyms of "veneer" are alternatives to each
     other. "Veneer" and "survival" are not. A flat OR across concepts retrieves everything about
     either, which is why an over-broad query returns six figures of results and a reviewer
     concludes the topic is well studied.

  2. **Multi-word free-text terms are phrase-quoted.** `"minimally invasive veneer"` is one
     concept; `minimally AND invasive AND veneer` is three, matching papers containing all three
     words anywhere.

WHAT IS ALWAYS VISIBLE
----------------------
The user's own words survive into the log verbatim, as `user_concept`, next to the built query.
A clinician reading a search log needs to see whether the question they asked is the question
that was searched — a translated MeSH string alone hides the answer to that.
"""
import _paths  # noqa: F401

import datetime
import os
import re

# The PubMed publication-type vocabulary is loaded from the connector that owns it, by explicit
# file path rather than by adding connectors/pubmed to sys.path — that directory holds generic
# module names (models, errors, parser, rate_limit) which would shadow same-named modules
# elsewhere in the plugin for every later import.
import importlib.util as _importlib_util

_pubmed_models_path = os.path.join(_paths.CONNECTORS_DIR, "pubmed", "models.py")
_spec = _importlib_util.spec_from_file_location("pubmed_models", _pubmed_models_path)
_pubmed_models = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_pubmed_models)
build_publication_type_filter = _pubmed_models.build_publication_type_filter

# Concept slots. PICO plus the two dental-specific ones the plugin's question formulation uses.
POPULATION = "population"
INTERVENTION = "intervention"
COMPARATOR = "comparator"
OUTCOME = "outcome"
MATERIAL = "material"
CONTEXT = "context"
CONCEPT_SLOTS = (POPULATION, INTERVENTION, COMPARATOR, OUTCOME, MATERIAL, CONTEXT)

# Above this many alternatives in a single concept, the concept is flagged as broadening. Not a
# hard limit — some concepts genuinely have many synonyms — but a flag the log carries.
SYNONYM_WARNING_THRESHOLD = 8

FIELD_TIAB = "Title/Abstract"
FIELD_MESH = "MeSH Terms"
FIELD_ALL = "All Fields"


class Concept:
    """One PICO element: the user's own words, its synonyms, and its MeSH terms."""

    def __init__(self, slot, user_terms, synonyms=None, mesh_terms=None, field=FIELD_TIAB):
        if slot not in CONCEPT_SLOTS:
            raise ValueError(f"{slot!r} is not one of {CONCEPT_SLOTS}")
        if not user_terms:
            raise ValueError("A concept must carry at least one term from the user's question.")
        self.slot = slot
        self.user_terms = [user_terms] if isinstance(user_terms, str) else list(user_terms)
        self.synonyms = list(synonyms or [])
        self.mesh_terms = list(mesh_terms or [])
        self.field = field

    @property
    def alternatives(self):
        return self.user_terms + self.synonyms

    def to_query(self):
        """OR the alternatives together — and only the alternatives. Free-text terms are
        phrase-quoted and field-restricted; MeSH terms use the MeSH field."""
        parts = [f'"{_clean(t)}"[{self.field}]' for t in self.alternatives if _clean(t)]
        parts += [f'"{_clean(m)}"[{FIELD_MESH}]' for m in self.mesh_terms if _clean(m)]
        if not parts:
            return None
        if len(parts) == 1:
            return parts[0]
        return "(" + " OR ".join(parts) + ")"

    def to_dict(self):
        return {"slot": self.slot, "user_terms": list(self.user_terms),
                "synonyms": list(self.synonyms), "mesh_terms": list(self.mesh_terms),
                "field": self.field, "query_fragment": self.to_query(),
                "alternative_count": len(self.alternatives) + len(self.mesh_terms)}


def _clean(term):
    return re.sub(r'["\[\]]', "", str(term or "")).strip()


class SearchStrategy:
    """A built query, everything that shaped it, and the result of running it."""

    def __init__(self, question, concepts, database="PubMed", study_type=None,
                 date_range=None, language=None, language_justification=None,
                 max_results=20):
        self.question = question
        self.concepts = list(concepts)
        self.database = database
        self.study_type = study_type
        self.date_range = date_range
        self.language = language
        self.language_justification = language_justification
        self.max_results = max_results
        self.date_searched = None
        self.result_count = None
        self.results_screened = None
        self.studies_included = None
        self.connector_status = None
        self.query_translation = None

    # ── Query construction ──────────────────────────────────────────────────────────────────
    @property
    def user_concept(self):
        """The user's own words, preserved verbatim, per the brief's visibility requirement."""
        return " · ".join(" / ".join(c.user_terms) for c in self.concepts)

    def build(self):
        fragments = [c.to_query() for c in self.concepts]
        fragments = [f for f in fragments if f]
        if not fragments:
            raise ValueError("No searchable concept was supplied.")
        query = " AND ".join(fragments)
        filter_clause = build_publication_type_filter(self.study_type) if self.study_type else None
        if filter_clause:
            query = f"({query}) AND ({filter_clause})"
        if self.language:
            query = f"({query}) AND {self.language}[Language]"
        return query

    def filters(self):
        out = {}
        if self.study_type:
            out["publication_type"] = self.study_type
            out["publication_type_clause"] = build_publication_type_filter(self.study_type)
        if self.date_range:
            out["date_range"] = f"{self.date_range[0]} to {self.date_range[1]}"
        if self.language:
            out["language"] = self.language
            out["language_justification"] = self.language_justification or (
                "NOT STATED — a language filter without a justification is a limitation, not a "
                "refinement. It excludes evidence and must be declared as such.")
        return out

    # ── Validation ──────────────────────────────────────────────────────────────────────────
    def validate(self):
        """Structural checks against over-broad expansion. Returns a list of warnings; an empty
        list means the query is well-formed, not that it is a good query."""
        warnings = []
        query = self.build()

        # A top-level OR joining different concepts is the specific defect this module exists to
        # prevent. Detected by depth-tracking rather than by a regex, so a legitimate OR inside a
        # concept's parentheses is not mistaken for one.
        if _has_top_level_or(query):
            warnings.append({
                "severity": "CRITICAL",
                "issue": "TOP_LEVEL_OR",
                "detail": ("Distinct concepts are joined by OR at the top level of the query. "
                           "This retrieves everything matching any concept and inflates the "
                           "result count without adding relevant evidence. Concepts are joined "
                           "by AND; only synonyms within a concept are joined by OR."),
            })

        for concept in self.concepts:
            count = len(concept.alternatives) + len(concept.mesh_terms)
            if count > SYNONYM_WARNING_THRESHOLD:
                warnings.append({
                    "severity": "WARNING", "issue": "BROAD_CONCEPT",
                    "detail": (f"The {concept.slot} concept carries {count} alternatives. Each "
                               f"one widens the retrieval; check they are genuine synonyms of the "
                               f"same idea rather than related but different concepts."),
                })
            for term in concept.alternatives:
                if " " in str(term) and f'"{_clean(term)}"' not in query:
                    warnings.append({
                        "severity": "CRITICAL", "issue": "UNQUOTED_PHRASE",
                        "detail": (f"Multi-word term {term!r} is not phrase-quoted and will match "
                                   f"its words separately anywhere in a record."),
                    })

        if not any(c.mesh_terms for c in self.concepts):
            warnings.append({
                "severity": "NOTE", "issue": "NO_MESH",
                "detail": ("No MeSH term was used. The search is a targeted/exploratory search, "
                           "not a systematic one — describe it as such "
                           "(search-strategy.md's hard rule)."),
            })

        if self.language and not self.language_justification:
            warnings.append({
                "severity": "WARNING", "issue": "UNJUSTIFIED_LANGUAGE_FILTER",
                "detail": ("A language filter is applied without a stated justification. It "
                           "excludes evidence and must be declared as a limitation."),
            })
        return warnings

    @property
    def is_systematic(self):
        """search-strategy.md's hard rule, in code: 'systematic' requires MeSH, filters, and a
        complete log. Anything short of that is a targeted search and is described as one."""
        return bool(
            any(c.mesh_terms for c in self.concepts)
            and self.filters()
            and self.date_searched
            and self.result_count is not None
            and self.results_screened is not None
            and self.studies_included is not None
        )

    def record_result(self, result_count, connector_status, date_searched=None,
                      results_screened=None, studies_included=None, query_translation=None):
        self.result_count = result_count
        self.connector_status = connector_status
        self.date_searched = date_searched or datetime.date.today().isoformat()
        self.results_screened = results_screened
        self.studies_included = studies_included
        self.query_translation = query_translation
        return self

    # ── Reporting ───────────────────────────────────────────────────────────────────────────
    def to_dict(self):
        return {
            "question": self.question,
            "user_concept": self.user_concept,
            "database": self.database,
            "exact_query": self.build(),
            "query_translation": self.query_translation,
            "filters": self.filters(),
            "date_searched": self.date_searched,
            "result_count": self.result_count,
            "results_screened": self.results_screened,
            "studies_included": self.studies_included,
            "connector_status": self.connector_status,
            "concepts": [c.to_dict() for c in self.concepts],
            "warnings": self.validate(),
            "search_type": "systematic" if self.is_systematic else "targeted/exploratory",
        }

    def to_markdown(self):
        d = self.to_dict()
        rows = [
            "| Field | Value |", "|---|---|",
            f"| Question | {d['question']} |",
            f"| User's own terms (verbatim) | {d['user_concept']} |",
            f"| Database | {d['database']} |",
            f"| Exact query | `{d['exact_query']}` |",
            f"| PubMed's translation | {d['query_translation'] or 'not recorded'} |",
            f"| Filters | {d['filters'] or 'none'} |",
            f"| Date searched | {d['date_searched'] or 'NOT RUN'} |",
            f"| Results retrieved | {d['result_count'] if d['result_count'] is not None else 'NOT RUN'} |",
            f"| Results screened | {d['results_screened'] if d['results_screened'] is not None else 'not recorded'} |",
            f"| Studies included | {d['studies_included'] if d['studies_included'] is not None else 'not recorded'} |",
            f"| Connector status | {d['connector_status'] or 'NOT RUN'} |",
            f"| Search type | {d['search_type']} |",
        ]
        out = "\n".join(rows)
        if d["warnings"]:
            out += "\n\n**Search-quality warnings**\n\n" + "\n".join(
                f"- **{w['severity']}** ({w['issue']}): {w['detail']}" for w in d["warnings"])
        return out


def _has_top_level_or(query):
    depth = 0
    tokens = re.split(r"(\(|\)|\bOR\b|\bAND\b)", query)
    for token in tokens:
        token = token.strip()
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        elif token == "OR" and depth == 0:
            return True
    return False


def from_pico(question, population=None, intervention=None, comparator=None, outcome=None,
              **kwargs):
    """Convenience constructor. Each argument is a Concept or None."""
    concepts = [c for c in (population, intervention, comparator, outcome) if c is not None]
    return SearchStrategy(question, concepts, **kwargs)
