"""Refactoring A2 applied to Member: self-validation + uniqueness in the service.

Messages are the legacy ones (MemberManager.addMember).
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from members.models import Member
from members.services import add_member, get_member


class MemberRegistrationTests(TestCase):

    def test_new_member_is_registered_as_first_purchase(self):
        add_member("A0042253U", "Ang Hao Yang")
        member = get_member("A0042253U")
        self.assertEqual(member.name, "Ang Hao Yang")
        self.assertTrue(member.is_first_purchase)
        self.assertEqual(member.loyalty_points, 0)

    def test_blank_member_id_is_rejected(self):
        for blank in ["", "  ", None]:
            with self.assertRaisesMessage(ValidationError, "Member ID field is blank. Please input again"):
                add_member(blank, "No Id")

    def test_duplicate_member_id_is_rejected(self):
        add_member("X437F356", "Suraj Sharma")
        with self.assertRaisesMessage(ValidationError, "Member ID X437F356 already existed. Please input again"):
            add_member("X437F356", "Someone Else")

    def test_member_ids_stay_case_sensitive_like_legacy(self):
        add_member("ISSAS", "Ashok Swarnalatha")
        self.assertIsNone(get_member("issas"))

    def test_invalid_member_cannot_be_saved_directly(self):
        with self.assertRaises(ValidationError):
            Member(member_id="   ", name="x").save()
        self.assertEqual(Member.objects.count(), 0)
