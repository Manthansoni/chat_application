# myapp/templatetags/form_tags.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    attributes = []
    for attr in css_class.split(','):
        attributes.append(attr)
    return field.as_widget(attrs={"class": attributes[0], "placeholder": attributes[1]})
