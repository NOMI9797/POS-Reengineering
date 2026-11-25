"""Money value object.

Refactoring A3 (Replace Primitive with Object): the legacy system kept
prices, subtotals, discounts and payments in ``double`` and rounded only when
printing (Util.formatDollar). Sample transaction 1 with a 10 % discount
printed Subtotal $73.65, Discount $7.37, Total $66.29, a receipt that does
not add up. Money always holds exactly two decimals, rounds half-up in one
place, and cannot be built from a float.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True, order=True)
class Money:
    amount: Decimal

    def __post_init__(self):
        if isinstance(self.amount, float):
            raise TypeError("Money cannot be created from float; pass a str, int or Decimal")
        value = Decimal(self.amount).quantize(CENT, rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", value)

    # --- arithmetic -----------------------------------------------------

    def __add__(self, other: Money) -> Money:
        return Money(self.amount + other.amount)

    def __radd__(self, other):
        # lets sum(list_of_money) work (sum starts from int 0)
        if other == 0:
            return self
        return NotImplemented

    def __sub__(self, other: Money) -> Money:
        return Money(self.amount - other.amount)

    def times(self, quantity: int) -> Money:
        return Money(self.amount * quantity)

    def percent_of(self, percent) -> Money:
        """``percent`` % of this amount, rounded to the cent once (BR-11)."""
        return Money(self.amount * Decimal(str(percent)) / 100)

    def whole_units_of(self, divisor: int) -> int:
        """floor(amount / divisor): points earned (/10, BR-13) and
        maximum redeemable points (/5, BR-12)."""
        return int((self.amount / divisor).to_integral_value(rounding=ROUND_FLOOR))

    # --- queries / formatting -------------------------------------------

    def is_negative(self) -> bool:
        return self.amount < 0

    def __str__(self) -> str:
        return f"${self.amount}"


Money.ZERO = Money(Decimal("0"))
