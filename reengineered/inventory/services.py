"""Category use cases (business layer).

Format rules live in the Category entity (refactoring A2); the service keeps
only the rule that needs the whole table: uniqueness.
Data access goes through the Django ORM here; Member B's repository layer
(refactoring B1) will replace the direct ``Category.objects`` calls.
"""
from django.core.exceptions import ValidationError

from inventory.models import Category


def add_category(code: str, name: str) -> Category:
    category = Category(code=code, name=name)
    category.clean()
    if Category.objects.filter(code=category.code).exists():
        raise ValidationError(
            f"Category {category.code} already existed. Please input again")
    category.save()
    return category


def get_category(code: str) -> Category | None:
    """Case-insensitive lookup, as in legacy CategoryManager.getCategory."""
    return Category.objects.filter(code=(code or "").strip().upper()).first()
