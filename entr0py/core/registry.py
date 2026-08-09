"""
entr0py.core.registry
~~~~~~~~~~~~~~~~~~~~~
Central module registry.  All Module subclasses register here at import time.
The modules/__init__.py imports every category package which triggers
registration via the @register decorator.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entr0py.core.base import Category, Module


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, "Module"] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, module: "Module") -> None:
        slug = module.meta.slug
        if slug in self._modules:
            raise ValueError(f"Duplicate module slug: {slug!r}")
        self._modules[slug] = module

    def register_all(self, modules: list["Module"]) -> None:
        for m in modules:
            self.register(m)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def get(self, slug: str) -> "Module | None":
        return self._modules.get(slug)

    def all(self) -> list["Module"]:
        return list(self._modules.values())

    def by_category(self, cat: "Category") -> list["Module"]:
        return [m for m in self._modules.values() if m.meta.category == cat]

    def search(self, query: str) -> list["Module"]:
        q = query.lower()
        return [
            m for m in self._modules.values()
            if q in m.meta.name.lower()
            or q in m.meta.description.lower()
            or any(q in tag for tag in m.meta.tags)
        ]

    def installed(self) -> list["Module"]:
        return [m for m in self._modules.values() if m.is_installed()]

    def not_installed(self) -> list["Module"]:
        return [m for m in self._modules.values() if not m.is_installed()]

    def __len__(self) -> int:
        return len(self._modules)

    def __contains__(self, slug: str) -> bool:
        return slug in self._modules


# Process-wide singleton
_registry = ModuleRegistry()


def get_registry() -> ModuleRegistry:
    return _registry


def register(module: "Module") -> None:
    _registry.register(module)
