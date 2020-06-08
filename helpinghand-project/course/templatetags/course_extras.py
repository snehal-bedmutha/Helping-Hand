from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
  """
    Returns the value turned into a list.
  """
  return value.split(key)

@register.filter(name='getValue')
def getValue(value, args):
    return value[int(args)]