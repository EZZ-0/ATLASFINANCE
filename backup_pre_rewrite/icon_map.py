"""
Icon Replacement Script
Replace all emojis with Bootstrap Icons class names
"""

# Emoji to Bootstrap Icon mapping
ICON_MAP = {
    # Tab icons
    "📊": "bar-chart-line",
    "💰": "cash-coin",
    "📈": "graph-up-arrow",
    "🛡️": "shield-check",
    "👥": "people",
    "📉": "graph-down",
    "🔍": "search",
    "🧮": "calculator",
    
    # Status indicators
    "🟢": "circle-fill text-success",
    "🟩": "check-circle text-success",
    "⬜": "dash-circle text-secondary",
    "🟥": "x-circle text-danger",
    "🔴": "circle-fill text-danger",
    "🟡": "circle-fill text-warning",
    "⚪": "circle text-secondary",
    
    # Action/Status symbols
    "✅": "check-circle-fill text-success",
    "✓": "check text-success",
    "✗": "x text-danger",
    "❌": "x-circle text-danger",
    "⚠️": "exclamation-triangle",
    "ℹ️": "info-circle",
    "💡": "lightbulb",
    
    # Misc
    "🔥": "fire",
    "⚡": "lightning-charge",
    "🔄": "arrow-repeat",
    "⭐": "star-fill",
    "📍": "geo-alt",
    "📌": "pin",
    "🏦": "building",
    "🎯": "bullseye",
    
    # Arrows
    "➡️": "arrow-right",
    "⬆️": "arrow-up",
    "⬇️": "arrow-down",
}

def get_icon_html(emoji, size="1.2em"):
    """Convert emoji to Bootstrap icon HTML"""
    icon_class = ICON_MAP.get(emoji, "circle")
    return f'<i class="bi bi-{icon_class}" style="font-size: {size};"></i>'

# Test
if __name__ == "__main__":
    print("Icon Mapping Test:")
    for emoji, icon_class in ICON_MAP.items():
        print(f"{emoji} → bi-{icon_class}")




