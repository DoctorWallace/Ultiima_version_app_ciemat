from django import template

register = template.Library()

@register.filter
def add_class(field, css):
    # Añade clases sin machacar las existentes
    attrs = field.field.widget.attrs.copy()
    current = attrs.get("class", "")
    attrs["class"] = (current + " " + css).strip()
    return field.as_widget(attrs=attrs)




@register.filter
def has_group(user, group_name: str):
    return user.is_authenticated and user.groups.filter(name__iexact=group_name).exists()
