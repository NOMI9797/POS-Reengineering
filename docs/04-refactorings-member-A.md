# Refactoring Log: Member A (Domain Model)

**Scope owned by Member A:** the domain/entity layer (`Category`, `Member`, `Discount`, `Product`, `Transaction` values).
**Rule followed:** each refactoring
* traces to an inventory (INV-x) or legacy-analysis (L-x) finding,
* keeps the business rules in `02-legacy-system-documentation.md §2.4` unchanged,
* is protected by tests written **before** the change, so the legacy behaviour is pinned down first.

**Target stack:** Python 3.12/3.13 + Django 5.2 LTS. "Before" is the legacy Java code. "After" is the code in the reengineered Django project:
* entities are Django models in `<app>/models.py`,
* business rules live in `<app>/services.py`,
* value objects live in `core/money.py`.

Each refactoring is committed separately, and the commit hash is recorded in the last row of each table.

| # | Refactoring (catalogue name) | Smell removed | Classes |
|---|---|---|---|
| A1 | **Replace Magic Number with explicit state** (Replace Type Code with Field + Introduce Query) | Magic number `-1` used as "never purchased" flag | `Member`, `MemberManager`, `DiscountManager`, `ConfirmPaymentDialog` |
| A2 | **Remove Setting Method + Move validation into constructor** (self-validating entity) | Temporal coupling (`requestedId` → `setId()`), duplicated and inconsistent validation | `Category`, `CategoryManager` (same pattern in `Member`, `Discount`) |
| A3 | **Replace Primitive with Object** (Money value object) | Primitive obsession: money held in `double` | `Product`, `Transaction`, `Util`, receipt/payment code |

**Status:** all three implemented. Run with `cd reengineered && python manage.py test` (44 tests total, all passing).

---

## A1: Replace magic number `-1` with explicit "has purchased" state

| | |
|---|---|
| **Smell** | Magic number / primitive used as a type code. `loyaltyPoint == -1` means "this member has never purchased", and every reader must know this hidden rule. |
| **Found in** | `Member.java:21, 53-56, 60`; `MemberManager.java:38` (default `-1`); `DiscountManager.java:63-68`; `ConfirmPaymentDialog.java:159-160` (clamps `-1` to 0) |
| **Traces to** | Phase 3 smell catalogue; data dictionary `Members.dat` column 3; BR-03, BR-09, BR-13 |
| **Why it matters** | 4 classes in 3 packages repeat the same `-1` checks. A balance of `-1` is not a real number of points, yet it is shown in the Member report. Arithmetic must special-case it (`addLoyaltyPoint`, `removeLoyaltyPoint`). |

### Before (legacy)

```java
// Member.java
public Member(String requestedId, String name) {
    ...
    loyaltyPoint = -1;                              // magic value
}
void addLoyaltyPoint(int loyaltyPoint) {
    if (this.loyaltyPoint < 0) setLoyaltyPoint(loyaltyPoint);   // special case
    else this.loyaltyPoint += loyaltyPoint;
}
int removeLoyaltyPoint(int loyaltyPoint) {
    if (this.loyaltyPoint < 0) return 0;            // special case
    ...
}

// DiscountManager.java  (getMaxDiscount)
int loyaltyPoint = ((Member) customer).getLoyaltyPoint();
String code = d.getCode().toUpperCase();
if (code.equals("MEMBER_FIRST") && loyaltyPoint != -1) return false;
if (code.equals("MEMBER_SUBSEQ") && loyaltyPoint == -1) return false;

// ConfirmPaymentDialog.java
int memberPoint = member != null ? member.getLoyaltyPoint() : 0;
if (memberPoint < 0) memberPoint = 0;               // GUI must know about -1 too
```

### After

```python
# members/models.py
class Member(models.Model):
    member_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    loyalty_points = models.PositiveIntegerField(default=0)   # invariant: never negative
    has_purchased = models.BooleanField(default=False)        # replaces the -1 sentinel

    @classmethod
    def from_legacy(cls, name, member_id, legacy_points):    # used by the data migration
        if legacy_points < 0:                                  # legacy used "< 0", not "== -1"
            return cls(member_id=member_id, name=name, loyalty_points=0, has_purchased=False)
        return cls(member_id=member_id, name=name, loyalty_points=legacy_points, has_purchased=True)

    @property
    def is_first_purchase(self) -> bool:
        return not self.has_purchased

    def redeem(self, points: int) -> None:
        if points < 0 or points > self.loyalty_points:
            raise ValidationError("Loyalty Point is not enough")
        self.loyalty_points -= points

    def record_purchase(self, earned_points: int) -> None:
        if earned_points < 0:
            raise ValidationError("Earned points cannot be negative")
        self.loyalty_points += earned_points
        self.has_purchased = True


# How callers use it (discount eligibility is built in Member C's refactoring C3):
if discount.code == DiscountCodes.MEMBER_FIRST:
    return member.is_first_purchase
if discount.code == DiscountCodes.MEMBER_SUBSEQ:
    return not member.is_first_purchase

# checkout (Member C, C2): no special case needed any more
max_points = min(member.loyalty_points, total.whole_units_of(5))
```

**Mechanics:**
1. Write the legacy behaviour (table below) as `pytest`/Django `TestCase` tests.
2. Model `has_purchased` as a field and add `is_first_purchase`.
3. Write the eligibility code against `is_first_purchase`.
4. Implement `record_purchase`/`redeem` in place of `addLoyaltyPoint`/`removeLoyaltyPoint`.
5. The migration script converts `-1` (table below).
6. Run the tests after every step.

**Data mapping (agreed with Member B for migration):**

| `Members.dat` loyalty | `member.loyalty_points` | `member.has_purchased` |
|---|---|---|
| `-1` | 0 | false |
| `n ≥ 0` | n | true |

**Behaviour preserved (tests):**

| Test | Legacy result | New result |
|---|---|---|
| New member gets best discount | `MEMBER_FIRST` (20 %) | `MEMBER_FIRST` |
| Member with 150 points | `MEMBER_SUBSEQ` (10 %) | `MEMBER_SUBSEQ` |
| First purchase, subtotal $73.65 | points −1 → 7 | 0 → 7, `has_purchased = True` |
| First purchase, subtotal $5 | points −1 → 0, then `MEMBER_SUBSEQ` next time | 0, `has_purchased = True` → `MEMBER_SUBSEQ` |
| Redeem more than balance | `IllegalArgumentException` "Loyalty Point is not enough" | `ValidationError` with the same message |
| Redeem then earn (150 − 13 + 7) | 144 | 144 |

The first two rows are checked at the model level (`is_first_purchase`); they become full discount-selection tests once the `discounts` app exists (C3).

| Implementation | |
|---|---|
| Commit | `d7579b1` |
| Code | `reengineered/members/models.py` |
| Tests | `reengineered/members/tests/test_member_loyalty.py`: 12 tests, all passing |

---

## A2: Remove two-step ID initialisation; validate inside the entity

| | |
|---|---|
| **Smell** | Temporal coupling and duplicated, inconsistent validation. Entities are built with a `requestedId` and an empty `id`. The manager validates elsewhere and then calls a package-private `setId()`. The same pattern is copied into `Category`, `Member` and `Discount`. Validation in `load()` and in `addCategory()` differs. |
| **Found in** | `Category.java:10-23`; `CategoryManager.java:36-47` vs `62-77`; `CategoryManager.java:54-55` (only lookup upper-cases); same pattern in `Member.java:12-23, 47` and `Discount.java:12-22, 69` |
| **Traces to** | Limitation **L-04 (verified, probe P3):** a lower-case code `bks` is accepted but can never be found. The original TODO comments at `DiscountManager.java:83` ("check constraint for all add") and `CategoryPanel.java:66` ("validate category"). |
| **Why it matters** | An object can exist in an invalid half-built state (`getId()` returns `null`, `toString()` then throws). Each new caller must remember to validate and call `setId()`. |

### Before (legacy)

```java
// Category.java
public Category(String requestedId, String name) {
    id = null;                                         // half-built object
    this.requestedId = (requestedId != null ? requestedId.trim() : null);
    this.name = (name != null ? name.trim() : null);
}
/*package*/ void setId() { id = requestedId; }         // must be called later

// CategoryManager.java – load(): one set of rules
if (categoryMap.containsKey(requestedId)) return;
if (requestedId.length() != 3) return;
category.setId();

// CategoryManager.java – addCategory(): another set of rules
if (categoryId == null || categoryId.isEmpty()) throw ...("Category ID is blank, please input again");
if (categoryMap.get(categoryId) != null)       throw ...("Category " + categoryId + " already existed...");
if (categoryId.length() != 3)                  throw ...("Category ID must be three letter code");
category.setId();

// lookup normalises, storage does not  →  "bks" stored, getCategory("bks") looks for "BKS"
public Category getCategory(String id) { return categoryMap.get(id.toUpperCase()); }
```

### After

```python
# inventory/models.py
CATEGORY_CODE = re.compile(r"^[A-Z]{3}$")

class Category(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100, blank=True)

    def clean(self):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        if not self.code:
            raise ValidationError("Category ID is blank, please input again")
        if not CATEGORY_CODE.match(self.code):
            raise ValidationError("Category ID must be three letter code")

    def save(self, *args, **kwargs):
        self.clean()          # every path (forms, legacy import, admin) is validated
        super().save(*args, **kwargs)


# inventory/services.py – only the rule that needs the whole table (uniqueness) stays here
def add_category(code: str, name: str) -> Category:
    category = Category(code=code, name=name)
    category.clean()                                    # always valid or raises
    if Category.objects.filter(code=category.code).exists():   # → repository in B1
        raise ValidationError(
            f"Category {category.code} already existed. Please input again")
    category.save()
    return category
```

The same steps are applied to `Member`: `Member.clean()` trims the ID and rejects a blank one with the legacy message "Member ID field is blank. Please input again". `members/services.add_member` keeps the duplicate check ("Member ID … already existed. Please input again"), and member IDs stay case-sensitive as in legacy. `Discount` gets the same treatment when the `discounts` app is built (C3).

**Mechanics:**
1. Add tests for blank, wrong length, duplicate, lower-case and valid input.
2. Put the format checks in the model's `clean()` instead of the manager.
3. Drop `requestedId`/`setId()`: the object is valid from the moment it is cleaned.
4. The data-migration import calls the same `clean()`, so file rows and form input obey one rule set (invalid rows are logged and skipped, as before).
5. Leave the uniqueness check in the service.

**Behaviour preserved / intentional deviations:**

| Input | Legacy | New | Note |
|---|---|---|---|
| `CLO`, `Clothing` | accepted | accepted | |
| `""` | "Category ID is blank…" | same message | |
| `CL` / `CLOT` | "…three letter code" | same message | |
| duplicate `CLO` | "Category CLO already existed…" | same message | |
| `bks` | stored as `bks`, then **unreachable** | stored as `BKS`, usable | **Deviation D-A2a**: fixes defect L-04 |
| `AB1` | accepted | rejected: "three letter code" | **Deviation D-A2b**: matches the legacy error text and the vendor-file rule `[A-Z]{3}` (`VendorManager.java:38`) |
| `Category(code="TOOLONG").save()` directly | (no such path) | rejected, nothing saved | entity guards the database |

| Implementation | |
|---|---|
| Commit | `4dda7ef` |
| Code | `reengineered/inventory/models.py`, `inventory/services.py`, `members/models.py` (`clean`/`save`), `members/services.py` |
| Tests | `reengineered/inventory/tests/test_category_validation.py` (12) + `members/tests/test_member_validation.py` (5): 17 tests, all passing |

---

## A3: Replace `double` money with a `Money` value object

| | |
|---|---|
| **Smell** | Primitive obsession. Prices, subtotal, discount, payment and change are all `double`; rounding happens only when text is displayed (`Util.formatDollar`), in several places. |
| **Found in** | `Product.java:14` (`double price`); `Transaction.java:19, 24, 68-84`; `Util.java:43-45`; `ConfirmPaymentDialog.java`, `ReceiptDialog.java` (format separately) |
| **Traces to** | Limitation **L-08**; risk **R-10**; inventory INV-2 |
| **Evidence (run on the legacy code)** | Sample transaction 1 (2 × CLO/1 @ 21.45 + 3 × MUG/1 @ 10.25) with the 10 % member discount gives raw values subtotal 73.65, discount **7.365000000000001**, total **66.28500000000001**. The legacy receipt shows Subtotal **$73.65**, Discount **$7.37**, Total **$66.29**. But 73.65 − 7.37 = **66.28**, so **the printed receipt does not add up by 1 cent.** |

### Before (legacy)

```java
// Product.java
private double price;

// Transaction.java
private double subtotal;
private double payment;
public double getDiscountAmount() {
    if (discount == null) return 0;
    return (discount.getPercent() / 100.0) * subtotal;     // 7.365000000000001
}
public double getSubtotalAfterDiscount() { return subtotal - getDiscountAmount(); }
...
subtotal += transactionItem.getQuantity() * product.getPrice();

// Util.java – rounding only when printed
public static String formatDollar(double amount) { return "$" + String.format("%.2f", amount); }
```

### After

```python
# core/money.py (abridged; see the file for the full class)
@dataclass(frozen=True, order=True)
class Money:
    amount: Decimal                                    # always 2 decimal places

    def __post_init__(self):
        if isinstance(self.amount, float):             # binary floats are refused
            raise TypeError("Money cannot be created from float; pass a str, int or Decimal")
        value = Decimal(self.amount).quantize(CENT, rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", value)

    def __add__(self, other): return Money(self.amount + other.amount)
    def __sub__(self, other): return Money(self.amount - other.amount)
    def times(self, quantity: int): return Money(self.amount * quantity)

    def percent_of(self, percent):                     # rounded once, here
        return Money(self.amount * Decimal(str(percent)) / 100)

    def whole_units_of(self, divisor: int) -> int:     # floor: points /10, redeem /5
        return int((self.amount / divisor).to_integral_value(rounding=ROUND_FLOOR))

    def __str__(self): return f"${self.amount}"

Money.ZERO = Money(Decimal("0"))


# Intended use in the sales app (Member C, refactoring C2):
subtotal = sum((line.unit_price.times(line.quantity) for line in lines), Money.ZERO)
discount = subtotal.percent_of(discount_percent)
total    = subtotal - discount                         # 73.65 − 7.37 = 66.28
```

**Mechanics:**
1. Create `Money` with its own unit tests (adding, half-up rounding, floor division, formatting).
2. Store prices as `models.DecimalField(max_digits=10, decimal_places=2)` (agreed with Member B) and wrap them in `Money` in the domain/service code.
3. Build the sale totals, payment and change with `Money`.
4. Format with `str(money)` (replaces `Util.formatDollar`).
5. Never build `Money` from a `float`: parse form input and CSV text as `Decimal(str)`.

**Behaviour preserved / intentional deviations:**

| Case | Legacy | New |
|---|---|---|
| Subtotal 2×21.45 + 3×10.25 | $73.65 | $73.65 |
| Points earned on $73.65 (÷10, floor) | 7 | 7 |
| Max redeemable on total (÷5, floor) | ⌊66.285 / 5⌋ = 13 | ⌊66.28 / 5⌋ = 13 |
| Discount 10 % of 73.65 | shows $7.37 | $7.37 |
| Total after discount | shows **$66.29** (inconsistent) | **$66.28** (= 73.65 − 7.37). **Deviation D-A3**: 1-cent correction so the receipt adds up. |
| Rounding 2.675 | float would give 2.67 | 2.68 (half-up) |

| Implementation | |
|---|---|
| Commit | `31f0468` |
| Code | `reengineered/core/money.py` |
| Tests | `reengineered/core/tests/test_money.py`: 15 tests, all passing |

---

## Intentional deviations raised by Member A (for the report's "behaviour changes" table)

| ID | Change | Reason | Evidence |
|---|---|---|---|
| D-A2a | Category codes are stored upper-case | Legacy accepted lower-case codes that could never be found again | Probe P3 |
| D-A2b | Category code must be letters A–Z | Matches the legacy error message and the vendor-file rule | `CategoryManager.java:73`, `VendorManager.java:38` |
| D-A3 | Discount rounded to cents before the total is computed | Legacy receipt does not add up (−1 cent) | Money check above |
