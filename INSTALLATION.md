# Installation Guide

Written for a first-time user on **macOS**. Notes for Windows and Linux are at the end.

Every command below was verified against the Claude Code CLI shipped on this machine
(`claude plugin --help`, `claude plugin marketplace --help`, `claude plugin install --help`).
Nothing here is invented.

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

4. **This repository on your computer.** Download or clone it, and note the folder path — for
   example `/Users/yourname/Downloads/DANA-v1.0.0-DISTRIBUTION`.

---

## B. Install from the bundled marketplace (recommended)

This repository *is* a Claude Code marketplace. Two commands.

**Step 1 — register the marketplace.** Use the full path to the repository folder:

```bash
claude plugin marketplace add /Users/yourname/Downloads/DANA-v1.0.0-DISTRIBUTION
```

Confirm it registered:

```bash
claude plugin marketplace list
```

You should see `dana-dental` listed.

**Step 2 — install the plugin:**

```bash
claude plugin install dana-dental-research@dana-dental
```

The `@dana-dental` suffix names the marketplace, which avoids ambiguity if you have others
registered.

> **Tip:** drag the folder from Finder into Terminal after typing `claude plugin marketplace add `
> — Terminal fills in the path for you.

### If you are hosting this on GitHub

Once the repository is pushed, the same command accepts a GitHub repository instead of a local
path:

```bash
claude plugin marketplace add owner/repository-name
```

Then install exactly as in Step 2.

---

## C. Direct / local loading

If you prefer not to use the marketplace, the packaged artifact is in `releases/`:

- `dana-dental-research-clinical-intelligence-v1.0.0.plugin`
- `dana-dental-research-clinical-intelligence-v1.0.0.zip`

Both are the same ZIP archive under different extensions. The plugin source is also present,
unpacked, at `plugin/dana-dental-research/`.

**The supported installation route is the marketplace flow in section B**, pointed at this
repository folder — that folder already contains the unpacked plugin, so no manual extraction is
needed. If you want to keep the plugin somewhere else, move `plugin/dana-dental-research/`
wherever you like and register *that* location's parent repository instead.

Verify the download first if you obtained the archive separately:

```bash
cd releases
shasum -a 256 -c SHA256SUMS.txt
```

---

## D. Verify the installation

```bash
claude plugin list
```

`dana-dental-research` should appear as installed and enabled.

Then start Claude Code and check the skills are available:

```bash
claude
```

Type `/` and you should see these nine skills:

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

You can also inspect what was installed:

```bash
claude plugin details dana-dental-research
```

---

## E. First test prompt — no patient data

Paste this into Claude Code:

```
/dana-dental-research:start
```

Then:

```
What does the current evidence say about the survival of porcelain laminate veneers?
Show me how you classify the sources.
```

A correct response retrieves real published studies, labels each source by evidence level, and
states plainly what the evidence does not answer. If it invents references or answers with no
sources at all, something is wrong — see Troubleshooting.

---

## F. Troubleshooting

**`claude: command not found`**
Claude Code is not installed or not on your PATH. Install it, then close and reopen Terminal.

**Plugin not detected after installing**
Run `claude plugin marketplace list` — if `dana-dental` is missing, the path in Step 1 was wrong.
Re-run with the full absolute path. Then `claude plugin list` to confirm the plugin. Restart Claude
Code; skills load at session start.

**"Wrong directory" / path errors**
Use the **absolute** path (starting with `/Users/`), not a relative one. Drag the folder into
Terminal to get it exactly right. A path containing spaces must be quoted.

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

**Skills do not appear**
Confirm with `claude plugin list` that the plugin is *enabled*, not merely installed. If disabled:
```bash
claude plugin enable dana-dental-research
```

---

## Windows and Linux

The same commands work. Only the path format differs — use your platform's absolute path, for
example `C:\Users\yourname\Downloads\DANA-v1.0.0-DISTRIBUTION` on Windows. On Windows use
`certutil -hashfile <file> SHA256` instead of `shasum` to check the checksum.
