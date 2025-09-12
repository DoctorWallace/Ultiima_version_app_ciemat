from django import template
register = template.Library()

@register.filter(name="has_group")
def has_group(user, group_name: str):
    try:
        return user.is_authenticated and user.groups.filter(name__iexact=group_name).exists()
    except Exception:
        return False

@register.filter
def add_class(field, css):
    return field.as_widget(attrs={"class": css})
