# Connector Implementation Decision — v0.4 Phase A

## Part 1 — Execution mechanism: direct bundled scripts, not an MCP server

**Decision: implement PubMed and Crossref clients as bundled Python scripts, invoked via
Claude Code's Bash tool, not as an MCP server.**

### What was actually researched

Fetched the current official Claude Code plugin documentation
(`code.claude.com/docs/en/plugins-reference`, retrieved 2026-08-29 — same fetch used for the
v0.3.1 manifest repair) and checked it specifically for how a plugin executes code:

- The documented standard plugin layout includes a `scripts/` directory explicitly described as
  holding "Hook and utility scripts", and a `bin/` directory whose contents are "added to the Bash
  tool's PATH and invokable as bare commands while the plugin is enabled."
- MCP servers are documented as a **separate, optional** plugin component (`.mcp.json` or inline
  `mcpServers` in `plugin.json`), used to "connect Claude Code with external tools and services"
  as a persistent server process communicating over the MCP protocol.
- Nothing in the documented architecture requires HTTP-calling code to run through MCP. A skill's
  `SKILL.md` can instruct Claude to invoke a bundled script directly via the Bash tool — this is
  the same mechanism Claude Code uses for any other bundled utility script.

### Why direct script invocation is the right choice here, not MCP

1. **PubMed and Crossref are simple, stateless REST/XML/JSON APIs.** MCP's value is in exposing
   *tools* with structured schemas to the model across a persistent connection, which matters for
   complex or stateful integrations. A `client.py` that takes a query and returns parsed JSON is a
   complete solution without that machinery.
2. **Lower operational surface.** An MCP server is a long-running process Claude Code must start,
   manage, and keep healthy for the plugin's lifetime. A script invoked on demand via Bash has no
   persistent process to manage, no separate startup/shutdown lifecycle, and nothing that can be
   "up" incorrectly between calls.
3. **Matches the existing plugin's pattern.** v0.2.1 through v0.3.1 contain zero MCP servers and
   zero `.mcp.json` server entries (the file added in v0.3.1 is deliberately empty:
   `{"mcpServers": {}}`). Introducing MCP now for two simple REST clients would be a bigger
   architectural jump than the task requires.
4. **`${CLAUDE_PLUGIN_ROOT}`** (documented environment variable, resolves to the plugin's install
   directory) lets a skill reference the bundled script path reliably regardless of where the
   plugin is installed from — e.g. `python3 "${CLAUDE_PLUGIN_ROOT}/connectors/pubmed/client.py"
   search --query "..."`.

### What this means architecturally

The `clinical-evidence-safe-search-gateway.md` workflow (formulate → select source → enforce
firewalls → invoke connector → return status → route through DEL-7/directness/citation/
numeric/synthesis) is unchanged. "Invoke connector" now has a concrete implementation: Claude,
following `evidence-research/SKILL.md`, runs the appropriate bundled script via the Bash tool,
captures its structured output (JSON to stdout), and continues the pipeline from there. The
gateway's behavioral contract does not depend on which execution mechanism sits behind
"invoke connector" — this decision only fills in that blank.

### Not invented

No plugin execution behavior was assumed beyond what the fetched documentation states. Where the
documentation didn't specify something (e.g. exact stdout/stderr conventions for bundled scripts
invoked by a skill), the connector code follows ordinary, conservative Unix conventions (JSON to
stdout on success, non-zero exit code and a structured error object on failure) rather than
inventing a Claude-Code-specific protocol that isn't documented anywhere.

---

## Part 2 — Live verification status (REWRITTEN in v0.4.5.1 — supersedes the v0.4 text)

**This section previously stated that the bundled connector code had never been executed against
the live network, and that no connector could therefore be marked `CONNECTED`. That is no longer
true and the old text has been removed rather than left to mislead.** The claim was accurate about
the original v0.4 build sandbox; it was never a universal fact about the connectors.

### Current verified reality

- **The packaged PubMed connector has made real live requests.** `connectors/pubmed/client.py`
  `search`, `search-systematic-reviews` and `fetch` were run as real subprocesses on Claude Code /
  macOS (2026-08-30 and 2026-08-31) against `eutils.ncbi.nlm.nih.gov`, returning real PMIDs, real
  records, and NCBI's own server-side `query_translation`.
- **The packaged Crossref connector has made real live requests.** `connectors/crossref/client.py
  lookup-doi` was run against `api.crossref.org` and its response parsed successfully.
- **The dual-source chain completed end to end.** `shared/citation_verifier.py` returned
  `VERIFIED` on the live PubMed x Crossref pair; `shared/retraction_gate.py` executed cleanly.
- Exact commands, dates, statuses, PMIDs and DOIs: **"Live Validation Record" in
  `connector-capability-map.md`**, which is the authoritative record.

Phase 19 bar 3 ("a real API request succeeds") is therefore **met** for `~~literature`,
`~~systematic-reviews` and `~~journal-access`, which are `CONNECTED` as of v0.4.5.

### Runtime connectivity is environment-dependent — check it, do not assume it

Successful validation on one machine is **not** a guarantee for every environment, and the
absence of network access in one sandbox was never evidence about the connectors themselves.
Both statements are wrong as universal claims:

- ~~"The connectors have no network access."~~ False — they have been run live successfully.
- ~~"The connectors always have network access."~~ Also unsupported — some sandboxes block
  outbound hosts. The original v0.4 build environment did exactly this, returning `HTTP 403` with
  `x-deny-reason: host_not_allowed` for both `eutils.ncbi.nlm.nih.gov` and `api.crossref.org`.

**Required behaviour:** treat network availability as a runtime property. Invoke the connector and
read the `status` field it returns. A blocked or unreachable environment surfaces through the
normal failure contract (`TIMEOUT` / `UPSTREAM_ERROR` per `errors.py`) — the clients never raise
and never fabricate. Never infer connectivity from documentation, from this file, or from a
previous successful run in a different environment; and never present a connectivity failure as
though the connector were unimplemented.

### Status verdict

```
IMPLEMENTATION READY — LIVE CONNECTION VERIFIED (Claude Code / macOS, 2026-08-30/31)
                     — RUNTIME AVAILABILITY ENVIRONMENT-DEPENDENT, CHECK AT INVOCATION
```

The historical account of what the v0.4 build sandbox could and could not reach — including the
`web_fetch` response-caching artefact and the PMC CAPTCHA gate — is retained for the record in
`LIVE_CONNECTIVITY_TESTS.md`, which carries its own superseded-in-part addendum.
