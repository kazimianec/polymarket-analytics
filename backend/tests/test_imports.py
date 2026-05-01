"""Smoke tests to verify all app modules are importable.

Catches broken imports early when creating a new project from the template.
"""

import importlib
import pkgutil


def _collect_submodules(package: str) -> list[str]:
    """Recursively collect all submodule names under a package."""
    pkg = importlib.import_module(package)
    modules = [package]
    if hasattr(pkg, "__path__"):
        for info in pkgutil.walk_packages(pkg.__path__, prefix=f"{package}."):
            modules.append(info.name)
    return modules


def test_all_app_modules_importable() -> None:
    """Every module under the app package should import without errors."""
    modules = _collect_submodules("app")
    assert len(modules) > 0, "No modules found under app"

    errors: list[str] = []
    for name in modules:
        try:
            importlib.import_module(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    assert not errors, "Failed to import:\n" + "\n".join(errors)
