"""Member use cases (business layer)."""
from django.core.exceptions import ValidationError

from members.models import Member


def add_member(member_id: str, name: str) -> Member:
    """Register a new member (BR-03): non-blank, unique ID; starts as first purchase."""
    member = Member(member_id=member_id, name=name)
    member.clean()
    if Member.objects.filter(member_id=member.member_id).exists():
        raise ValidationError(
            f"Member ID {member.member_id} already existed. Please input again")
    member.save()
    return member


def get_member(member_id: str) -> Member | None:
    return Member.objects.filter(member_id=(member_id or "").strip()).first()
