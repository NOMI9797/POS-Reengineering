"""Refactoring A3: Money value object replaces double.

The receipt scenario uses legacy sample transaction 1
(2 x CLO/1 @ 21.45 + 3 x MUG/1 @ 10.25, member, 10 % MEMBER_SUBSEQ).
"""
from decimal import Decimal

from django.test import SimpleTestCase

from core.money import Money


class LegacyReceiptScenarioTests(SimpleTestCase):

    def setUp(self):
        self.subtotal = Money("21.45").times(2) + Money("10.25").times(3)
        self.discount = self.subtotal.percent_of(10)
        self.total = self.subtotal - self.discount

    def test_subtotal_matches_legacy(self):
        self.assertEqual(self.subtotal, Money("73.65"))

    def test_discount_matches_legacy_display(self):
        self.assertEqual(self.discount, Money("7.37"))

    def test_D_A3_total_now_adds_up(self):
        # legacy printed $66.29 because it rounded 66.28500000000001 only at display time
        self.assertEqual(self.total, Money("66.28"))
        self.assertEqual(self.subtotal - self.discount, self.total)

    def test_points_earned_on_subtotal_unchanged(self):
        # BR-13: floor(subtotal / 10)
        self.assertEqual(self.subtotal.whole_units_of(10), 7)

    def test_max_redeemable_points_unchanged(self):
        # BR-12: floor(total / 5); legacy floor(66.285 / 5) = 13
        self.assertEqual(self.total.whole_units_of(5), 13)

    def test_receipt_formatting(self):
        self.assertEqual(
            [str(self.subtotal), str(self.discount), str(self.total)],
            ["$73.65", "$7.37", "$66.28"])


class MoneyBehaviourTests(SimpleTestCase):

    def test_always_two_decimals(self):
        self.assertEqual(str(Money(5)), "$5.00")
        self.assertEqual(Money("2.5").amount, Decimal("2.50"))

    def test_rounds_half_up_where_float_would_not(self):
        # float: round(2.675, 2) == 2.67 because 2.675 is stored as 2.67499...
        self.assertEqual(Money("2.675"), Money("2.68"))

    def test_float_input_is_refused(self):
        with self.assertRaises(TypeError):
            Money(21.45)

    def test_sum_of_line_totals(self):
        lines = [Money("21.45").times(2), Money("10.25").times(3)]
        self.assertEqual(sum(lines), Money("73.65"))
        self.assertEqual(sum([], Money.ZERO), Money.ZERO)

    def test_no_discount_is_zero(self):
        self.assertEqual(Money("73.65").percent_of(0), Money.ZERO)

    def test_change_is_negative_balance(self):
        balance = Money("66.28") - Money("70")
        self.assertTrue(balance.is_negative())
        self.assertEqual(str(Money.ZERO - balance), "$3.72")

    def test_points_floor_below_one_unit(self):
        self.assertEqual(Money("9.99").whole_units_of(10), 0)

    def test_is_immutable(self):
        m = Money("1.00")
        with self.assertRaises(AttributeError):
            m.amount = Decimal("2.00")

    def test_comparison(self):
        self.assertLess(Money("4.99"), Money("5.00"))
