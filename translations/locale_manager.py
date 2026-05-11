"""
LocaleManager — loads translation JSON files and dispatches locale-change
events to any registered observer callbacks.

Usage
-----
from i18n.locale_manager import locale_manager   # singleton

# Get a translated ability name (falls back to English name if missing)
name = locale_manager.ability_name("omen", "Q", fallback="Paranoia")

# Subscribe to locale changes (called with new locale code)
locale_manager.subscribe(my_callback)

# Change locale
locale_manager.set_locale("fr")

# List available locales → [{"code": "en", "language": "English"}, ...]
locales = locale_manager.available_locales()
"""
from __future__ import annotations
import json
from pathlib import Path

# Translations live next to this package's parent directory
_TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"


class LocaleManager:
    def __init__(self):
        self._current_code: str = "fr"
        self._data: dict[str, dict] = {}          # code → full JSON dict
        self._meta_cache: list[dict] | None = None
        self._observers: list[callable] = []

        # Always pre-load English so there's always a fallback
        self._load("fr")

    # ── Locale discovery ──────────────────────────────────────────────────

    def available_locales(self) -> list[dict]:
        """
        Scan the translations directory and return a list of
        {"code": "fr", "language": "Français"} dicts, sorted by language name.
        """
        if self._meta_cache is not None:
            return self._meta_cache

        result = []
        for path in sorted(_TRANSLATIONS_DIR.glob("*.json")):
            try:
                with path.open(encoding="utf-8") as f:
                    data = json.load(f)
                meta = data.get("_meta", {})
                code = meta.get("code", path.stem)
                language = meta.get("language", code.upper())
                result.append({"code": code, "language": language})
            except Exception:
                pass

        self._meta_cache = sorted(result, key=lambda x: x["language"])
        return self._meta_cache

    # ── Loading ───────────────────────────────────────────────────────────

    def _load(self, code: str) -> bool:
        """Load a locale file into the cache. Returns True on success."""
        if code in self._data:
            return True
        path = _TRANSLATIONS_DIR / f"{code}.json"
        if not path.exists():
            return False
        try:
            with path.open(encoding="utf-8") as f:
                self._data[code] = json.load(f)
            return True
        except Exception:
            return False

    # ── Active locale ─────────────────────────────────────────────────────

    @property
    def current_code(self) -> str:
        return self._current_code

    def set_locale(self, code: str) -> bool:
        """
        Switch to *code*. Loads the file if needed.
        Notifies all observers. Returns False if the locale file was not found.
        """
        if code == self._current_code:
            return True
        if not self._load(code):
            return False
        self._current_code = code
        self._notify()
        return True

    # ── Translation API ───────────────────────────────────────────────────

    def ability_name(self, agent_id: str, ability_key: str,
                     fallback: str = "") -> str:
        """
        Return the translated ability name for the current locale.
        Falls back to English, then to *fallback* if still missing.
        """
        name = self._lookup(self._current_code, agent_id, ability_key)
        if name is not None:
            return name
        # Fall back to English
        name = self._lookup("en", agent_id, ability_key)
        return name if name is not None else fallback

    def _lookup(self, code: str, agent_id: str, ability_key: str) -> str | None:
        locale_data = self._data.get(code, {})
        agent_data = locale_data.get(agent_id, {})
        return agent_data.get(ability_key)

    # ── Observer pattern ──────────────────────────────────────────────────

    def subscribe(self, callback: callable):
        """Register *callback* to be called (with no args) on locale change."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback: callable):
        self._observers = [cb for cb in self._observers if cb is not callback]

    def _notify(self):
        for cb in list(self._observers):
            try:
                cb()
            except Exception:
                pass


# ── Module-level singleton ────────────────────────────────────────────────
locale_manager = LocaleManager()