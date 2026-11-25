"""Refactoring A2: Category validates itself; the service only checks uniqueness.

Messages are the legacy ones (CategoryManager.addCategory). The two
deliberate deviations (D-A2a, D-A2b) are tested explicitly.
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory.models import Category
from inventory.services import add_category, get_category


class CategoryRulesPreservedTests(TestCase):

    def test_valid_category_is_added(self):
        add_category("CLO", "Clothing")
        self.assertEqual(get_category("CLO").name, "Clothing")

    def test_code_and_name_are_trimmed(self):
        add_category("  MUG ", "  Mugs  ")
        category = get_category("MUG")
        self.assertEqual(category.name, "Mugs")

    def test_blank_code_is_rejected(self):
        for blank in ["", "   ", None]:
            with self.assertRaisesMessage(ValidationError, "Category ID is blank, please input again"):
                add_category(blank, "Nothing")

    def test_code_must_have_three_characters(self):
        for code in ["CL", "CLOT"]:
            with self.assertRaisesMessage(ValidationError, "Category ID must be three letter code"):
                add_category(code, "Wrong length")

    def test_duplicate_code_is_rejected(self):
        add_category("CLO", "Clothing")
        with self.assertRaisesMessage(ValidationError, "Category CLO already existed. Please input again"):
            add_category("CLO", "Clothing again")

    def test_lookup_is_case_insensitive_like_legacy(self):
        add_category("STA", "Stationary")
        self.assertIsNotNone(get_category("sta"))

    def test_unknown_category_returns_none(self):
        self.assertIsNone(get_category("XYZ"))


class CategoryDeviationTests(TestCase):

    def test_D_A2a_lower_case_code_is_stored_upper_case_and_reachable(self):
        # legacy probe P3: "bks" was stored as-is and getCategory("bks") returned null
        add_category("bks", "Books")
        self.assertEqual(get_category("bks").code, "BKS")

    def test_D_A2a_lower_case_duplicate_of_existing_code_is_detected(self):
        add_category("CLO", "Clothing")
        with self.assertRaisesMessage(ValidationError, "Category CLO already existed"):
            add_category("clo", "Clothing")

    def test_D_A2b_code_must_be_letters(self):
        # legacy accepted "AB1"; its own message and vendor-file rule say letters only
        with self.assertRaisesMessage(ValidationError, "Category ID must be three letter code"):
            add_category("AB1", "Digits")


class EntityGuardsTheDatabaseTests(TestCase):

    def test_invalid_category_cannot_be_saved_directly(self):
        # every path (forms, legacy import, admin) goes through Category.clean()
        with self.assertRaises(ValidationError):
            Category(code="TOOLONG", name="x").save()
        self.assertEqual(Category.objects.count(), 0)

    def test_direct_save_normalises_code(self):
        Category(code="dia", name="Diary").save()
        self.assertTrue(Category.objects.filter(code="DIA").exists())
