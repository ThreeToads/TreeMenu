from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from tree_menu.menu_builder.MenuBuilder import MenuBuilder

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Рендер меню по названию.
    """
    request = context["request"]

    builder = MenuBuilder(menu_name, request)
    tree = builder.build()

    html = render_to_string("tree_menu/menu.html", {
        "tree": tree,
        "menu_name": menu_name,
        "request": request,
    })

    return mark_safe(html)
