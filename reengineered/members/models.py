from django.core.exceptions import ValidationError
from django.db import models


class Member(models.Model):
    """A registered customer who earns and redeems loyalty points.

    Refactoring A1 (Replace Magic Number with explicit state):
    the legacy class stored ``loyaltyPoint = -1`` to mean "has never
    purchased" (Member.java:21). Here the balance is never negative and the
    "first purchase" fact is its own field.
    """

    member_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    loyalty_points = models.PositiveIntegerField(default=0)
    has_purchased = models.BooleanField(default=False)

    class Meta:
        ordering = ["member_id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.member_id})"

    # --- creation -------------------------------------------------------

    @classmethod
    def from_legacy(cls, name: str, member_id: str, legacy_points: int) -> "Member":
        """Build a member from a legacy ``Members.dat`` row.

        Legacy treated any negative balance as "never purchased"
        (Member.addLoyaltyPoint: ``if (this.loyaltyPoint < 0)``).
        """
        if legacy_points < 0:
            return cls(member_id=member_id, name=name, loyalty_points=0, has_purchased=False)
        return cls(member_id=member_id, name=name, loyalty_points=legacy_points, has_purchased=True)

    # --- queries --------------------------------------------------------

    @property
    def is_first_purchase(self) -> bool:
        """True until the member completes a purchase (qualifies for MEMBER_FIRST)."""
        return not self.has_purchased

    # --- behaviour ------------------------------------------------------

    def redeem(self, points: int) -> None:
        """Spend points; raises if more than the balance (BR-12)."""
        if points < 0 or points > self.loyalty_points:
            raise ValidationError("Loyalty Point is not enough")
        self.loyalty_points -= points

    def record_purchase(self, earned_points: int) -> None:
        """Credit points earned by a completed sale (BR-13)."""
        if earned_points < 0:
            raise ValidationError("Earned points cannot be negative")
        self.loyalty_points += earned_points
        self.has_purchased = True
