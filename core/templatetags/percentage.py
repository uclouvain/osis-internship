from django import template

register = template.Library()

@register.filter
def percentage(value):
    return "{0:.0f}%".format(value)
