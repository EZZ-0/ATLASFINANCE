"""
Theme Presets for Atlas Financial Intelligence
Easily swap between color schemes without touching main code
"""

THEMES = {
    'blue_corporate': {
        'name': 'Professional Dark (Current)',
        'primary': '#3b82f6',
        'primary_light': '#60a5fa',
        'primary_dark': '#2563eb',
        'secondary': '#10b981',
        'secondary_light': '#34d399',
        'background': '#0f1419',
        'surface': 'rgba(59, 130, 246, 0.12)',
        'text': '#f0f4f8',
        'text_secondary': '#94a3b8',
        'gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    },
    
    'emerald_gold': {
        'name': 'Emerald & Gold',
        'primary': '#10b981',
        'primary_light': '#34d399',
        'primary_dark': '#047857',
        'secondary': '#f59e0b',
        'secondary_light': '#fbbf24',
        'background': '#0a1f1a',
        'surface': 'rgba(16, 185, 129, 0.15)',
        'text': '#ffffff',
        'text_secondary': '#d1fae5',
        'gradient': 'linear-gradient(135deg, #10b981 0%, #f59e0b 100%)',
    },
    
    'purple_rose': {
        'name': 'Purple & Rose Gold',
        'primary': '#8b5cf6',
        'primary_light': '#a78bfa',
        'primary_dark': '#6d28d9',
        'secondary': '#f43f5e',
        'secondary_light': '#fb7185',
        'background': '#1a0a2e',
        'surface': 'rgba(139, 92, 246, 0.15)',
        'text': '#ffffff',
        'text_secondary': '#f3e8ff',
        'gradient': 'linear-gradient(135deg, #8b5cf6 0%, #f43f5e 100%)',
    },
    
    'slate_cyan': {
        'name': 'Slate & Cyan',
        'primary': '#0ea5e9',
        'primary_light': '#38bdf8',
        'primary_dark': '#0284c7',
        'secondary': '#06b6d4',
        'secondary_light': '#22d3ee',
        'background': '#0f172a',
        'surface': 'rgba(14, 165, 233, 0.15)',
        'text': '#ffffff',
        'text_secondary': '#e0f2fe',
        'gradient': 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
    },
    
    'dark_burgundy': {
        'name': 'Dark Burgundy & Copper',
        'primary': '#991b1b',
        'primary_light': '#dc2626',
        'primary_dark': '#7f1d1d',
        'secondary': '#b45309',
        'secondary_light': '#d97706',
        'background': '#1a0a0a',
        'surface': 'rgba(153, 27, 27, 0.15)',
        'text': '#ffffff',
        'text_secondary': '#fef2f2',
        'gradient': 'linear-gradient(135deg, #991b1b 0%, #b45309 100%)',
    }
}

def get_theme(theme_name='blue_corporate'):
    """Get theme colors by name"""
    return THEMES.get(theme_name, THEMES['blue_corporate'])

def get_theme_names():
    """Get list of available theme names"""
    return {name: data['name'] for name, data in THEMES.items()}


