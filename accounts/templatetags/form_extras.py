from django import template

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name: str):
    try:
        return user.is_authenticated and user.groups.filter(name__iexact=group_name).exists()
    except Exception:
        return False


@register.filter(name="add_class")
def add_class(field, css: str):
    # Add classes preserving existing ones
    existing = field.field.widget.attrs.get("class", "")
    new_classes = (existing + " " + str(css)).strip()
    return field.as_widget(attrs={**field.field.widget.attrs, "class": new_classes})


@register.filter(name="add_attr")
def add_attr(field, arg: str):
    # Set/update an attribute using "name:value"
    try:
        key, value = str(arg).split(":", 1)
    except ValueError:
        return field
    return field.as_widget(attrs={**field.field.widget.attrs, key: value})
