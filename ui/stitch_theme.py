"""Stitch Pastel Theme CSS for MovieGraph AI.

Implements the exact design tokens generated in Stitch:
- Canvas: Warm Ivory (#FAF8F5)
- Text: Soft Charcoal (#2D3142)
- Secondary Accent: Dusty Lavender (#B4A7D6)
- Tertiary Accent: Muted Sage (#A3B899)
- Highlights: Soft Peach (#F7D1BA), Powder Blue (#B8D8E8), Pale Blush (#F3D1DC)
- Fully rounded pills (border-radius: 9999px) and soft cards (20px)
- Soft pastel diffused shadows
"""


def get_stitch_css() -> str:
    """Returns the comprehensive CSS stylesheet for Streamlit."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Root Tokens */
    :root {
        --color-bg: #FAF8F5;
        --color-surface: #FFFFFF;
        --color-surface-dim: #F2EFE9;
        --color-text: #2D3142;
        --color-text-muted: #6E7282;
        --color-lavender: #B4A7D6;
        --color-lavender-dark: #53457A;
        --color-lavender-light: #EFEAF7;
        --color-sage: #A3B899;
        --color-sage-light: #EBF2E8;
        --color-peach: #F7D1BA;
        --color-peach-light: #FDF3ED;
        --color-powder-blue: #B8D8E8;
        --color-powder-blue-light: #EEF7FC;
        --color-blush: #F3D1DC;
        --color-border: #E8E5DF;
        --radius-pill: 9999px;
        --radius-card: 20px;
        --radius-sm: 10px;
        --shadow-pastel: 0 12px 32px -8px rgba(180, 167, 214, 0.18);
        --shadow-subtle: 0 4px 16px 0 rgba(45, 49, 66, 0.04);
    }

    /* Streamlit Global Container Override */
    .stApp {
        background-color: var(--color-bg) !important;
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
    }

    /* Hide standard Streamlit header bar completely to eliminate top clipping */
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    .stAppHeader {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Main view container spacing */
    .main .block-container,
    div.block-container {
        max-width: 1200px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Universal Text & Heading Contrast Overrides */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] strong,
    div[data-testid="stMarkdownContainer"] em,
    div[data-testid="stMarkdownContainer"] li {
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
    }

    /* Widget Labels */
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span,
    label[data-baseweb="label"] {
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        margin-bottom: 6px !important;
    }

    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F1EDE4 !important;
        padding: 6px !important;
        border-radius: var(--radius-pill) !important;
        gap: 8px !important;
        border: 1px solid var(--color-border) !important;
        margin-bottom: 2rem !important;
        display: flex !important;
        justify-content: center !important;
        position: relative !important;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"],
    .stTabs div[role="tablist"] > div[style*="background-color"],
    .stTabs div[role="tablist"] > div:last-child {
        display: none !important;
        background-color: transparent !important;
        height: 0 !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: var(--radius-pill) !important;
        color: var(--color-text-muted) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 24px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-text) !important;
        background-color: rgba(255, 255, 255, 0.65) !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--color-surface) !important;
        color: var(--color-lavender-dark) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(45, 49, 66, 0.08) !important;
        border: 1px solid rgba(180, 167, 214, 0.3) !important;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        background-color: var(--color-surface) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-pill) !important;
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: 1.05rem !important;
        padding: 14px 24px !important;
        box-shadow: var(--shadow-pastel) !important;
        transition: all 0.25s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--color-lavender) !important;
        box-shadow: 0 0 0 4px rgba(180, 167, 214, 0.25) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #A0A5B5 !important;
    }

    /* Selectbox Input Styling */
    div[data-baseweb="select"] {
        border-radius: var(--radius-pill) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: var(--color-surface) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-pill) !important;
        min-height: 48px !important;
        box-shadow: var(--shadow-subtle) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--color-lavender) !important;
    }

    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
    }

    div[data-baseweb="select"] svg {
        fill: var(--color-text) !important;
        color: var(--color-text) !important;
    }

    /* BaseWeb Dropdown Popover & Menu Items (Light Pastel Card) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: 18px !important;
        box-shadow: 0 16px 40px -8px rgba(45, 49, 66, 0.15) !important;
        overflow: hidden !important;
    }

    ul[data-baseweb="menu"],
    div[data-baseweb="menu"],
    div[role="listbox"] {
        background-color: #FFFFFF !important;
        color: var(--color-text) !important;
        padding: 8px !important;
        border-radius: 18px !important;
    }

    li[data-baseweb="menu-item"],
    li[role="option"],
    div[role="option"] {
        background-color: transparent !important;
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        transition: background 0.15s ease, color 0.15s ease !important;
    }

    li[data-baseweb="menu-item"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"],
    li[data-highlighted="true"] {
        background-color: var(--color-lavender-light) !important;
        color: var(--color-lavender-dark) !important;
        font-weight: 700 !important;
    }

    /* Slider Styling */
    div[data-testid="stSlider"] div[data-baseweb="slider"] {
        padding: 8px 0 !important;
    }

    /* Slider track background */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        background: #E8E5DF !important;
    }

    /* Slider active progress bar */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div {
        background: var(--color-lavender) !important;
    }

    /* Slider Thumb */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: #FFFFFF !important;
        border: 3px solid var(--color-lavender) !important;
        box-shadow: 0 2px 8px rgba(180, 167, 214, 0.5) !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Slider tick values */
    div[data-testid="stSlider"] div {
        color: var(--color-text-muted) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
    }

    /* Slider current value text */
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--color-lavender-dark) !important;
        font-weight: 700 !important;
    }

    /* Primary Action Buttons (Ask AI & Generate Recommendations) */
    div[data-testid="stFormSubmitButton"] button,
    .stFormSubmitButton > button,
    button[data-testid="stBaseButton-primary"],
    button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"] {
        background-color: var(--color-lavender) !important;
        color: #2D3142 !important;
        border-radius: var(--radius-pill) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 12px 28px !important;
        border: 1px solid rgba(180, 167, 214, 0.6) !important;
        box-shadow: 0 4px 14px rgba(180, 167, 214, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover,
    .stFormSubmitButton > button:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #A493D1 !important;
        color: #1F222E !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(180, 167, 214, 0.45) !important;
    }

    /* Secondary Action Buttons & Suggestion Chips */
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"],
    .stButton > button {
        background-color: #FFFFFF !important;
        color: var(--color-text) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-pill) !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        box-shadow: var(--shadow-subtle) !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:hover {
        background-color: var(--color-lavender-light) !important;
        border-color: var(--color-lavender) !important;
        color: var(--color-lavender-dark) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(180, 167, 214, 0.3) !important;
    }

    /* Table styling (Graph Explorer) */
    div[data-testid="stTable"] table {
        background-color: var(--color-surface) !important;
        color: var(--color-text) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--color-border) !important;
        overflow: hidden !important;
    }

    div[data-testid="stTable"] th {
        background-color: var(--color-surface-dim) !important;
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        border-bottom: 1.5px solid var(--color-border) !important;
        padding: 10px 14px !important;
    }

    div[data-testid="stTable"] td {
        color: var(--color-text) !important;
        font-family: 'Manrope', sans-serif !important;
        border-bottom: 1px solid var(--color-border) !important;
        padding: 10px 14px !important;
    }

    /* Expanders Styling */
    div[data-testid="stExpander"] {
        background-color: var(--color-surface) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: var(--shadow-subtle) !important;
        margin-top: 12px !important;
        overflow: hidden !important;
    }

    div[data-testid="stExpander"] summary {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        color: var(--color-text) !important;
        padding: 12px 18px !important;
    }

    div[data-testid="stExpander"] summary:hover {
        color: var(--color-lavender-dark) !important;
    }

    div[data-testid="stExpander"] summary svg {
        fill: var(--color-text) !important;
    }

    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 16px 20px !important;
        border-top: 1px solid var(--color-border) !important;
    }

    /* Code blocks styling */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #272B38 !important;
        color: #E2E8F0 !important;
        border-radius: 8px !important;
    }

    /* Custom Component Cards */
    .stitch-card {
        background: var(--color-surface);
        border-radius: var(--radius-card);
        padding: 24px;
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-pastel);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stitch-card:hover {
        box-shadow: 0 16px 36px -8px rgba(180, 167, 214, 0.25);
    }

    /* Badge Pills */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: var(--radius-pill);
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .badge-lavender {
        background-color: var(--color-lavender-light);
        color: #53457A;
        border: 1px solid rgba(180, 167, 214, 0.5);
    }

    .badge-sage {
        background-color: var(--color-sage-light);
        color: #38522E;
        border: 1px solid rgba(163, 184, 153, 0.5);
    }

    .badge-peach {
        background-color: var(--color-peach-light);
        color: #8C4724;
        border: 1px solid rgba(247, 209, 186, 0.6);
    }

    .badge-blue {
        background-color: var(--color-powder-blue-light);
        color: #245472;
        border: 1px solid rgba(184, 216, 232, 0.6);
    }

    .badge-charcoal {
        background-color: #F1EDE4;
        color: var(--color-text);
        border: 1px solid var(--color-border);
    }

    /* Status Pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        border-radius: var(--radius-pill);
        font-size: 0.85rem;
        font-weight: 600;
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-subtle);
    }

    .status-dot-green {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: #38A169;
        display: inline-block;
        box-shadow: 0 0 10px rgba(56, 161, 105, 0.6);
        animation: pulse-beacon 2s infinite;
    }

    @keyframes pulse-beacon {
        0% { box-shadow: 0 0 0 0 rgba(56, 161, 105, 0.5); }
        70% { box-shadow: 0 0 0 8px rgba(56, 161, 105, 0); }
        100% { box-shadow: 0 0 0 0 rgba(56, 161, 105, 0); }
    }

    .status-dot-orange {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: #ED8936;
        display: inline-block;
        box-shadow: 0 0 8px #ED8936;
    }

    /* Six Degrees Path Chain Styling */
    .path-chain-container {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        padding: 24px;
        background: #FFFFFF;
        border-radius: 20px;
        border: 1.5px solid #E8E5DF;
        box-shadow: var(--shadow-pastel);
        margin: 20px 0;
    }

    .path-step-person {
        background: #F5F2FA;
        border: 1.5px solid #B4A7D6;
        color: #53457A;
        padding: 10px 18px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(83, 69, 122, 0.08);
    }

    .path-step-movie {
        background: #FAF8F5;
        border: 1.5px solid #2D3142;
        color: #2D3142;
        padding: 10px 18px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(45, 49, 66, 0.08);
    }

    .path-arrow {
        color: #B4A7D6;
        font-size: 1.2rem;
        font-weight: 800;
        padding: 0 4px;
    }

    /* Comparison Head-to-Head Cards */
    .compare-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 20px;
    }

    .compare-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 24px;
        border: 1.5px solid #E8E5DF;
        box-shadow: var(--shadow-subtle);
    }

    .compare-score-banner {
        background: linear-gradient(135deg, #F5F2FA 0%, #EBF2E8 100%);
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        margin: 24px 0;
        border: 1.5px solid #B4A7D6;
    }

    /* Network Canvas Box */
    .network-frame {
        background: #FFFFFF;
        border-radius: 22px;
        border: 1.5px solid #E8E5DF;
        box-shadow: var(--shadow-pastel);
        overflow: hidden;
        margin-top: 16px;
    }

    /* Prompt Library Chips */
    .prompt-chip {
        display: inline-block;
        background: #FFFFFF;
        border: 1.5px solid #E8E5DF;
        border-radius: 9999px;
        padding: 8px 16px;
        font-size: 0.85rem;
        color: #2D3142;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 4px;
    }
    .prompt-chip:hover {
        border-color: #B4A7D6;
        background: #FAF8F5;
        transform: translateY(-2px);
    }
    </style>
    """
