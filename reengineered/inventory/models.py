import re

from django.core.exceptions import ValidationError
from django.db import models

CATEGORY_CODE = re.compile(r"^[A-Z]{3}$")


class Category(models.Model):
    """Product category identified by a three-letter code (e.g. CLO, MUG).

    Refactoring A2 (Remove Setting Method + move validation into the entity):
    legacy Category was built half-empty (id = null, requestedId = input) and
    CategoryManager validated it in two different ways before calling setId()
    (CategoryManager.java:36-47 vs 62-77). Lookups upper-cased the code but
    storage did not, so a lower-case code could never be found again (L-04).
    Here the code is normalised and validated by the entity itself, and every
    save goes through that check.
    """

    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def clean(self):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        if not self.code:
            raise ValidationError("Category ID is blank, please input again")
        if not CATEGORY_CODE.match(self.code):
            raise ValidationError("Category ID must be three letter code")

    def save(self, *args, **kwargs):
        self.clean()  # an invalid category can never reach the database
        super().save(*args, **kwargs)
