# Installation Guide

Written for a first-time user on **macOS**. Notes for Windows and Linux are at the end.

Every command below was verified against the Claude Code CLI (`claude plugin --help`,
`claude plugin marketplace --help`, `claude plugin install --help`) and by running a full
end-to-end installation test. Nothing here is invented.

---

## A. Prerequisites

1. **Claude Code installed.** Open Terminal and run:
   ```bash
   claude --version
   ```
   If you see a version number, you are ready. If you see `command not found`, see Troubleshooting.

2. **A signed-in Claude Code account.** Run `claude` once and complete sign-in if prompted.

3. **An internet connection.** The evidence connectors query PubMed, Crossref and
   ClinicalTrials.gov live. Without a connection the assistant still works, but it will tell you
   retrieval was unavailable rather than answering from memory.

That is all. You do **not** need to download anything by hand, and you do **not** need a GitHub
account.

---

## B. Install

Two commands.

**Step 1 — register the marketplace:**

```bash
claude plugin marketplace add danaaburawaeh-glitch/dental-research-clinical-intelligence
```

Claude Code fetches the repository itself and validates it. Confirm it registered:

```bash
claude plugin marketplace list
```

You should see `dana-dental` listed, with its source shown as GitHub.

**Step 2 — install the plugin:**

```bash
claude plugin install dana-dental-research@dana-dental
```

The `@dana-dental` suffix names the marketplace, which avoids ambiguity if you have others
registered.

---

## C. Verify the installation

```bash
claude plugin list
```

`dana-dental-research` should appear as **version 1.1.0**, scope `user`, status **enabled**.

Then inspect what was installed:

```bash
claude plugin details dana-dental-research
```

This lists the component inventory. You should see **9 skills**:

| Skill | Purpose |
|---|---|
| `start` | Orientation and routing |
| `clinical-governance` | The safety and governance rules |
| `clinical-case` | Full case analysis |
| `triage` | Urgent symptoms |
| `esthetic-prosthodontics` | Veneers, crowns, esthetic planning |
| `treatment-plan-audit` | Adversarial review of an existing plan |
| `scientific-problem-selection` | Research question selection |
| `evidence-research` | Literature retrieval and appraisal |
| `quality-control` | Pre-release checking of an output |

The same command also reports the projected token cost — roughly **850 tokens always-on** per
session, with each skill costing more only when it actually fires.

---

## D. Start Claude Code

```bash
claude
```

---

## E. First test — no patient data

Inside Claude Code, run the orientation skill:

```
/dana-dental-research:start
```

Then try a real question:

```
What does the current evidence say about the survival of porcelain laminate veneers?
Show me how you classify the sources.
```

A correct response retrieves real published studies, labels each source by evidence level, and
states plainly what the evidence does not answer. If it invents references or answers with no
sources at all, something is wrong — see Troubleshooting.

---

## F. Updating

```bash
claude plugin marketplace update dana-dental
claude plugin install dana-dental-research@dana-dental
```

Check which version you have with `claude plugin list`.

---

## G. Troubleshooting

**`claude: command not found`**
Claude Code is not installed or not on your PATH. Install it, then close and reopen Terminal.

**Marketplace not found, or the repository cannot be fetched**
Check your internet connection and re-run the `marketplace add` command exactly as written,
including the `owner/repository` form. Confirm with `claude plugin marketplace list`.

**Plugin not detected after installing**
Run `claude plugin marketplace list` — if `dana-dental` is missing, Step 1 did not complete. Then
`claude plugin list` to confirm the plugin. Restart Claude Code; skills load at session start.

**Skills do not appear**
Confirm with `claude plugin list` that the plugin is *enabled*, not merely installed. If disabled:
```bash
claude plugin enable dana-dental-research
```

**No internet connection**
The assistant will report that retrieval was unavailable. **This is not a finding.** A failed or
unavailable search does not mean no evidence exists — it means nothing was searched. Re-run when
you are back online.

**PubMed, Crossref or ClinicalTrials.gov failure**
These are public services and occasionally rate-limit or go down. The connector reports a failure
status rather than guessing. Wait and retry. If it persists, check whether your network blocks
`eutils.ncbi.nlm.nih.gov`, `api.crossref.org` or `clinicaltrials.gov`. **Again: a failure is never
evidence of absence.**

**`NOT CONNECTED — AUTH REQUIRED` for SFDA**
Expected. Saudi regulatory lookup needs a registered SFDA developer application, which is not
configured in this release. Any Saudi regulatory statement will come back as **REQUIRES
VERIFICATION** — which is the correct answer, not an error. Verify Saudi status directly with SFDA
before purchase or clinical use. To connect it later, see
`plugin/dana-dental-research/docs/SFDA_CONNECTOR_VALIDATION.md`.

**Uninstalling**
```bash
claude plugin uninstall dana-dental-research@dana-dental
claude plugin marketplace remove dana-dental
```

---

## Windows and Linux

The two installation commands are identical on every platform. Only Troubleshooting paths differ.
On Windows use `certutil -hashfile <file> SHA256` in place of `shasum` if you verify a download.

---

# Developer / Local Testing Only

**Ordinary users should not need this section.** It covers working from a local checkout, which is
useful only when developing the plugin or testing an unreleased change.

### Registering a local checkout as a marketplace

Point `marketplace add` at a directory instead of a repository:

```bash
claude plugin marketplace add /absolute/path/to/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

Use the **absolute** path (starting with `/Users/` on macOS). Dragging the folder from Finder into
Terminal fills it in exactly. A path containing spaces must be quoted.

Note that this registers your working copy, so edits take effect on the next
`claude plugin marketplace update dana-dental`. That is convenient for development and a bad idea
for production use — the installed plugin then depends on a directory you might move or delete.

### Installing from the packaged artifact

`releases/` contains:

- `dana-dental-research-clinical-intelligence-v1.1.0.plugin`
- `dana-dental-research-clinical-intelligence-v1.1.0.zip`

Both are the same archive under different extensions. Verify a download before using it:

```bash
cd releases
shasum -a 256 -c SHA256SUMS.txt
```

The repository already contains the plugin unpacked at `plugin/dana-dental-research/`, so the
marketplace flow above needs no manual extraction.

### Private or internal deployments

If you host this repository **privately** — an internal clinic fork, or a staged rollout before
public release — each user must be authenticated to GitHub and granted access to the repository.
The simplest route:

```bash
gh auth login     # GitHub.com → HTTPS → Login with a web browser
```

Then the standard two commands in section B work unchanged.

**This is not required for the public release.** A public repository installs with no GitHub
account and no authentication at all.
