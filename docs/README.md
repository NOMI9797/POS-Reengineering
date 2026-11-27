# POS Reengineering: Documentation Index

| File | Phase / content | Owner |
|---|---|---|
| [01-inventory-analysis.md](01-inventory-analysis.md) | Phase 1: asset inventory, classification, dependency maps | Member A |
| [02-legacy-system-documentation.md](02-legacy-system-documentation.md) | Phase 2: restructured legacy documentation (overview, architecture, class/sequence diagrams, data dictionary, business rules BR-01…18, dependencies and limitations) | Member A |
| [03-risk-register.md](03-risk-register.md) | Risk register (maintained throughout) | Member A (all contribute) |
| [04-refactorings-member-A.md](04-refactorings-member-A.md) | Member A's 3 refactorings (A1–A3) with before/after code | Member A |
| [05-team-handoff.md](05-team-handoff.md) | Smells, confirmed defects, data smells, proposed refactorings for B and C, how to run legacy | Member A → B, C |
| [Team-Work-Guide.md](Team-Work-Guide.md) | **Start here:** short guide to who does what (A done, B and C to do) | Member A → all |
| [Team-Work-Guide-detailed.md](Team-Work-Guide-detailed.md) | Detailed reference for B and C: schema, test values, patterns | Member A → B, C |
| [Member-A-Report.md](Member-A-Report.md) | Member A report (source of the Word file) with diagrams and screenshots | Member A |
| [inventory-live-demo.md](inventory-live-demo.md) | How to run the inventory analysis live (SonarQube + terminal) | Member A |
| `screenshots/` | Tool evidence: `member-a/` (terminal steps 1–8), `member-a-sonar/` (SonarQube views) | Member A |
| `../analysis/inventory/` | Inventory script (`inventory.sh`) and its saved output | Member A |
| `../analysis/sonarqube/` | SonarQube scripts: `setup-sonarqube.sh` (once per laptop), `start-`, `run-sonar-scan`, `stop-` | Member A, used by B |
| `../analysis/legacy-bug-probe/` | Executable evidence for defects P1–P8 (`run-probe.sh`, `probe-output.txt`) | Member A |
| `../legacy-pos/` | Unmodified clone of the legacy system (`yangzai/unit1-ca` @ `87bee5f`) | reference |

Diagrams are written in Mermaid. They render on GitHub/GitLab, in VS Code (Markdown Preview Mermaid extension) and at mermaid.live, where they can be exported as PNG/SVG for the Word report.
