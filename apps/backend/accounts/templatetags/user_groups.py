from django import template

register = template.Library()


@register.filter
def has_group(user, group_name: str) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter
def starts_with(value: str, prefix: str) -> bool:
    try:
        return str(value).startswith(prefix)
    except Exception:
        return False
