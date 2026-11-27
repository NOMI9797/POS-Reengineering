# POS Reengineering – Team Guide

Who does what, in plain words

Member A: Malik Nouman Ahmed · 27 November 2026

**Deadline:** submit by Tuesday 1 December 2026, 11:59 PM. Presentation on Wednesday 2 December (10 minutes, about 3 minutes each).

## 1. The project in short

We take an old Java shop system (the "legacy POS") and rebuild it as a cleaner Python + Django system that does the same job. We must show every step of the reengineering process and document it.

**What we submit (all together):**

1. A technical report covering all 6 phases.
2. The new Django code, with its database.
3. The presentation slides.
4. The link to our private GitHub repository, showing each member's own commits.

**The 6 phases and who owns them:**

| Phase | What it means | Owner |
| --- | --- | --- |
| 1 Inventory Analysis | List everything in the old project and label it | A |
| 2 Document Restructuring | Write proper documentation of the old system | A |
| 3 Reverse Engineering | Study the old code deeply and find its problems (smells) | B |
| 4 Code Restructuring | Improve the code: each member does 3 refactorings | A, B, C |
| 5 Data Restructuring | Move the old text files into a proper database | B |
| 6 Forward Engineering | Build the new system with a clean layered design | C |

All along: keep a risk register (A) and write tests proving the new system behaves like the old one (C, with everyone).

## 2. Member A – done

| Done | Where to find it |
| --- | --- |
| Phase 1: every asset listed and labelled (active/obsolete, reuse), dependency maps | `docs/01-inventory-analysis.md` |
| Phase 2: full documentation of the old system, 18 business rules, data dictionary | `docs/02-legacy-system-documentation.md` |
| Old system's problems: 8 proven bugs, 17 limitations, 13 code smells, 10 data smells | `docs/02` §2.6, `docs/05-team-handoff.md` |
| Risk register (17 risks) | `docs/03-risk-register.md` |
| 3 refactorings, coded and tested (44 tests pass) | `docs/04-refactorings-member-A.md`, `reengineered/` |
| Django starter project (apps `core`, `members`, `inventory`) | `reengineered/` |
| Tool evidence: inventory script and SonarQube, with screenshots | `analysis/`, `docs/screenshots/` |
| Member A report (Word, 40 pages) | `docs/Member-A-Report.md` |

**Still with A until the end:** update the risk register as you finish your parts, and merge everyone's sections into the final report.

**Ready for you to use:**

- `Money` (in `reengineered/core/money.py`): use it for every price and total.
- `Member.from_legacy()`: use it when importing old members.
- `add_category()` and `add_member()`: ready-made services for the pages.
- The 18 business rules (`docs/02` §2.4): the new system must follow all of them.

## 3. Member B – to do

**You own:** Phase 3 (Reverse Engineering), Phase 5 (Data Restructuring) and 3 refactorings.

**Step 1 – Phase 3: study the old code**

1. Make a table of code measures per class (size, number of methods, what it depends on).
2. Explain 3 important old algorithms in simple pseudocode: best discount, completing a sale, making product IDs.
3. Write the smell catalogue: start from the 13 smells in `docs/05` and add proof for each (code lines, numbers). Use SonarQube for the numbers; see below.

**Step 2 – Phase 5: build the database**

1. Create the Django models: product, vendor, discount, sale, sale line (category and member already exist).
2. Write an import command that loads the old files from `legacy-pos/data-sample/` into the database.
3. Fix the data problems while importing (for example, `PUBLIC` becomes an empty member, passwords get hashed) and list each fix.
4. Check the result: 5 categories, 10 products, 11 members, 5 discounts, 3 sales.

**Step 3 – your 3 refactorings**

- **B1:** move all database access into "repository" classes.
- **B2:** replace the old text-file format with proper database mapping.
- **B3:** report bad data rows clearly instead of crashing.

Write each one up like A's (`docs/04`): problem, old code, new code, why, test.

**Reference:** exact tables and columns, data problems and test ideas are in `docs/Team-Work-Guide-detailed.md` §3.

**Why you need SonarQube:** Phase 3 is marked as "Reverse Engineering & Smell Detection" (15 marks). SonarQube finds code smells automatically and gives exact numbers per file and per rule (issues, complexity, duplication). That turns your smell catalogue and code-measures table into tool-based evidence instead of only your own reading of the code.

**Set up SonarQube on your own laptop (once):**

1. Install Java 17 or newer and Docker (Docker Desktop, or `brew install colima docker` on a Mac). Keep about 5 GB of disk free.
2. Run `./analysis/sonarqube/setup-sonarqube.sh` and choose your own admin password when asked. It starts SonarQube, creates your scan token and adds the "POS Inventory" rules.
3. Run `./analysis/sonarqube/run-sonar-scan.sh`, then open http://localhost:9000 and the project `legacy-pos`.
4. When finished: `./analysis/sonarqube/stop-sonarqube.sh` (results are kept).

## 4. Member C – to do

**You own:** Phase 6 (Forward Engineering), testing, and 3 refactorings.

**Step 1 – build the pages (same 8 features as the old system)**

Login, Checkout, Add category, Add member, Add product, Low-stock list and purchase order, Add discount, Reports. Plain pages are fine: the design is not marked, the structure is.

**Step 2 – keep the layers clean (this is what the marker checks)**

| Layer | Contains | Rule |
| --- | --- | --- |
| Pages (views, templates) | What the user sees | No business rules here |
| Services | All business rules | Each rule in one place |
| Repositories (from B) | Database access | Only place that talks to the database |

Also show the design patterns: MVC (Django's pages), Repository (B's), Singleton (one shared loyalty-points settings object) and Observer (a "sale completed" signal that triggers the low-stock alert).

**Step 3 – your 3 refactorings**

- **C1:** move all screen code out of the business classes.
- **C2:** put the whole checkout (discount, points, payment, stock) into one service.
- **C3:** turn the discount rules into separate small classes instead of one long if/else.

Write each one up like A's (`docs/04`).

**Step 4 – tests:** one test per business rule, using the old sample data. Example: a member buying 2 × CLO/1 and 3 × MUG/1 pays $66.28 after a 10% discount and earns 7 points.

**Step 5 – documentation of the new system:** new architecture diagram, old-vs-new comparison table, a list mapping old classes to new files, why we chose Django, and measured improvements (for example: business classes using screen code 6 → 0).

**Optional – SonarQube for C:** with the same setup (Member B's steps above, on your own laptop), SonarQube can also scan the new Django code. Comparing its issues, complexity and duplication with the legacy scan gives measured evidence of improvement for Step 5. The scan script currently scans the legacy code only, so it needs a small change (project name and source folder).

**Reference:** page list, test values and pattern details are in `docs/Team-Work-Guide-detailed.md` §4.

## 5. Everyone

| Task | Who | When |
| --- | --- | --- |
| Commit your own work under your own name | Each member | Every day |
| Write your report sections in `docs/` | Each member | By 30 Nov |
| Merge the final report | A | 30 Nov |
| Make your own slides (about 3 each) | Each member | 30 Nov |
| Sign the work distribution table | All | 1 Dec |
| Submit report, code, slides and repository link | All | 1 Dec, before 11:59 PM |

**Git, in short:** set your git email to the one on your GitHub account; work on your own branch; run `python manage.py test` before you push; open a pull request into `main`.

**In the presentation**, each member must explain and change their own work live. Work you cannot explain gets no marks.

## 6. Does this cover the project requirements?

| Requirement in the brief | Covered by | Status |
| --- | --- | --- |
| Phase 1 Inventory Analysis | A | Done |
| Phase 2 Document Restructuring | A | Done |
| Phase 3 Reverse Engineering and smells | B (using A's findings) | To do |
| Phase 4 Code Restructuring (3 refactorings each) | A done; B, C | In progress |
| Phase 5 Data Restructuring | B | To do |
| Phase 6 Forward Engineering, layered design | C | To do |
| Risk register | A | Done (keep updated) |
| Tests proving the same behaviour | C, with A and B | In progress |
| Old-system documentation | A | Done |
| New-system documentation | C (B adds the database part) | To do |
| Work distribution table, signed | All | To do |
| Slides and presentation | All | To do |
