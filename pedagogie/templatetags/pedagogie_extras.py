# pedagogie/templatetags/pedagogie_extras.py
from django import template

register = template.Library()

@register.filter
def dict_lookup(d, key):
    """
    Permet d'accéder à une clé de dictionnaire dans les templates Django.
    Usage : {{ mon_dict|dict_lookup:cle }}
    """
    if isinstance(d, dict):
        return d.get(key, [])
    return []