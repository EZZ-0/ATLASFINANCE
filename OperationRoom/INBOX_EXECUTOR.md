# INBOX: EXECUTOR

<!-- 
DATA FILE: Tasks assigned to Executor.
For protocols and task templates, see: OPERATION_ROOM_GUIDE.txt
-->

---

## ⚠️ NEW MODE: PARALLEL MILESTONES

```
╔════════════════════════════════════════════════════════════════════════════╗
║  YOU OWN MILESTONE-006 COMPLETELY                                          ║
║                                                                            ║
║  - You design, implement, and test the entire feature                      ║
║  - No waiting for Architect                                                ║
║  - No research tasks - you do the FULL implementation                      ║
║  - Report completion when done                                             ║
║                                                                            ║
║  Architect is working on MILESTONE-005 in parallel.                        ║
║  We sync when both are done.                                               ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## YOUR MILESTONE: MILESTONE-006 - White-Label/Custom Branding ✅ COMPLETE

| Field | Value |
|-------|-------|
| **Phase** | 3 - Professional Polish |
| **Owner** | EXECUTOR (Full Ownership) |
| **Est. Time** | 4-6 hours |
| **Priority** | P0 - ✅ COMPLETED |
| **Why** | B2B revenue - firms pay for branded tools |
| **Completed** | 2025-12-08 03:25 |

---

### OBJECTIVE

Create a theming system that allows users (or future B2B clients) to customize the look and feel of the ATLAS engine.

---

### DELIVERABLES

1. **Theme Configuration System**
   - Create `config/themes.py` with theme definitions
   - Support light/dark mode toggle
   - Define color variables (primary, secondary, accent, background, text)
   - Font family options

2. **CSS Variable Injection**
   - Create `app_themes.py` module
   - Inject CSS variables based on selected theme
   - Apply to existing UI components

3. **3 Built-in Themes**
   - `atlas_dark` (current default)
   - `atlas_light` (professional light mode)
   - `corporate_blue` (B2B-friendly corporate theme)

4. **Theme Selector UI**
   - Add theme dropdown to sidebar (below ticker search)
   - Persist selection in session state
   - Smooth transition on change

5. **Logo Injection Support** (Optional/Stretch)
   - Placeholder for custom logo upload
   - Config option for logo URL

---

### IMPLEMENTATION GUIDE

#### Step 1: Create Theme Definitions

```python
# config/themes.py (CREATE THIS)

THEMES = {
    'atlas_dark': {
        'name': 'ATLAS Dark',
        'primary': '#1a1a2e',
        'secondary': '#16213e',
        'accent': '#0f3460',
        'highlight': '#e94560',
        'text': '#eaeaea',
        'text_secondary': '#a0a0a0',
        'background': '#0f0f1a',
        'card_bg': 'rgba(26, 26, 46, 0.8)',
        'border': 'rgba(255, 255, 255, 0.1)',
        'success': '#00c853',
        'warning': '#ffc107',
        'danger': '#ff5252',
        'font_family': "'Segoe UI', sans-serif",
    },
    'atlas_light': {
        'name': 'ATLAS Light',
        'primary': '#ffffff',
        'secondary': '#f5f5f5',
        'accent': '#1976d2',
        'highlight': '#d32f2f',
        'text': '#212121',
        'text_secondary': '#757575',
        'background': '#fafafa',
        'card_bg': 'rgba(255, 255, 255, 0.9)',
        'border': 'rgba(0, 0, 0, 0.12)',
        'success': '#4caf50',
        'warning': '#ff9800',
        'danger': '#f44336',
        'font_family': "'Segoe UI', sans-serif",
    },
    'corporate_blue': {
        'name': 'Corporate',
        'primary': '#0d47a1',
        'secondary': '#1565c0',
        'accent': '#42a5f5',
        'highlight': '#ff6f00',
        'text': '#ffffff',
        'text_secondary': '#bbdefb',
        'background': '#0a1929',
        'card_bg': 'rgba(13, 71, 161, 0.7)',
        'border': 'rgba(66, 165, 245, 0.3)',
        'success': '#66bb6a',
        'warning': '#ffa726',
        'danger': '#ef5350',
        'font_family': "'Arial', sans-serif",
    }
}

def get_theme(theme_name: str) -> dict:
    return THEMES.get(theme_name, THEMES['atlas_dark'])
```

#### Step 2: Create Theme Injection Module

```python
# app_themes.py (CREATE THIS)

import streamlit as st
from config.themes import THEMES, get_theme

def inject_theme_css(theme_name: str = 'atlas_dark'):
    """Inject CSS variables for selected theme."""
    theme = get_theme(theme_name)
    
    css = f"""
    <style>
    :root {{
        --primary: {theme['primary']};
        --secondary: {theme['secondary']};
        --accent: {theme['accent']};
        --highlight: {theme['highlight']};
        --text: {theme['text']};
        --text-secondary: {theme['text_secondary']};
        --background: {theme['background']};
        --card-bg: {theme['card_bg']};
        --border: {theme['border']};
        --success: {theme['success']};
        --warning: {theme['warning']};
        --danger: {theme['danger']};
        --font-family: {theme['font_family']};
    }}
    
    .stApp {{
        background-color: var(--background);
        font-family: var(--font-family);
    }}
    
    /* Override Streamlit defaults */
    .stMetric label {{
        color: var(--text-secondary) !important;
    }}
    
    .stMetric [data-testid="stMetricValue"] {{
        color: var(--text) !important;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def render_theme_selector():
    """Render theme selector in sidebar."""
    theme_options = {v['name']: k for k, v in THEMES.items()}
    
    selected_name = st.sidebar.selectbox(
        "Theme",
        options=list(theme_options.keys()),
        index=0,
        key='theme_selector'
    )
    
    selected_key = theme_options[selected_name]
    st.session_state.current_theme = selected_key
    
    return selected_key
```

#### Step 3: Integrate into usa_app.py

Find where CSS is injected (early in the file) and add:

```python
# Near top of app, after page config
from app_themes import inject_theme_css, render_theme_selector

# In sidebar section
theme = render_theme_selector()
inject_theme_css(theme)
```

---

### TESTING CHECKLIST

- [ ] Dark theme displays correctly (current default)
- [ ] Light theme displays correctly (readable, professional)
- [ ] Corporate theme displays correctly
- [ ] Theme persists during session
- [ ] All metric cards readable in all themes
- [ ] Charts/graphs visible in all themes
- [ ] No CSS conflicts with existing styles
- [ ] Flip cards work in all themes

---

### FILES TO CREATE

| File | Purpose |
|------|---------|
| `config/themes.py` | Theme definitions |
| `app_themes.py` | CSS injection + selector |

### FILES TO MODIFY

| File | Change |
|------|--------|
| `usa_app.py` | Import and call theme functions |

---

### REPORTING

When complete, post in `LIVE_CHAT.md`:

```
[EXECUTOR]: [DONE] MILESTONE-006 Complete.
- Created config/themes.py with 3 themes
- Created app_themes.py with CSS injection
- Integrated theme selector in sidebar
- Tested all 3 themes
- Ready for integration
```

---

### NOTES

- **DON'T** wait for Architect - work independently
- **DON'T** modify core financial logic - only styling
- **DO** test thoroughly before reporting done
- **DO** keep existing dark theme as default

---

## COMPLETED TASKS (BATCH 2)

| Task | Status | Notes |
|------|--------|-------|
| E017 | ✅ DONE | Insider module validated |
| E018 | ✅ DONE | Ownership bug found → Architect fixed |
| E019 | ✅ DONE | SEC EDGAR validated |
| E020 | ✅ DONE | 13F research complete |
| E021 | ✅ DONE | pctChange extraction confirmed |

---

<!-- 
END OF INBOX
For protocols: see OPERATION_ROOM_GUIDE.txt
-->
