# Handoff from Member A to Members B and C

This file passes on what the inventory and legacy analysis found, so B (reverse engineering + data) and C (forward engineering + testing) can start immediately. It also proposes **3 concrete refactorings per member**, each tied to real code, so everyone meets the "3 major refactorings each" rule without overlap.

> Legacy clone: `legacy-pos/`. Re-run the defect probes: `analysis/legacy-bug-probe/run-probe.sh`. Re-run the legacy tests: see "How to run" at the end.

---

## 1. Ownership split for refactorings (no overlap)

| Member | Layer | Refactorings |
|---|---|---|
| **A** | Domain entities | A1 replace `-1` sentinel · A2 self-validating entities · A3 Money value object (see `04-refactorings-member-A.md`) |
| **B** | Data access / persistence | B1 Extract Repository · B2 Replace `toString()` serialisation with explicit mapping · B3 Replace error swallowing with validated loading |
| **C** | Service + presentation | C1 Move TableModels out of the managers (Observer/MVC) · C2 Extract Service for checkout/loyalty rules · C3 Replace hard-coded discount codes with a Strategy |

---

## 2. For Member B: reverse engineering and data

### 2.1 Code smells already found (seed list for the smell catalogue)

| # | Smell | Where | Notes |
|---|---|---|---|
| S-01 | **Divergent change / God class (low cohesion)** | `ProductManager` (246 LOC, 19 methods), `TransactionManager`, `MemberManager`, `CategoryManager`, `DiscountManager` | Each mixes CSV I/O, validation, business rules and a Swing table model |
| S-02 | **Duplicated code** | 7 × `load()`/`store()` doing `Files.lines → splitCsv → forEach`; 7 × near-identical `getTableModel()`; `ProductManager` has 2 copies of the same table model (lines 174-234) | |
| S-03 | **Large class / long method** | `ConfirmPaymentDialog.getPaymentPanel()` ≈ 200 lines; `ReceiptDialog.getAdditionalInfo()` ≈ 140 lines | |
| S-04 | **Feature envy / misplaced business logic** | Redemption cap computed in `ConfirmPaymentDialog:158-184`, `Transaction:206-207`, `TransactionManager:159-164` | One version compares **points with dollars** (`Transaction.java:207`) |
| S-05 | **Layer violation** | `javax.swing` imported in 6 non-GUI classes | Back end cannot run headless |
| S-06 | **Magic numbers/strings** | `-1`, `"ALWAYS"`, `"PUBLIC"`, `"M"/"A"`, `"MEMBER_FIRST"`, file paths, column indexes `fireTableCellUpdated(index, 3)` | |
| S-07 | **Primitive obsession** | Money as `double`; product ID `CAT/n` as a string that also encodes the category | |
| S-08 | **Dead code** | `AdhesiveLabelPrinter`, `Printer.id/count/getTag`, `VendorManager` (never queried), 3 `FeaturePanel` constructors, ≈62 commented-out lines, unused imports (`ProductPanel` imports `Consumer`, `Function`, `Supplier`) | |
| S-09 | **Swallowed exceptions** | 16 × `printStackTrace()` | |
| S-10 | **Temporal coupling** | `requestedId` + `setId()`; `Transaction` locked once `id` is set; `TransactionManager.load` must delay `setId` ("or it will lock addTransactionItem", line 82) | |
| S-11 | **Inappropriate intimacy** | GUI reads `TransactionManager.POINT_TO_DOLLAR`/`DOLLAR_TO_POINT` constants directly | |
| S-12 | **Copy-paste error** | `ConfirmPaymentDialog.java:110` sets `redeemLabel` instead of `redeemValueLabel`; lines 116-117 set `redeemTA` instead of `redeemValueTA` | Real UI bug |
| S-13 | **Global mutable state** | `Util.DATE_FORMAT` is a shared static `SimpleDateFormat` (not thread-safe), also passed to GUI fields | |

### 2.2 Defects confirmed by running the legacy code (`probe-output.txt`)

| Probe | Defect | Location |
|---|---|---|
| P1 | After any new sale, **all past member sales are rewritten as `PUBLIC`** (inverted condition) | `TransactionManager.java:78-80` |
| P2 | `NullPointerException` in `deductQuantity` when the understock table model does not exist yet | `ProductManager.java:146-150` |
| P3 | Lower-case category accepted, then unreachable | `CategoryManager.java:54, 66-77` |
| P4 | Comma inside a field corrupts the row on reload | `Util.splitCsv` |
| P5 | One malformed line → exception escapes the constructor → app cannot start | every `load()` |
| P6 | Duplicate discount silently ignored | `DiscountManager.java:84`, `StoreApplication.java:61` |
| P7 | With 2014 data, the public best discount is none; member discounts work | `Discounts.dat` |
| P8 | `Transaction.getId()` throws NPE before the sale is saved (`Integer` unboxing) | `Transaction.java:52` |

Found by code reading (not executed):
* **R1.** The transaction report's end-date filter compares with midnight. Sales made in the current session carry a time of day, so typing today's date as End Date leaves them out (`ReportPanel.java:99-115`).
* **R2.** `TransactionItem.toString()` calls `parent.getCustomer()` before the `parent != null` check (`TransactionItem.java:40-43`).
* **R3.** `addTransaction` can throw "Insufficient Amount", and `CheckoutPanel` does not catch it (`CheckoutPanel.java:126`).

### 2.3 Data smells (input to Phase 5)

| # | Data smell | Normalisation fix |
|---|---|---|
| DS-1 | `Transactions.dat` repeats memberId and date on every line of the same sale | Split into `sale` (header) and `sale_line` tables (2NF) |
| DS-2 | Unit price, discount, redeemed/earned points and payment are not stored | Add `sale_line.unit_price`, `sale.discount_code`, `sale.discount_amount`, `sale.points_redeemed`, `sale.points_earned`, `sale.amount_paid` |
| DS-3 | The category is encoded inside the product ID (`CLO/1`) | `product.category_code` FK, keeping `product_code` as a unique business key |
| DS-4 | The category is encoded in vendor file names; identical rows across 5 files | `vendor` + `vendor_category` (M:N) tables |
| DS-5 | `-1` sentinel for points; `ALWAYS` for dates/period; `M/A` flag | `has_purchased BOOLEAN`, nullable `start_date`/`period_days`, `applies_to ENUM('MEMBER','ALL')` |
| DS-6 | `PUBLIC` pseudo-member ID | `sale.member_id` nullable FK (NULL = public customer) |
| DS-7 | Plain-text passwords | `storekeeper.password_hash` |
| DS-8 | No quoting/escaping, no header, no trailing newline, no schema | Relational schema with types and constraints |
| DS-9 | Spelling: "Stationary" (should be "Stationery"), "Sovenirs", "momento" | Decide: keep as-is (data fidelity) and note it, or clean during migration and log the change |
| DS-10 | Migration data: use `data-sample/`, because any `data/` copy may already be damaged by P1 | Validation report: row counts, FK checks, rejected rows |

### 2.4 B's refactorings (proposed)

| ID | Refactoring | Before (legacy) | After | Traces to |
|---|---|---|---|---|
| **B1** | **Extract Class → Repository** (Repository pattern) | `load()`/`store()` copied into 7 managers `repositories.py` per app (`CategoryRepository`, `ProductRepository`, ...) wrapping the Django ORM; services call the repository, never `Model.objects` directly, so tests can swap in a fake | S-01, S-02, INV-1 |
| **B2** | **Replace `toString()` serialisation with an explicit mapper/ORM mapping** | `Product.toString()` is the file format; `TransactionItem.toString()` writes the CSV row (and corrupts on commas, P4; drops the member, P1) Django models define the table mapping; a separate `legacy_import` mapper (Python `csv` module, which handles quoting) converts each `.dat` row → model; `__str__` is used only for display | P1, P4, DS-1 |
| **B3** | **Replace error swallowing with validated, row-level loading** (Replace Error Code with Exception + Introduce Special Case for "rejected row") | `printStackTrace()` ×16; a bad line aborts start-up (P5) | The import management command (`python manage.py import_legacy data-sample/`) returns `ImportResult(imported, rejected=[(line, reason)])`; Python `logging` instead of `printStackTrace` | S-09, P5, L-15 |

---

## 3. For Member C: forward engineering and testing

### 3.1 C's refactorings (proposed)

| ID | Refactoring | Before (legacy) | After | Traces to |
|---|---|---|---|---|
| **C1** | **Move Method: separate presentation models from business classes** (MVC + Observer) | 7 `getTableModel()` in managers and `Transaction`; `fireTableRowsInserted` calls inside business methods; NPE P2 | Services return plain data; Django views + templates (MVT = Django's MVC) render tables; Observer via Django **signals** (e.g. `sale_completed` → understock alert); no HTML/view code below the view layer | S-05, L-12, P2 |
| **C2** | **Extract Service: checkout and loyalty rules into `CheckoutService` / `LoyaltyPolicy`** | Redemption cap in 3 places (one compares points with dollars); point rates read by the GUI from `TransactionManager` | One `LoyaltyPolicy` (`EARN_DOLLARS_PER_POINT=10`, `POINT_VALUE=5` read from `settings.py`/env); `checkout_service.complete(sale)` does debit, credit, stock and save inside **`transaction.atomic()`** | S-04, S-11, BR-12…15, L-11, L-13 |
| **C3** | **Replace Conditional with Polymorphism (Strategy)** for discount eligibility | `if (code.equals("MEMBER_FIRST") …)` hard-coded in `DiscountManager.getMaxDiscount` | `DiscountRule` strategy classes: `AllCustomersRule`, `MemberOnlyRule`, `FirstPurchaseRule`, `SubsequentPurchaseRule`; `today` is passed in (or `django.utils.timezone.now` is mocked) for the date window (R-11) | S-06, BR-07…09 |

### 3.2 Regression tests needed (one per business rule)

Write tests for BR-01 … BR-18 (`02-legacy-system-documentation.md §2.4`). Concrete expected values from the sample data:

| Case | Expected |
|---|---|
| Member `F42563743156` (150 pts) buys 2 × CLO/1 + 3 × MUG/1 | subtotal $73.65, discount `MEMBER_SUBSEQ` 10 % = $7.37, total $66.28, earns 7 points, max redeem 13 points |
| New member `R64565FG4` (−1 → first purchase) | `MEMBER_FIRST` 20 % |
| Public customer, today | no discount (all promotions date from 2014) |
| Quantity above stock (e.g. 769 × STA/1 with stock 768) | rejected "Exceeded inventory quantity." |
| Inventory screen with sample data (DIA/2 has qty 113, threshold 10) | DIA/2 is not understock, so it is not listed |
| Add product to MUG | id `MUG/3` |
| Add category `CLO` again | "Category CLO already existed. Please input again" |

---

## 4. How to run the legacy system and tests (macOS/Linux, JDK 11+)

```bash
cd legacy-pos
# compile
mkdir -p /tmp/legacy-out
javac -encoding UTF-8 -d /tmp/legacy-out $(find src -name '*.java')

# run the GUI (needs a data/ folder in the working directory)
cp -r data-sample data
java -cp /tmp/legacy-out sg.edu.nus.iss.se24_2ft.unit1.ca.StoreApplication     # login: Stacy / Dean56s

# run the 45 legacy JUnit tests (download junit-4.12.jar + hamcrest-core-1.3.jar first)
javac -encoding UTF-8 -d /tmp/legacy-out -cp junit-4.12.jar $(find src test -name '*.java')
(cd test && find sg -name '*Test.java' | sed 's/\.java$//; s#/#.#g') | \
  xargs java -cp /tmp/legacy-out:junit-4.12.jar:hamcrest-core-1.3.jar org.junit.runner.JUnitCore
# → OK (45 tests)
```
