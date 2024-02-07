from django import template

register = template.Library()

@register.filter(name='get_file_extension')
def get_file_extension(value):
    return value.split('.')[-1]