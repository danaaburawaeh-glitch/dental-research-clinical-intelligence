# Installation — English

**Dental Research & Clinical Intelligence by Dr. Dana** · v1.0.2

Three routes, by experience level. Most people want **A**.

---

## A. Marketplace installation (normal)

Requires Claude Code installed and signed in. **No GitHub account.**

```bash
claude plugin marketplace add danaaburawaeh-glitch/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

Verify:

```bash
claude plugin list                          # expect: version 1.0.2, enabled
claude plugin details dana-dental-research  # expect: Skills (9)
```

Start:

```bash
claude
```
```
/dana-dental-research:start
```

Update later:

```bash
claude plugin marketplace update dana-dental
claude plugin install dana-dental-research@dana-dental
```

---

## B. Beginner guide (no Terminal)

If typing commands is unfamiliar, use the graphical installer: download the `.pkg`, double-click,
Continue, Install. It performs the two commands above for you.

Because the installer is not signed by Apple, macOS will warn on first open. Right-click the file →
**Open** → **Open**, or approve it under **System Settings → Privacy & Security → Open Anyway**.

Full walkthrough in both languages ships with the installer as `INSTALL_WITHOUT_TERMINAL_EN.md` and
`INSTALL_WITHOUT_TERMINAL_AR.md`.

---

## C. Developer / local installation

For working on the plugin or testing an unreleased change:

```bash
git clone https://github.com/danaaburawaeh-glitch/dental-research-clinical-intelligence.git
claude plugin marketplace add /absolute/path/to/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

This registers your working copy, so edits apply on the next
`claude plugin marketplace update dana-dental`. Convenient for development, wrong for production —
the install then depends on a directory you might move or delete.

Verify a downloaded release artifact:

```bash
cd releases && shasum -a 256 -c SHA256SUMS.txt
```

---

## The nine skills

| Skill | What it does |
|---|---|
| `start` | Orients you and routes the question to the right workflow |
| `clinical-governance` | Applies the safety, evidence, privacy and regulatory rules |
| `clinical-case` | Full case analysis through the governed diagnostic sequence |
| `triage` | Handles urgent symptoms, swelling, trauma and bleeding first |
| `esthetic-prosthodontics` | Governs elective esthetic and fixed-prosthodontic planning |
| `treatment-plan-audit` | Adversarially audits a plan you already have |
| `scientific-problem-selection` | Helps choose and de-risk a research question |
| `evidence-research` | Retrieves, verifies and appraises published evidence |
| `quality-control` | Checks an output before you rely on it |

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `claude: command not found` | Install Claude Code, then reopen Terminal |
| Marketplace not found | Re-run the `marketplace add` command; check your connection |
| Plugin installed but skills missing | `claude plugin enable dana-dental-research`, then restart Claude Code |
| Search fails | A failed search is **not** evidence of absence. Retry when online |
| `NOT CONNECTED — AUTH REQUIRED` for SFDA | Expected. Saudi status returns *requires verification*; confirm with SFDA directly |

Uninstall:

```bash
claude plugin uninstall dana-dental-research@dana-dental
claude plugin marketplace remove dana-dental
```
