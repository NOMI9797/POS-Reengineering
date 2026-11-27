# POS Reengineering – Team Work Guide

Guidelines for Members A, B and C, and alignment with the project requirements

Prepared by Member A: Malik Nouman Ahmed · 27 November 2026

Submission (report, code, slides, repository link) is due Tuesday 1 December 2026 at 11:59 PM; presentations are on 2 December. Member A's part is complete; this guide tells Members B and C exactly what to build and document so the combined work meets every requirement of the brief.

## 1. How to use this guide

Each member owns one layer of the system and the phases that belong to it, so no two members write the same code or the same report section. Read your own section, then Section 5 (shared tasks) and Section 6 (what the marker checks).

| Member | Owns | Phases of the process model | Refactorings | Status |
| --- | --- | --- | --- | --- |
| A – Malik Nouman Ahmed | Domain model, legacy documentation, risk register | 1 Inventory Analysis, 2 Document Restructuring | A1, A2, A3 | Done |
| B | Data access and database | 3 Reverse Engineering, 5 Data Restructuring | B1, B2, B3 | To do |
| C | Services, user interface, testing | 6 Forward Engineering, testing | C1, C2, C3 | To do |

Phase 4 (Code Restructuring) is shared: each member's three refactorings together form it.

### 1.1 Starting point

| Item | Where |
| --- | --- |
| Repository | `github.com/NOMI9797/POS-Reengineering` (private) |
| Legacy system, unmodified | `legacy-pos/` (git tag `legacy-baseline`) |
| Django project (skeleton + Member A code) | `reengineered/` – apps `core`, `members`, `inventory`; 44 tests passing |
| Findings to build on | `docs/01` to `docs/05`, `docs/Member-A-Report.md` |
| Legacy defects, reproducible | `analysis/legacy-bug-probe/run-probe.sh` |
| Inventory tool (all inventory numbers, obsolete check, `jdeps`) | `analysis/inventory/inventory.sh` |
| SonarQube (local server in Docker, scan scripts) | `analysis/sonarqube/` – `start-sonarqube.sh`, `run-sonar-scan.sh`, `stop-sonarqube.sh` |
| Live demo of the inventory analysis | `docs/inventory-live-demo.md` |
| Word report generator | `tools/md2docx.py` |

Set-up (Python 3.12 or 3.13; Django 5.2 does not support Python 3.15):

```bash
git clone https://github.com/NOMI9797/POS-Reengineering.git
cd POS-Reengineering/reengineered
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test        # 44 tests must pass before you start
```

### 1.2 Rules every member follows

1. Preserve legacy behaviour. The 18 business rules BR-01 to BR-18 (`docs/02` §2.4) are the specification; no new features.
2. Every change traces to a finding ID: `INV-`, `L-`, `S-`, `DS-`, `BR-` or `P1`–`P8`.
3. Fixing a legacy defect is allowed only as a documented deviation with its own test (see Member A's D-A2a, D-A2b, D-A3).
4. Commit your own work under your own name, one commit per refactoring, on your own branch; open a pull request into `main`.
5. Run `python manage.py test` before every push; all tests stay green.
6. Write report text in your own words (similarity check).

### 1.3 Deadline plan

| Date | Member B | Member C | All |
| --- | --- | --- | --- |
| Fri 27 Nov | Models + migrations for all tables | `discounts`, `sales`, `accounts` views plan and login page; agree model, repository and service names with B | Read this guide |
| Sat 28 Nov | `import_legacy` command, B1–B3 | Checkout service, discount strategies, C2–C3 | Daily merge |
| Sun 29 Nov | Validation report, Phase 3 write-up | Views and templates, C1; regression tests | Integration day |
| Mon 30 Nov | Phase 5 write-up, schema diagram | Architecture write-up, comparison, mapping | Merge report, slides, risk register review |
| Tue 1 Dec | Final fixes | Final fixes | Signatures, submit before 11:59 PM |
| Wed 2 Dec | – | – | 10-minute presentation, about 3 minutes each |

## 2. Member A – completed work

All Member A deliverables are done, committed under Member A's name and pushed; 44 tests pass. Only two ongoing duties remain: keeping the risk register current and merging the final report.

### 2.1 Deliverables

- [x] **Phase 1 – Inventory Analysis.** 41 source assets, 16 test files, 11 data files, 7 libraries and 18 configuration/build/documentation assets identified. Every asset has an ID, a Status (active/obsolete) and a Reuse decision; 3 dependency maps verified with `jdeps`; conclusions INV-1 to INV-8. File: `docs/01-inventory-analysis.md`.
- [x] **Phase 2 – Document Restructuring (legacy documentation set A).** System overview, 8 features, use-case diagram, recovered architecture, module inventory, class diagram, checkout sequence diagram, data dictionary for all 11 files, business rules BR-01 to BR-18. File: `docs/02-legacy-system-documentation.md`.
- [x] **Weaknesses and smells.** Limitations L-01 to L-17, code smells S-01 to S-13, data smells DS-1 to DS-10. Files: `docs/02` §2.6, `docs/05`, report §4.
- [x] **Verified defects P1–P8.** Reproduced on the legacy code by `analysis/legacy-bug-probe/`. The worst: after any sale, all past member sales are rewritten as `PUBLIC` (P1).
- [x] **Risk register.** 17 risks with likelihood, impact, score, mitigation, owner, status and heat map. File: `docs/03-risk-register.md`.
- [x] **Django skeleton.** Project `pos`, apps `core`, `members`, `inventory`; settings from environment variables; pinned `requirements.txt`.
- [x] **Refactoring A1** – `-1` loyalty sentinel replaced by `has_purchased` (`members/models.py`, 12 tests, commit `d7579b1`).
- [x] **Refactoring A2** – self-validating `Category` and `Member` entities (`inventory/models.py`, `inventory/services.py`, `members/services.py`, 17 tests, commit `4dda7ef`).
- [x] **Refactoring A3** – `Money` value object replaces `double` (`core/money.py`, 15 tests, commit `31f0468`).
- [x] **Inventory tool evidence.** `analysis/inventory/inventory.sh` regenerates every inventory number; 8 steps (find, line counter, grep, `jdeps`, JUnit, probe) shown as command and result screenshots in the report. Screenshots: `docs/screenshots/member-a/`.
- [x] **SonarQube analysis.** SonarQube Community Build 26.11 runs locally in Docker; quality profile "POS Inventory" (Sonar way plus maintainability rules); 11 dashboard screenshots in the report (size, complexity, duplication, TODO and printStackTrace issues). SonarQube covers code size and smells; the terminal tools cover data/config/docs, obsolete classes, dependencies, tests and defects. Screenshots: `docs/screenshots/member-a-sonar/`.
- [x] **Live demo guide** for running the inventory analysis in class (SonarQube + terminal). File: `docs/inventory-live-demo.md`.
- [x] **Member A report** with 7 diagrams and 27 screenshots (40 pages). Files: `docs/Member-A-Report.md` and the Word version.
- [x] **Handoff** of findings and proposed refactorings to B and C. File: `docs/05-team-handoff.md`.

### 2.2 Ongoing duties until submission

- [ ] Update risk statuses as B and C deliver (for example R-03 becomes Mitigated after B's validated migration) and log each change.
- [ ] Merge all sections into the final report and run the consistency review on 30 November.

### 2.3 What Members B and C reuse from Member A

| Asset | Use it for |
| --- | --- |
| `core.money.Money` | Every price, subtotal, discount, payment and change (B: `DecimalField` columns; C: checkout totals) |
| `Member.from_legacy(name, id, points)` | B's import of `Members.dat` (`-1` becomes 0 points, `has_purchased = False`) |
| `Member.redeem()`, `Member.record_purchase()` | C's checkout service (BR-12, BR-13) |
| `inventory.services.add_category`, `members.services.add_member` | C's "Add category" and "Add member" pages |
| Business rules BR-01 to BR-18 | C's regression tests |
| Data dictionary, data smells DS-1 to DS-10 | B's schema design |
| Smells S-01 to S-13, defects P1–P8 | B's Phase 3 analysis |
| SonarQube server and `run-sonar-scan.sh` | B: evidence for the Phase 3 smell catalogue (issues per rule, complexity, duplication); C: scan `reengineered/` as a second project to measure the improvement |

## 3. Member B – guidelines (to do)

Member B owns Phase 3 (Reverse Engineering), Phase 5 (Data Restructuring), the whole data layer of the Django system and refactorings B1–B3. B creates every model and migration first, because Member C's services and pages depend on them.

### 3.1 Phase 3 – Reverse Engineering

**Brief:** "Analyze legacy code to recover design and detect weaknesses. Identify code and data smells." Member A already recovered the architecture, class and sequence diagrams (`docs/02`); do not repeat them. Phase 3 goes deeper into the code and the data.

- [ ] **Code metrics per class.** For each of the 40 classes: lines of code, number of methods, number of packages imported (fan-out), imports `javax.swing` (yes/no), number of responsibilities. Example command: `grep -c "^import sg" <file>`. Present as one table and name the 5 worst classes.
- [ ] **Recovered algorithms.** Write pseudocode (or an activity diagram) for the three most important legacy algorithms: best-discount selection (`DiscountManager.getMaxDiscount`, lines 57–75), sale completion (`TransactionManager.addTransaction`, lines 150–208) and product ID generation (`ProductManager.addProduct`, lines 88–108).
- [ ] **Recovered legacy data model.** An ER diagram of the data exactly as the files hold it, including the hidden keys (category inside `CLO/1`, category inside `VendorsCLO.dat`, `PUBLIC` instead of a member).
- [ ] **Code smell catalogue.** Expand S-01 to S-13 (`docs/05` §2.1). For each smell: name (Fowler catalogue), location with line numbers, a short code excerpt, the metric that shows it, the consequence, and the refactoring that removes it (A1–A3, B1–B3, C1–C3). Set up SonarQube on your own laptop once with `./analysis/sonarqube/setup-sonarqube.sh` (needs Java 17+ and Docker), scan with `./analysis/sonarqube/run-sonar-scan.sh`, open http://localhost:9000 (project `legacy-pos`) and use its issues per rule, complexity and duplication as evidence.
- [ ] **Data smell catalogue.** Expand DS-1 to DS-10 (`docs/05` §2.3) with a real example row from `data-sample/` for each.
- [ ] **Defect confirmation.** Re-run `analysis/legacy-bug-probe/run-probe.sh` and include the output for P1–P8.

### 3.2 Phase 5 – Data Restructuring

**Brief:** "Redesign and normalize the data model. Migrate to a relational database and resolve data inconsistencies."

**Target schema.** `category` and `member` already exist (Member A). Add these models with migrations:

| Table (app) | Columns and constraints | Fixes |
| --- | --- | --- |
| `product` (`inventory`) | `id` PK; `code` unique (`CLO/1`); `category` FK → category; `name`; `description`; `quantity` ≥ 0; `price` `DECIMAL(10,2)` ≥ 0; `barcode` unique; `threshold` ≥ 0; `order_quantity` ≥ 0 | DS-3, DS-8 |
| `vendor` (`vendors`) | `id` PK; `name` unique; `description` | DS-4 |
| `vendor_category` (`vendors`) | `vendor` FK; `category` FK; unique (vendor, category) | DS-4 |
| `discount` (`discounts`) | `code` PK (upper-case); `description`; `start_date` nullable (null = ALWAYS); `period_days` nullable (null = ALWAYS); `percent` `DECIMAL(5,2)`; `applies_to` choice `MEMBER` / `ALL` | DS-5 |
| `sale` (`sales`) | `id` PK (keeps legacy transaction id); `date`; `member` FK nullable (null = public customer); `discount_code`, `discount_percent`, `discount_amount`, `points_redeemed`, `points_earned`, `amount_paid` (nullable for migrated legacy sales) | DS-1, DS-2, DS-6 |
| `sale_line` (`sales`) | `id` PK; `sale` FK; `product` FK; `quantity` > 0; `unit_price` `DECIMAL(10,2)`; unique (sale, product) | DS-1, DS-2 |
| storekeeper | Django's built-in `auth.User` (username + hashed password) | DS-7 |

- [ ] **Normalisation write-up.** Show the legacy layout fails each form and how the schema meets it: 1NF (the category hidden inside the product id is not atomic), 2NF (`Transactions.dat` repeats member and date per line, so they move to `sale`), 3NF (no column depends on another non-key column).
- [ ] **New ER diagram** of the schema above.
- [ ] **Migration command** `python manage.py import_legacy ../legacy-pos/data-sample`. Read files with the `csv` module as UTF-8 (fixes the comma problem P4). Load in dependency order: categories → vendors → products → members → discounts → storekeepers → sales. Use `Member.from_legacy()` for members and the model `clean()` rules for every row. Wrap it in `transaction.atomic()` so a failure leaves the database unchanged.
- [ ] **Resolve data inconsistencies** and record each decision:

| Inconsistency found in `data-sample/` | Recommended resolution |
| --- | --- |
| Member `R64565FG4` (Ang Lee) has loyalty `-1` (never purchased) but appears in sale 3 | Treat the sales history as the source of truth: `has_purchased = True`. Record as deviation D-B1 with a test. |
| Legacy sales store no unit price | Use the product's current price from `Products.dat`; state this assumption in the migration summary |
| Legacy sales store no discount, points or payment | Leave those columns null for migrated sales |
| `PUBLIC` used as a member id | `member = NULL` |
| The same 4 vendors repeated in 5 files | 4 `vendor` rows + 20 `vendor_category` rows |
| `ALWAYS` in discount dates | `NULL` |
| Spelling errors ("Stationary", "Sovenirs", "momento") | Keep unchanged (data fidelity); list them |
| Plain-text passwords | `User.objects.create_user()` stores a hash |

- [ ] **Validation report.** The import prints, and a test asserts, these counts: categories 5, products 10, members 11, discounts 5, storekeepers 2, vendors 4, vendor-category links 20, sales 3, sale lines 4, rejected rows 0, plus a foreign-key check.
- [ ] **Database choice.** SQLite for development and tests; PostgreSQL by setting `POS_DB_ENGINE` and the other `POS_DB_*` variables (already supported in `pos/settings.py`). Justify in two sentences.

### 3.3 Refactorings B1–B3

Document each exactly like Member A's (`docs/04`): smell, location, before code (legacy Java), after code (Django), mechanics, behaviour preserved, test, commit hash.

| ID | Refactoring | Before (legacy) | After (Django) | Traces to |
| --- | --- | --- | --- | --- |
| B1 | Extract Class → Repository | `load()`/`store()` copied into 7 managers | `repositories.py` per app (`CategoryRepository`, `ProductRepository`, …) wrapping the ORM; services call repositories, never `Model.objects`. Start by replacing `Category.objects` in `inventory/services.py`. | S-01, S-02, INV-1 |
| B2 | Replace `toString()` serialisation with explicit mapping | `Product.toString()` and `TransactionItem.toString()` are the file format (comma corruption P4, member loss P1) | Model fields define the table; a `legacy_import` mapper turns each CSV row into a model | P1, P4, DS-1 |
| B3 | Replace swallowed errors with validated row-level loading | 16 × `printStackTrace()`; one bad line stops start-up (P5) | Import returns `ImportResult(imported, rejected=[(line, reason)])`; Python `logging` | S-09, P5, L-15 |

### 3.4 Tests Member B writes

- [ ] Import counts (the validation numbers above).
- [ ] A product name containing a comma survives import and reload (P4 fixed).
- [ ] After a new sale is saved, earlier member sales still belong to their member (P1 fixed).
- [ ] A malformed row is rejected and reported; the rest still import (P5 fixed).
- [ ] Repository tests: save, find by code, exists.
- [ ] Deviation D-B1 (Ang Lee is not treated as a first purchase).

### 3.5 Member B report sections

- [ ] Phase 3 – Reverse Engineering (3.1 above).
- [ ] Phase 5 – Data Restructuring: schema, ER diagram, normalisation, migration summary, inconsistencies table, validation report.
- [ ] Refactoring log B1–B3.
- [ ] Contribution to documentation set B: "database schema and migration summary" and "refactored data structures".

## 4. Member C – guidelines (to do)

Member C owns Phase 6 (Forward Engineering): the business services, the web pages, the regression tests, the reengineered-system documentation and refactorings C1–C3. C builds on Member B's models and repositories and Member A's `Money`, `Member` and `Category` code.

### 4.1 Target architecture (what the marker checks)

The brief requires "defined layers (Presentation, Business Logic, Data Access)", a service layer with centralised business rules, database access via repository or ORM, a configurable and testable design, and patterns such as MVC, Repository, Singleton and Observer.

| Layer | Django files | Rule |
| --- | --- | --- |
| Presentation | `<app>/views.py`, `<app>/urls.py`, `templates/` | Reads input, calls one service, renders a template. No business rule, no `Model.objects`. |
| Business logic | `<app>/services.py`, model methods, `core/money.py`, `LoyaltyPolicy` | Every business rule BR-01 to BR-18 lives here, once. |
| Data access | `<app>/repositories.py` (Member B) over the Django ORM | Only layer that queries the database. |
| Configuration | `pos/settings.py` + environment variables | File paths, loyalty rates and database are settings, not code (fixes L-13). |

| Pattern | How it appears | Where to show it |
| --- | --- | --- |
| MVC | Django MVT: model = `models.py`, controller = view function, view = template | Every feature |
| Repository | Member B's `repositories.py` (B1) | Services |
| Singleton | One `LoyaltyPolicy` instance built from settings and shared by all services | `sales/loyalty.py` |
| Observer | Django signal `sale_completed`; a receiver builds the understock alert. Replaces the legacy `*PanelListener` interfaces. | `sales/signals.py` |
| Strategy | Discount eligibility rules (C3) | `discounts/rules.py` |

### 4.2 Features to rebuild (preserve F1–F8, no new features)

| Feature | Page (URL) | Service | Rules preserved |
| --- | --- | --- | --- |
| F1 Login | `/login/` (Django `LoginView`); every page `@login_required` | Django auth | BR-01 |
| F2 Checkout | `/checkout/` add items and member → `/checkout/payment/` redeem, pay, confirm → `/checkout/receipt/<id>/` with understock alert | `sales/services.py` – `CheckoutService` | BR-08 to BR-15 |
| F3 Add category | `/categories/` form + list | `inventory.services.add_category` (exists) | BR-02 |
| F4 Add member | `/members/` form + list | `members.services.add_member` (exists) | BR-03 |
| F5 Add product | `/products/` form + list | `inventory.services.add_product` (generates `CAT/n`) | BR-04 |
| F6 Understock and purchase order | `/inventory/understock/` list with checkboxes | `inventory.services.generate_purchase_order` | BR-05, BR-06 |
| F7 Add discount | `/discounts/` form + list | `discounts.services.add_discount` (duplicate shows an error: fixes L-05) | BR-16 |
| F8 Reports | `/reports/` categories, products, transactions (inclusive date range), members | `reports/services.py` or per-app queries | BR-17 |

Plain Django templates are enough; looks are not graded, architecture is.

### 4.3 Refactorings C1–C3

Document each exactly like Member A's (`docs/04`): smell, location, before (legacy Java), after (Django), mechanics, behaviour preserved, test, commit hash.

| ID | Refactoring | Before (legacy) | After (Django) | Traces to |
| --- | --- | --- | --- | --- |
| C1 | Move Method: separate presentation from business classes (MVC + Observer) | 7 `getTableModel()` methods inside managers and `Transaction`; `fireTableRowsInserted` inside business methods; crash P2 | Services return plain data; views and templates render tables; `sale_completed` signal replaces listener callbacks; no UI code below the view layer | S-05, S-12, L-12, P2 |
| C2 | Extract Service: checkout and loyalty rules | Redemption cap computed in 3 places (`ConfirmPaymentDialog.java:158-184`, `Transaction.java:206-207`, `TransactionManager.java:159-164`); GUI reads `TransactionManager` rate constants | `CheckoutService.complete()` runs stock check, discount, redemption cap, payment check, point debit/credit (`Member.redeem`, `Member.record_purchase`), stock deduction and save inside `transaction.atomic()`; totals with `Money`; rates from one `LoyaltyPolicy` | S-04, S-11, L-11, L-13 |
| C3 | Replace Conditional with Polymorphism (Strategy) | `if (code.equals("MEMBER_FIRST") …)` hard-coded in `DiscountManager.getMaxDiscount` | `AllCustomersRule`, `MemberOnlyRule`, `FirstPurchaseRule` (uses `member.is_first_purchase`), `SubsequentPurchaseRule`; the date is passed in, so tests fix "today" | S-06, BR-07 to BR-09, R-11 |

### 4.4 Regression tests (prove functionality is preserved)

One test per business rule, using legacy sample data. Required expected values:

| Case | Expected result | Rule |
| --- | --- | --- |
| Member `F42563743156` buys 2 × CLO/1 + 3 × MUG/1 | Subtotal $73.65; `MEMBER_SUBSEQ` 10% = $7.37; total $66.28; earns 7 points; can redeem at most 13 | BR-08, 11, 12, 13 |
| Brand-new member checks out | `MEMBER_FIRST` 20% | BR-09 |
| Public customer, today | No discount (all promotions date from 2014) | BR-07, BR-09 |
| `PRESIDENT_BDAY` (start 2014-02-01, 7 days) on 2014-02-08 and 2014-02-09 | Active, then not active | BR-07 |
| 769 × STA/1 (stock 768) | Rejected: "Exceeded inventory quantity." | BR-10 |
| Payment + redemption below total | Rejected: "Insufficient Amount" | BR-14 |
| Add a product to MUG | Gets id `MUG/3` | BR-04 |
| Product at or below threshold, purchase order | Quantity increases by its order quantity | BR-05, BR-06 |
| Sale completed | Sold products now understock appear in the alert | BR-15 |
| Duplicate discount code | Error shown (deviation fixing L-05) | BR-16 |

- [ ] Write the test plan: rule → test name → expected value → result.
- [ ] Final run: total number of tests and "all pass" as evidence for the report.

### 4.5 Reengineered-system documentation (set B) written by Member C

- [ ] **Technology stack and rationale.** Python 3.12, Django 5.2 LTS, SQLite/PostgreSQL, Django test runner; why Django (built-in ORM, auth, migrations, MVT layering, test framework) and why not staying on Swing.
- [ ] **Improved architecture diagram** (layers as in 4.1) and design diagrams: new class diagram of models and services; new checkout sequence diagram through `CheckoutService`.
- [ ] **Comparison table, legacy vs reengineered:** layers, where rules live, persistence, configuration, error handling, platform, patterns, tests.
- [ ] **Mapping old → new components**, for example: `StoreApplication` → `pos/settings.py` + `urls.py`; `CategoryManager` → `inventory/repositories.py` + `services.py` + `views.py`; `Transaction`/`TransactionItem` → `Sale`/`SaleLine`; `ConfirmPaymentDialog` → payment view + `CheckoutService`; `Util.formatDollar` → `Money`; `ReceiptPrinter` → receipt template.
- [ ] **Evidence of architectural improvement** as measured numbers: business classes importing UI code (6 → 0); copies of file I/O code (7 → 0); hard-coded settings (paths, rates → settings); verified defects (8 → 0, each with a test); automated tests (45 legacy → total in the new system). Optionally scan `reengineered/` in SonarQube as a second project and compare its issues, complexity and duplication with `legacy-pos`.
- [ ] **README** with run steps and screenshots of the 8 features; a short live demo for the presentation.

## 5. Shared team tasks

Four deliverables are submitted together on 1 December: the technical report, the codebase, the slides and the repository link. The slides are presented unchanged on 2 December.

### 5.1 Final report structure (Member A merges)

Each member writes their sections in Markdown under `docs/`; Member A merges them and builds the Word file with `tools/md2docx.py`.

| # | Report section | Written by | Source |
| --- | --- | --- | --- |
| 1 | Introduction, legacy system, technology choice | A + C | A report §1, C stack rationale |
| 2 | Phase 1 – Inventory Analysis | A | Done |
| 3 | Phase 2 – Document Restructuring (legacy documentation, set A) | A | Done |
| 4 | Phase 3 – Reverse Engineering (metrics, algorithms, smells) | B | Guide §3.1 |
| 5 | Phase 4 – Code Restructuring: refactoring log A1–A3, B1–B3, C1–C3 | A, B, C | Each member's log |
| 6 | Phase 5 – Data Restructuring (schema, migration, validation) | B | Guide §3.2 |
| 7 | Phase 6 – Forward Engineering (architecture, comparison, mapping, evidence; set B) | C | Guide §4.5 |
| 8 | Risk register | A (all add risks) | Done, kept current |
| 9 | Testing: legacy baseline, regression tests, results | C (A and B add theirs) | Guide §4.4 |
| 10 | Work distribution table with signatures | All | Below |
| Appendix | Repository link, how to run, commit list | A | README |

### 5.2 Work distribution table (to sign)

| Member | Phases and tasks | Refactorings | Deliverables owned | Signature |
| --- | --- | --- | --- | --- |
| A – Malik Nouman Ahmed | 1 Inventory Analysis; 2 Document Restructuring; risk register; Django skeleton; report assembly | A1 `-1` sentinel → explicit state; A2 self-validating entities; A3 Money value object | `docs/01`–`05`, `analysis/`, `core/money.py`, `members/`, `inventory/` (Category), report sections 2, 3, 8 | |
| B | 3 Reverse Engineering; 5 Data Restructuring; data layer | B1 Extract Repository; B2 explicit mapping; B3 validated import | Models and migrations, `repositories.py`, `import_legacy`, report sections 4, 6 | |
| C | 6 Forward Engineering; testing | C1 presentation separated (MVC, Observer); C2 checkout service; C3 discount strategies | Services, views, templates, regression tests, report sections 7, 9 | |

### 5.3 Slides (10 minutes, about 3 minutes each)

| Slide | Content | Presenter |
| --- | --- | --- |
| 1 | Title, team, legacy system in one sentence | A |
| 2 | Inventory: assets, classification, dependency map; live run of SonarQube and the inventory script | A |
| 3 | Legacy architecture, worst defect P1, risk register highlights | A |
| 4 | Refactorings A1–A3 (before/after) | A |
| 5 | Reverse engineering: metrics and top smells | B |
| 6 | New database schema and migration results | B |
| 7 | Refactorings B1–B3 | B |
| 8 | New layered architecture and comparison with legacy | C |
| 9 | Live demo of checkout; refactorings C1–C3 | C |
| 10 | Test evidence and measured improvements | C |

Every member must be able to explain and change their own work live; work a member cannot explain earns no marks.

### 5.4 Git rules

1. Before the first commit: `git config --global user.email "<email on your GitHub account>"`.
2. Work on a branch named after you and the task, for example `b/repositories` or `c/checkout-service`.
3. One commit per refactoring; the message names it ("Refactoring B1: …").
4. Open a pull request into `main`; another member reviews; all tests pass before merging.
5. Never force-push `main`; never commit `.venv/`, `db.sqlite3` or `.env` (already in `.gitignore`).
6. Check contributions with `git shortlog -sn`; every member must appear.

## 6. Alignment with the project requirements

When Members B and C finish the tasks in Sections 3 and 4, every requirement of the brief is covered by a named deliverable. Member A's rows are done; update the Status column as each item lands.

### 6.1 The six phases and throughout-project activities

| Requirement (brief) | Owner | Deliverable that satisfies it | Status |
| --- | --- | --- | --- |
| 1 Inventory Analysis: identify code, libraries, configs, docs, tests; classify active/obsolete/reusable; map dependencies | A | Report §2: asset tables with Status/Reuse on every asset, 3 dependency maps verified by `jdeps`, INV-1 to INV-8; tool evidence (inventory script, SonarQube) | Done |
| 2 Document Restructuring: documentation of actual structure and operation | A | Report §3: overview, use case, architecture, class and sequence diagrams, data dictionary, BR-01 to BR-18 | Done |
| 3 Reverse Engineering: recover design, detect weaknesses, code and data smells | A (design, seed smells) + B (depth) | Design recovery done by A; B adds metrics, recovered algorithms, full smell catalogues (Guide §3.1) | In progress |
| 4 Code Restructuring: refactor for modularity and lower complexity | A, B, C | 9 refactorings: A1–A3 done; B1–B3, C1–C3 to do | In progress |
| 5 Data Restructuring: normalise, migrate to a relational DB, resolve inconsistencies | B | Schema, ER diagram, `import_legacy`, inconsistencies table, validation report (Guide §3.2) | To do |
| 6 Forward Engineering: deliver a layered, modular, maintainable system | C (+ A skeleton) | Django apps, services, views, templates (Guide §4) | In progress |
| Risk register with likelihood, impact, mitigation | A (all add) | Report §5, 17 risks, kept current | Done |
| Tests showing functionality is preserved | C (+ A, B) | 45 legacy tests run; 44 tests for A's code; regression tests per rule (Guide §4.4) | In progress |

### 6.2 Improved architecture features

| Required feature | How it is met | Owner | Status |
| --- | --- | --- | --- |
| Defined layers: Presentation, Business Logic, Data Access | views/templates → services → repositories | C, B | To do |
| Clean separation of UI, logic and persistence | C1 (no UI code in business classes), B1 (no queries outside repositories) | C, B | In progress |
| Centralised business rules and service layer | C2 `CheckoutService` + `LoyaltyPolicy`; A's entity rules | C, A | To do |
| Database integration via repository or ORM | Django ORM wrapped by B1 repositories | B | To do |
| Configurable and testable design | Environment-based settings (done); Django test suite | A, C | In progress |
| Design patterns: MVC, Repository, Singleton, Observer | Django MVT; B1; `LoyaltyPolicy`; `sale_completed` signal | C, B | To do |
| Legacy and reengineered architecture diagrams, comparison table, justification | Legacy diagrams (A, done); new diagrams, comparison, justification (C) | A, C | To do |

### 6.3 Documentation requirements

| Required item | Owner | Where | Status |
| --- | --- | --- | --- |
| A: system overview and module inventory | A | Report §3.1, §3.2, §3.4 | Done |
| A: extracted architecture and class diagrams | A | Report §3.3, §3.5 (+ use case, sequence) | Done |
| A: code/data smells and weaknesses | A (+ B expands) | Report §4.1–4.4 | Done |
| A: dependencies and limitations | A | Report §2.7–2.8, §4.2 | Done |
| B: improved architecture and design diagrams | C | Guide §4.5 | To do |
| B: refactored module and data structures | B, C | Refactoring logs; models | To do |
| B: database schema and migration summary | B | Guide §3.2 | To do |
| B: technology stack and rationale | C | Guide §4.5 | To do |
| B: mapping from old to new components | C | Guide §4.5 | To do |
| B: evidence of architectural improvement | C | Measured before/after numbers, Guide §4.5 | To do |
| C: at least 3 major refactorings per member, with before/after and reasoning | A (done), B, C | Refactoring logs | To do |
| Work distribution table, signed by all | All | Guide §5.2 | To do |

### 6.4 Deliverables and guidelines

| Requirement | Owner | Status |
| --- | --- | --- |
| Each member contributes to at least one major phase deliverable (A: phases 1 and 2) | All | Done |
| Technical report covering all six phases | A merges, all write | To do |
| Slides for the 10-minute presentation | All | To do |
| Every member can explain and change their own work | All | To do |
| Reengineered codebase with database schema and configuration | B, C (A skeleton) | In progress |
| Framework and database choices justified | C, B | To do |
| Private repository with each member's own commits | All | In progress |
| Preserve functionality; trace every change to a finding | All (rules BR-01 to BR-18 and finding IDs in place) | In progress |

### 6.5 Marks coverage

| Criterion | Marks | Covered by |
| --- | --- | --- |
| Inventory & Document Restructuring | 15 | A |
| Reverse Engineering & Smell Detection | 15 | B (A's findings as base) |
| Code & Data Restructuring | 20 | A, B, C refactorings; B data restructuring |
| Forward Engineering (Improved Architecture) | 15 | C (+ B data layer) |
| Refactoring Documentation | 10 | A, B, C (3 each) |
| Risk Analysis & Testing | 10 | A register; C regression tests; all tests |
| Dual Documentation (Legacy ↔ Reengineered) | 10 | A legacy set; C reengineered set; B schema |
| Presentation & Work Distribution | 5 | All |
