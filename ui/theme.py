"""
Visual theme constants for the Valorant Caster app.
All colours and font settings live here so tweaking is trivial.
"""

# ── Palette ───────────────────────────────────────────────────────────────
BG_DARK        = "#0f1116"   # main window background
BG_PANEL       = "#161b22"   # column / card backgrounds
BG_CARD        = "#1c2230"   # individual agent card
BG_INPUT       = "#1a1f2e"   # text input background
BG_OVERLAY     = "#0d1117"   # picker overlay background
BG_HOVER       = "#252d3d"   # hover state

ACCENT_RED     = "#ff4655"   # Valorant red
ACCENT_RED_DIM = "#7a2030"   # muted red (bookmark inactive)
ACCENT_GOLD    = "#c8a84b"   # ultimate highlight
ACCENT_BLUE    = "#3a86c8"   # initiator role colour (unused – here for future)

TEXT_PRIMARY   = "#eaeaea"
TEXT_SECONDARY = "#7a8599"
TEXT_DISABLED  = "#3d4455"

ROLE_COLORS = {
    "Duelist":    "#ff4655",
    "Controller": "#7c4dff",
    "Initiator":  "#3a86c8",
    "Sentinel":   "#2ec4b6",
}

# ── Typography ────────────────────────────────────────────────────────────
FONT_FAMILY    = "Segoe UI"     # Falls back gracefully on Linux/Mac
FONT_TITLE     = (FONT_FAMILY, 11, "bold")
FONT_BODY      = (FONT_FAMILY, 9)
FONT_SMALL     = (FONT_FAMILY, 8)
FONT_ABILITY   = (FONT_FAMILY, 8, "bold")
FONT_ULTIMATE  = (FONT_FAMILY, 8, "bold")

# ── Layout ────────────────────────────────────────────────────────────────
WINDOW_MIN_W   = 900
WINDOW_MIN_H   = 680
CARD_WIDTH     = 300          # min agent card width (resizable)
CARD_HEIGHT    = 155
PICKER_WIDTH   = 340
AGENT_THUMB    = 52           # agent portrait size in card
ABILITY_ICON   = 22           # ability icon size in card
PICKER_ICON    = 36           # agent icon size in picker list
BOOKMARK_W     = 22
BOOKMARK_H     = 38