from django.template.loader import render_to_string
from django.urls import ResolverMatch

from tree_menu.models import MenuItem


class MenuNode(object):

    def __init__(self, id, title, url, named_url):
        self.id = id
        self.title = title
        self.url = url
        self.named_url = named_url
        self.is_active = False
        self.is_ancestor = False
        self.expanded = False
        self.children = []


class MenuBuilder(object):
    """
    Класс, отвечающий за построение дерева меню.
    """

    def __init__(self, menu_name, request):
        self.menu_name = menu_name
        self.request = request
        self.items = []
        self.id_map = {}
        self.children_map = {}
        self.active_item = None
        self.ancestor_ids = set()

    # ----------------------------------
    def build(self):
        self._load_items()
        if not self.items:
            return []

        self._resolve_active_item()
        self._collect_ancestors()

        tree = self._build_tree(None)
        self._mark_expanded(tree)
        return tree

    # ---------------------------------
    def _load_items(self):
        qs = (
            MenuItem.objects
            .filter(menu__name=self.menu_name)
            .select_related("parent")
            .order_by("order", "id")
        )

        self.items = list(qs)
        self.id_map = {item.id: item for item in self.items}

        for item in self.items:
            parent_id = item.parent_id
            if parent_id not in self.children_map:
                self.children_map[parent_id] = []
            self.children_map[parent_id].append(item)

    def _resolve_active_item(self):
        path = self.request.path

        try:
            match = self.request.resolver_match
            resolved_name = match.view_name if match else None
        except Exception:
            resolved_name = None

        # 1. Совпадение по named_url
        for item in self.items:
            if item.named_url and resolved_name == item.named_url:
                self.active_item = item
                return

        # 2. Совпадение по URL
        for item in self.items:
            try:
                url = item.resolved_url()
            except Exception:
                url = item.url or ""

            if url == path:
                self.active_item = item
                return

    def _collect_ancestors(self):
        if not self.active_item:
            return

        current = self.active_item
        while current and current.parent_id:
            self.ancestor_ids.add(current.parent_id)
            current = self.id_map.get(current.parent_id)

    def _build_tree(self, parent_id):
        result = []

        children = sorted(
            self.children_map.get(parent_id, []),
            key=lambda x: (x.order, x.id)
        )

        for item in children:
            try:
                url = item.resolved_url()
            except Exception:
                url = item.url or ""

            node = MenuNode(
                id=item.id,
                title=item.title,
                url=url,
                named_url=item.named_url,
            )

            if self.active_item and item.id == self.active_item.id:
                node.is_active = True

            if item.id in self.ancestor_ids:
                node.is_ancestor = True

            node.children = self._build_tree(item.id)
            result.append(node)

        return result

    def _mark_expanded(self, nodes):
        for node in nodes:
            if node.is_active or node.is_ancestor:
                node.expanded = True
            self._mark_expanded(node.children)
