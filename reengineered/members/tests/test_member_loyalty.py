"""Refactoring A1: the -1 "never purchased" sentinel replaced by has_purchased.

Each test pins down a behaviour of the legacy Member/MemberManager/
DiscountManager code (see docs/04-refactorings-member-A.md, table "Behaviour
preserved") so the new model behaves the same way.
"""
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from members.models import Member


class LegacyMappingTests(SimpleTestCase):
    """Members.dat column 3 -> (loyalty_points, has_purchased)."""

    def test_minus_one_means_first_purchase_with_zero_points(self):
        m = Member.from_legacy("Ang Lee", "R64565FG4", -1)
        self.assertEqual(m.loyalty_points, 0)
        self.assertTrue(m.is_first_purchase)

    def test_positive_points_mean_member_has_purchased(self):
        m = Member.from_legacy("Yan Martel", "F42563743156", 150)
        self.assertEqual(m.loyalty_points, 150)
        self.assertFalse(m.is_first_purchase)

    def test_zero_points_is_a_real_balance_not_first_purchase(self):
        # legacy: 0 != -1, so MEMBER_SUBSEQ applies
        m = Member.from_legacy("Someone", "X1", 0)
        self.assertFalse(m.is_first_purchase)

    def test_any_negative_value_is_treated_as_never_purchased(self):
        # legacy addLoyaltyPoint used "< 0", not "== -1"
        m = Member.from_legacy("Someone", "X2", -5)
        self.assertEqual(m.loyalty_points, 0)
        self.assertTrue(m.is_first_purchase)


class LoyaltyBehaviourTests(SimpleTestCase):

    def test_new_member_starts_with_zero_points_and_first_purchase(self):
        m = Member(member_id="A0001", name="New")
        self.assertEqual(m.loyalty_points, 0)
        self.assertTrue(m.is_first_purchase)

    def test_first_purchase_credits_points_and_clears_flag(self):
        # legacy: -1 -> 7 after a $73.65 sale (floor(73.65 / 10) = 7)
        m = Member.from_legacy("Ang Lee", "R64565FG4", -1)
        m.record_purchase(7)
        self.assertEqual(m.loyalty_points, 7)
        self.assertFalse(m.is_first_purchase)

    def test_first_purchase_under_ten_dollars_still_ends_first_purchase(self):
        # legacy: -1 -> 0, so the next sale gets MEMBER_SUBSEQ
        m = Member.from_legacy("Ang Lee", "R64565FG4", -1)
        m.record_purchase(0)
        self.assertEqual(m.loyalty_points, 0)
        self.assertFalse(m.is_first_purchase)

    def test_debit_then_credit_like_legacy_checkout(self):
        # TransactionManager.addTransaction: debit redeemed, then credit earned
        m = Member.from_legacy("Yan Martel", "F42563743156", 150)
        m.redeem(13)
        m.record_purchase(7)
        self.assertEqual(m.loyalty_points, 144)

    def test_redeem_more_than_balance_is_rejected_with_legacy_message(self):
        m = Member.from_legacy("Yan Martel", "F42563743156", 150)
        with self.assertRaisesMessage(ValidationError, "Loyalty Point is not enough"):
            m.redeem(151)
        self.assertEqual(m.loyalty_points, 150)

    def test_first_purchase_member_cannot_redeem(self):
        # legacy: -1 points -> UI max redeem 0, debit of >0 rejected
        m = Member.from_legacy("Ang Lee", "R64565FG4", -1)
        with self.assertRaises(ValidationError):
            m.redeem(1)

    def test_negative_amounts_are_rejected(self):
        m = Member.from_legacy("Yan Martel", "F42563743156", 150)
        with self.assertRaises(ValidationError):
            m.redeem(-1)
        with self.assertRaises(ValidationError):
            m.record_purchase(-1)


class PersistenceTests(TestCase):

    def test_state_survives_a_database_round_trip(self):
        Member.from_legacy("Ang Lee", "R64565FG4", -1).save()
        m = Member.objects.get(member_id="R64565FG4")
        m.record_purchase(7)
        m.save()
        reloaded = Member.objects.get(member_id="R64565FG4")
        self.assertEqual(reloaded.loyalty_points, 7)
        self.assertFalse(reloaded.is_first_purchase)
