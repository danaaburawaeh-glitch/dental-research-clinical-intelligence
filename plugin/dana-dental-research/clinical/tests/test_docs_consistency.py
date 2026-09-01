"""
clinical/tests/test_docs_consistency.py

v0.9.2 — documentation-consistency regression.

Catches the defect class that produced the v0.9.1 P1 blocker: a statement true of an earlier
release surviving into a shipped document where it reads as a current system-state claim.

The rule this enforces is not "never mention the old state". History must be preserved. The rule
is: a historical statement must be marked historical, and every *current* operational reference
must reflect current reality.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(os.path.dirname(HERE))
DOCS = os.path.join(PLUGIN, "docs")
SKILLS = os.path.join(PLUGIN, "skills")

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def read(*p):
    return io.open(os.path.join(*p), encoding="utf-8").read()


GAPS = read(DOCS, "UNRESOLVED_GAPS.md")
CAP = read(SKILLS, "start", "references", "connector-capability-map.md")

CONNECTED = {
    "~~literature": "CONNECTED — PubMed/NCBI",
    "~~systematic-reviews": "CONNECTED — PubMed filtered retrieval",
    "~~journal-access": "CONNECTED — METADATA/CITATION VERIFICATION via Crossref",
    "~~clinical-trials": "CONNECTED — ClinicalTrials.gov API v2",
}
NOT_CONNECTED = {
    "~~clinical-guidelines": "NOT CONNECTED",
    "~~manufacturer-ifu": "NOT CONNECTED",
    "~~regulatory-saudi": "NOT CONNECTED — AUTH REQUIRED",
}

# ── 1. Historical sectioning ────────────────────────────────────────────────
check("01 gaps file separates current from historical",
      "# PART A — CURRENT RELEASE STATE" in GAPS and "# PART B — HISTORICAL / RESOLVED" in GAPS)
check("02 title names the current release, not v0.3",
      GAPS.splitlines()[0].strip() == "# Unresolved Gaps — Current Release (v0.9.2)")
check("03 Part B is explicitly not a current claim",
      "Nothing in Part B is a claim about" in GAPS)
check("04 every historical entry carries a status label",
      all(re.search(rf"\*\*{h} ·.*?(RESOLVED|SUPERSEDED|HISTORICAL)", GAPS, re.S)
          for h in re.findall(r"\*\*(H\d\d) ·", GAPS)))

# ── 2. The false connector claim is gone from current state ─────────────────
part_a = GAPS[GAPS.index("# PART A"):GAPS.index("# PART B")]
check("05 'No connector is actually wired' absent from Part A",
      "No connector is actually wired" not in part_a)
check("06 the false claim survives only as a marked-resolved historical entry",
      "No connector is actually wired" in GAPS and "H02" in GAPS
      and "RESOLVED, and the entry was FALSE" in GAPS)
check("07 Part A states the real connector status",
      all(v in part_a for v in CONNECTED.values()))
check("08 not-connected placeholders stated correctly",
      all(k in part_a for k in NOT_CONNECTED))
check("09 regulatory-saudi shown as AUTH REQUIRED",
      "NOT CONNECTED — AUTH REQUIRED" in part_a)
check("10 Crossref never described as full text",
      "CONNECTED — FULL TEXT" not in GAPS
      and "does not provide full\ntext" in GAPS.replace("\r", ""))

# ── 3. Gaps file agrees with the capability map ─────────────────────────────
def map_status(text, key):
    m = re.search(rf"^\| `{re.escape(key)}` \|.*", text, re.M)
    if not m:
        return None
    mm = re.search(r"\*\*([^*]+)\*\*", m.group(0).split("|")[4])
    return mm.group(1).strip().rstrip(".") if mm else None


mismatch = []
for k, v in {**CONNECTED, **NOT_CONNECTED}.items():
    got = map_status(CAP, k)
    if got != v:
        mismatch.append((k, got, v))
check("11 capability map matches the declared current state", not mismatch, str(mismatch))
check("12 both capability-map copies agree",
      read(SKILLS, "start", "references", "connector-capability-map.md").count("CONNECTED")
      == read(SKILLS, "evidence-research", "references",
              "connector-capability-map.md").count("CONNECTED"))

# ── 4. Clinical Protocol status ─────────────────────────────────────────────
check("13 gaps file states v1.3 APPROVED", "Clinical Protocol v1.3 — APPROVED" in GAPS)
check("14 CLINICAL-PROTOCOL-08 no longer a current gap",
      "CLINICAL-PROTOCOL-08" not in part_a)
check("15 it appears as resolved history",
      "H01 · CLINICAL-PROTOCOL-08" in GAPS and "RESOLVED" in GAPS)
check("16 no current reference calls the protocol a draft",
      "working draft" not in part_a.lower())

# ── 5. Numbering hygiene ────────────────────────────────────────────────────
gids = re.findall(r"\*\*(G\d\d) ·", GAPS)
hids = re.findall(r"\*\*(H\d\d) ·", GAPS)
check("17 current gap IDs unique", len(gids) == len(set(gids)), str(len(gids)))
check("18 historical IDs unique", len(hids) == len(set(hids)), str(len(hids)))
check("19 no legacy numbered-list items remain",
      not re.search(r"^\d+\. \*\*", GAPS, re.M))
check("20 NCT linkage appears exactly once as a current gap",
      len(re.findall(r"\*\*G\d\d · PubMed `<DataBankList>`", GAPS)) == 1)
check("21 the previous triplication is acknowledged",
      "previously appeared three times" in GAPS)
check("22 enhancement register renamed away from P#",
      "| E1 |" in GAPS and "| P1 |" not in GAPS)

# ── 6. Classification ───────────────────────────────────────────────────────
a2 = GAPS[GAPS.index("## A.2"):GAPS.index("## A.3")]
a3 = GAPS[GAPS.index("## A.3"):GAPS.index("## A.4")]
check("23 every current gap is classified P2 or P3",
      len(re.findall(r"\*\*G\d\d ·", a2)) + len(re.findall(r"\*\*G\d\d ·", a3)) == len(gids))
# Anchored to headings: an unanchored `##.*P[01]` matched the literal "G##" in prose.
check("24 no current gap is classified P0 or P1",
      not re.search(r"^#+ .*\bP[01]\b", GAPS, re.M))
check("25 P2 section is labelled non-blocking",
      "P2 (non-blocking improvements)" in GAPS)

# ── 7. Whole-package current-state contradictions ───────────────────────────
FORBIDDEN_CURRENT = (
    "No connector is actually wired",
    "fully `NOT CONNECTED` state",
    "no network access",
    "has NOT been run against the live network",
)
HISTORICAL_MARKERS = ("HISTORICAL", "SUPERSEDED", "RESOLVED", "PART B", "was FALSE",
                      "no longer", "withdrawn", "STATUS UPDATE", "ADDENDUM",
                      "original", "Original", "earlier release", "at the time")
unmarked = []
for base in (DOCS, SKILLS):
    for root, _d, files in os.walk(base):
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, PLUGIN)
            t = read(path)
            for phrase in FORBIDDEN_CURRENT:
                if phrase in t and not any(m in t for m in HISTORICAL_MARKERS):
                    unmarked.append((rel, phrase))
check("26 no unmarked stale current-state claim anywhere", not unmarked, str(unmarked[:3]))

check("27 no shipped doc still titled as a v0.3 index",
      not any(read(DOCS, f).splitlines()[0].strip().endswith("— v0.3")
              for f in os.listdir(DOCS) if f.endswith(".md")))

manifest = json.loads(read(PLUGIN, ".claude-plugin", "plugin.json"))
check("28 manifest version marks this tree as v1.2 development, not public v1.1.0",
      manifest["version"] == "1.2.0-development", manifest["version"])
check("29 manifest describes the connected set accurately",
      "~~clinical-trials" in manifest["description"]
      and "AUTH REQUIRED" in manifest["description"])
check("30 creator attribution preserved", "Dana" in manifest["author"]["name"])
check("31 display name set, internal id unchanged",
      manifest["displayName"] == "Dental Research & Clinical Intelligence by Dr. Dana"
      and manifest["name"] == "dana-dental-research")
check("32 README exists and leads with the display name",
      read(PLUGIN, "README.md").startswith(
          "# Dental Research & Clinical Intelligence by Dr. Dana"))
check("33 README connector table matches the current state",
      all(v in read(PLUGIN, "README.md") for v in CONNECTED.values()))
check("34 README does not describe Crossref as full text",
      "full text" in read(PLUGIN, "README.md")
      and "never full text" in read(PLUGIN, "README.md"))

# ── 8. Remote MCP transport (v1.1.0) ───────────────────────────────────────
MCP_URL = "https://dental-ai-research-mcp.onrender.com/mcp"
MCP_SERVER = "dental-ai-research"
mcp = json.loads(read(PLUGIN, ".mcp.json"))
srv = mcp.get("mcpServers", {}).get(MCP_SERVER, {})
check("35 remote MCP server declared in .mcp.json",
      srv.get("type") == "http" and srv.get("url") == MCP_URL, str(mcp))
check("36 transport rules reference exists and is loaded by evidence-research",
      os.path.exists(os.path.join(SKILLS, "evidence-research", "references",
                                  "retrieval-transports.md"))
      and "retrieval-transports.md" in read(SKILLS, "evidence-research", "SKILL.md"))
check("37 start no longer claims the bundled .mcp.json is empty as current state",
      "empty by design" not in read(SKILLS, "start", "SKILL.md").split("(Historical note:")[0])
TRANSPORTS = read(SKILLS, "evidence-research", "references", "retrieval-transports.md")
check("38 transport doc states MCP adds no source and changes no status",
      "does NOT change any connector's CONNECTED status" in TRANSPORTS
      or "changes NO status" in TRANSPORTS
      or "adds no new source" in read(SKILLS, "evidence-research", "SKILL.md"))
check("39 retraction gate is not waived by the MCP transport",
      "retraction-status unchecked" in TRANSPORTS
      and "retraction-status unchecked" in read(SKILLS, "evidence-research", "SKILL.md"))
check("40 the two transports are not presented as independent corroboration",
      "not independent corroboration" in TRANSPORTS
      or "never independent corroboration" in TRANSPORTS)
check("41 capability map records the MCP transport on both copies",
      all(MCP_URL in read(SKILLS, s, "references", "connector-capability-map.md")
          for s in ("start", "evidence-research")))
check("42 Cochrane/Embase/Scopus still NOT IMPLEMENTED on the MCP transport",
      "NOT IMPLEMENTED" in TRANSPORTS and "Cochrane" in TRANSPORTS)

# Naming defect caught by the v1.1.0 fresh-install validation: Claude Code registers a
# plugin-provided MCP server as `plugin:<plugin>:<server>` and builds the tool prefix from THAT,
# not from the bare server name. A skill checking `mcp__dental-ai-research__*` would find nothing
# and silently fall back to the local connectors.
RUNTIME_PREFIX = "mcp__plugin_dana-dental-research_dental-ai-research__"
ROUTING_DOCS = {
    "evidence-research/SKILL.md": read(SKILLS, "evidence-research", "SKILL.md"),
    "start/SKILL.md": read(SKILLS, "start", "SKILL.md"),
    "retrieval-transports.md": TRANSPORTS,
    "safe-search-gateway": read(SKILLS, "evidence-research", "references",
                                "clinical-evidence-safe-search-gateway.md"),
    "capability-map(start)": read(SKILLS, "start", "references",
                                  "connector-capability-map.md"),
    "capability-map(er)": read(SKILLS, "evidence-research", "references",
                               "connector-capability-map.md"),
}
bad_prefix = [n for n, d in ROUTING_DOCS.items()
              if "mcp__dental-ai-research__" in d]
check("43 no routing doc tells a skill to look for the wrong tool prefix",
      not bad_prefix, str(bad_prefix))
check("44 the real runtime prefix is documented where routing decisions are made",
      all(RUNTIME_PREFIX in ROUTING_DOCS[n]
          for n in ("retrieval-transports.md", "evidence-research/SKILL.md",
                    "start/SKILL.md", "capability-map(start)", "capability-map(er)")))
no_suffix = [n for n in ("retrieval-transports.md", "evidence-research/SKILL.md",
                         "start/SKILL.md", "safe-search-gateway")
             if not all(s in ROUTING_DOCS[n] for s in
                        ("__search_pubmed", "__search_systematic_reviews",
                         "__verify_citation", "__search_clinical_trials"))]
check("45 tools are identified by suffix, so a prefix change cannot disable the transport",
      not no_suffix, str(no_suffix))

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)
