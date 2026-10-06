APP_CSS = """
<style>
:root {
    --halo-bg: #07110e;
    --halo-panel: #101b16;
    --halo-panel-raised: #15221c;
    --halo-border: #293a31;
    --halo-border-soft: rgba(142, 174, 151, 0.16);
    --halo-green: #b5e879;
    --halo-green-dim: #78965d;
    --halo-cyan: #86d9c2;
    --halo-text: #edf3ee;
    --halo-muted: #9baa9f;
    --halo-faint: #718078;
}

/* ---- App shell ---- */
.stApp {
    background-color: var(--halo-bg);
    background-image:
        linear-gradient(rgba(131, 167, 143, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(131, 167, 143, 0.025) 1px, transparent 1px),
        linear-gradient(115deg, #07110e 0%, #0a1511 54%, #0d1813 100%);
    background-size: 44px 44px, 44px 44px, cover;
    color: var(--halo-text);
}

/* ---- Streamlit chrome ----
   Hide dev chrome, but never hide an ancestor of the sidebar
   expand button or the sidebar cannot be reopened. */
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="InputInstructions"],
[data-testid="stMainMenu"] { display: none !important; }

/* The sidebar expand button lives inside the toolbar, so keep the toolbar rendered. */
[data-testid="stToolbar"] {
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
    right: auto !important;
}

/* Keep the header collapsed but clickable so the sidebar expand control stays reachable. */
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    box-shadow: none !important;
    pointer-events: none !important;
}
/* The header is zero-height, so the expand button needs its own size and placement. */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] button {
    position: fixed !important;
    top: 0.7rem !important;
    left: 0.7rem !important;
    width: 2.3rem !important;
    height: 2.3rem !important;
    min-width: 2.3rem !important;
    min-height: 2.3rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 1000 !important;
    background: rgba(16, 27, 22, 0.94) !important;
    border: 1px solid var(--halo-border-soft) !important;
    border-radius: 8px !important;
    color: var(--halo-text) !important;
}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: rgba(24, 40, 32, 0.98) !important;
    border-color: var(--halo-green) !important;
}
[data-testid="stExpandSidebarButton"] span,
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
    display: block !important;
    width: auto !important;
    height: auto !important;
    font-size: 1.2rem !important;
    line-height: 1 !important;
    pointer-events: none !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background: rgba(16, 27, 22, 0.94) !important;
    border: 1px solid var(--halo-border-soft) !important;
    border-radius: 8px !important;
    color: var(--halo-text) !important;
}
[data-testid="stSidebarCollapseButton"] {
    opacity: 1 !important;
    visibility: visible !important;
}
/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #09130f;
    border-right: 1px solid var(--halo-border-soft);
    min-width: 250px;
    max-width: 250px;
    transition: margin-left 220ms ease;
}
/* Streamlit slides the sidebar with transform, which leaves its 250px flex
   footprint behind; the negative margin reclaims that space for the content. */
[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: -250px !important;
    border-right: 0;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 0.82rem; margin: 0; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] .stCaption p { font-size: 0.68rem !important; letter-spacing: 0.04em; line-height: 1.5; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] p { font-size: 0.85rem; }

/* ---- Layout and base typography ---- */
[data-testid="stMain"] { transition: width 220ms ease; }
.block-container {
    max-width: 1540px;
    padding-top: 3.2rem;
    padding-bottom: 4rem;
    margin-left: auto;
    margin-right: auto;
    transition: max-width 220ms ease, padding 220ms ease;
}

html, body, [class*="css"] {
    font-family: Bahnschrift, "Aptos", "Segoe UI", sans-serif;
    letter-spacing: 0;
}

h1, h2, h3 { color: var(--halo-text); letter-spacing: 0; }
h1 { font-size: 2.35rem; font-weight: 680; line-height: 1.1; margin-bottom: 0.4rem; }
h2 { font-size: 1.35rem; font-weight: 650; line-height: 1.2; }
h3 { font-size: 1.02rem; font-weight: 650; line-height: 1.25; }
p, label, .stMarkdown { color: var(--halo-text); }

/* ---- Page header and status ---- */
.halo-page-header { margin: 0; }
.halo-page-title {
    color: var(--halo-text);
    font-size: 2.15rem;
    font-weight: 680;
    line-height: 1.12;
    margin: 0.1rem 0 0;
}
.halo-page-description {
    color: var(--halo-muted);
    font-size: 0.92rem;
    line-height: 1.45;
    margin: 0.5rem 0 0;
}
.halo-section-title {
    color: var(--halo-text);
    font-size: 1.02rem;
    font-weight: 650;
    margin: 1.6rem 0 0.7rem;
}

/* ---- Brand ---- */
.halo-brand {
    color: var(--halo-text);
    font-size: 1.7rem;
    font-weight: 750;
    line-height: 1;
    letter-spacing: 0.04em;
}
.halo-brand-mark {
    width: 10px;
    height: 10px;
    display: inline-block;
    margin-right: 0.55rem;
    background: var(--halo-green);
    box-shadow: 0 0 14px rgba(181, 232, 121, 0.42);
    transform: rotate(45deg);
}
.halo-brand-sub {
    color: var(--halo-faint);
    font-size: 0.69rem;
    margin-top: 0.55rem;
    text-transform: uppercase;
}
.halo-eyebrow {
    color: var(--halo-cyan);
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    margin: 0 0 0.45rem 0;
}
.halo-faint { color: var(--halo-faint); font-size: 0.75rem; }
.halo-date { text-align: right; margin-top: 0.55rem; }
.halo-divider { border-top: 1px solid var(--halo-border-soft); margin: 1rem 0; }
.halo-system-status {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.42rem;
    color: var(--halo-green);
    font: 0.64rem "Consolas", monospace;
    letter-spacing: 0.08em;
}
.halo-system-pulse {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--halo-green);
    box-shadow: 0 0 0 0 rgba(181, 232, 121, 0.55);
    animation: halo-pulse 2.2s ease-out infinite;
}

/* ---- Cards ----
   Cards are st.container(border=True, key=...) blocks, which
   Streamlit exposes as .st-key-<key>. */
[class*="st-key-halocard"], [class*="st-key-halocompact"], .st-key-halo_assistant {
    background: linear-gradient(145deg, rgba(20, 32, 26, 0.97), rgba(13, 23, 18, 0.98));
    border: 1px solid var(--halo-border) !important;
    border-radius: 8px !important;
    padding: 1.25rem 1.3rem 1.3rem !important;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.13);
}
/* Only the dashboard grid needs a height floor; st.columns wraps those in a
   horizontal block, while full-width cards on other pages size to content. */
[data-testid="stHorizontalBlock"] [class*="st-key-halocard"] { min-height: 340px; }
[class*="st-key-halocompact"] { min-height: 0; }
/* Streamlit spaces every element apart; rows carry their own rhythm. */
[class*="st-key-halocard"], [class*="st-key-halocompact"] { gap: 0 !important; }
.st-key-halo_assistant [data-testid="stVerticalBlock"] { gap: 0.5rem; }

.halo-panel-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
    padding-bottom: 0.85rem;
    border-bottom: 1px solid var(--halo-border-soft);
    margin-bottom: 0.2rem;
}
.halo-panel-title { font-size: 1.02rem; font-weight: 650; color: var(--halo-text); margin: 0; line-height: 1.3; }
.halo-panel-subtitle { color: var(--halo-faint); font-size: 0.75rem; margin: 0.3rem 0 0; line-height: 1.35; }
.halo-panel-index { color: var(--halo-green-dim); font: 0.7rem "Consolas", monospace; flex-shrink: 0; }

/* ---- Metrics ---- */
.halo-metric {
    border: 1px solid var(--halo-border);
    border-left: 2px solid var(--halo-green-dim);
    background: rgba(16, 27, 22, 0.92);
    border-radius: 6px;
    padding: 1.05rem 1.1rem;
    min-height: 104px;
}
.halo-metric-label { color: var(--halo-muted); font-size: 0.73rem; text-transform: uppercase; }
.halo-metric-value { color: var(--halo-text); font-size: 1.85rem; font-weight: 680; margin-top: 0.32rem; }
.halo-metric-note { color: var(--halo-faint); font-size: 0.72rem; margin-top: 0.1rem; }

/* ---- Rows and tags ---- */
.halo-row {
    display: grid;
    grid-template-columns: 30px minmax(0, 1fr) auto;
    gap: 0.7rem;
    align-items: start;
    padding: 0.8rem 0;
    border-bottom: 1px solid rgba(142, 174, 151, 0.1);
}
/* Each row is its own Streamlit block, so :last-child cannot find the final row. */
[class*="st-key-halocard"] [data-testid="stElementContainer"]:last-child .halo-row { border-bottom: 0; }
.halo-row-number { color: var(--halo-green); font: 0.74rem "Consolas", monospace; padding-top: 0.1rem; }
.halo-row-title { color: var(--halo-text); font-size: 0.9rem; line-height: 1.4; }
.halo-row-meta { color: var(--halo-muted); font-size: 0.74rem; margin-top: 0.25rem; line-height: 1.4; }
.halo-tag {
    color: var(--halo-cyan);
    border: 1px solid rgba(134, 217, 194, 0.24);
    background: rgba(134, 217, 194, 0.06);
    border-radius: 4px;
    padding: 0.18rem 0.38rem;
    font-size: 0.64rem;
    white-space: nowrap;
    text-transform: uppercase;
}
.halo-empty { color: var(--halo-faint); font-size: 0.84rem; padding: 0.5rem 0; }
.halo-callout {
    border-left: 2px solid var(--halo-green);
    background: rgba(181, 232, 121, 0.055);
    padding: 1rem 1.05rem;
    color: var(--halo-text);
    line-height: 1.45;
    font-size: 0.86rem;
}
/* ---- Loading indicator ---- */
.halo-loading {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    border: 1px solid rgba(134, 217, 194, 0.25);
    background: linear-gradient(100deg, rgba(134, 217, 194, 0.08), rgba(181, 232, 121, 0.05));
    border-radius: 6px;
    padding: 0.8rem 0.9rem;
    margin: 0.7rem 0;
    color: var(--halo-text);
    animation: halo-activity 1.8s ease-in-out infinite alternate;
}
.halo-loading strong { display: block; font-size: 0.82rem; font-weight: 650; }
.halo-loading small { display: block; color: var(--halo-muted); font-size: 0.7rem; margin-top: 0.16rem; }
.halo-loading-copy { display: flex; flex-direction: column; gap: 0.12rem; min-width: 0; }
.halo-loading-orbit {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(134, 217, 194, 0.25);
    border-top-color: var(--halo-green);
    border-right-color: var(--halo-cyan);
    border-radius: 50%;
    animation: halo-spin 900ms linear infinite;
}
.halo-loading-bars { display: flex; gap: 3px; margin-left: auto; align-items: end; height: 18px; }
.halo-loading-bars i { display: block; width: 3px; height: 7px; background: var(--halo-green); animation: halo-bars 900ms ease-in-out infinite; }
.halo-loading-bars i:nth-child(2) { animation-delay: 120ms; }
.halo-loading-bars i:nth-child(3) { animation-delay: 240ms; }

/* ---- Animations ---- */
@keyframes halo-spin { to { transform: rotate(360deg); } }
@keyframes halo-pulse { 0% { box-shadow: 0 0 0 0 rgba(181, 232, 121, 0.5); } 70% { box-shadow: 0 0 0 7px rgba(181, 232, 121, 0); } 100% { box-shadow: 0 0 0 0 rgba(181, 232, 121, 0); } }
@keyframes halo-bars { 0%, 100% { height: 7px; opacity: 0.4; } 50% { height: 17px; opacity: 1; } }
@keyframes halo-activity { from { border-color: rgba(134, 217, 194, 0.22); } to { border-color: rgba(181, 232, 121, 0.48); } }
.halo-sample-banner {
    display: inline-flex;
    gap: 0.5rem;
    align-items: center;
    border: 1px solid rgba(134, 217, 194, 0.22);
    background: rgba(134, 217, 194, 0.055);
    color: var(--halo-cyan);
    border-radius: 4px;
    padding: 0.35rem 0.58rem;
    font: 0.66rem "Consolas", monospace;
    text-transform: uppercase;
}
.halo-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--halo-green); }

/* ---- Assistant panel ---- */
.st-key-halo_assistant {
    padding: 1.3rem 1.3rem 1.4rem !important;
    background: linear-gradient(160deg, rgba(17, 31, 25, 0.99), rgba(9, 19, 15, 0.99));
    border-color: rgba(134, 217, 194, 0.24) !important;
}
.halo-assistant-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    padding-bottom: 1.2rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--halo-border-soft);
}
.halo-assistant-title {
    color: var(--halo-text);
    font-size: 1.12rem;
    font-weight: 660;
    line-height: 1.25;
    margin: 0.16rem 0 0;
}
.halo-assistant-subtitle {
    color: var(--halo-muted);
    font-size: 0.78rem;
    line-height: 1.4;
    margin: 0.34rem 0 0;
}
.halo-assistant-head p:not(.halo-eyebrow) { margin: 0.38rem 0 0; color: var(--halo-muted); font-size: 0.78rem; line-height: 1.4; }
.halo-ready {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    color: var(--halo-green);
    font: 0.62rem "Consolas", monospace;
    letter-spacing: 0.06em;
}
.halo-ready i { width: 6px; height: 6px; border-radius: 50%; background: var(--halo-green); box-shadow: 0 0 9px rgba(181, 232, 121, 0.5); }
.halo-field-label { margin: 0 0 0.55rem; color: var(--halo-faint); font: 0.64rem "Consolas", monospace; }
.halo-question-label { margin-top: 1rem; }
.halo-assistant-divider { height: 1px; background: var(--halo-border-soft); margin: 1.1rem 0; }
.halo-assistant-empty { color: var(--halo-faint); font-size: 0.8rem; line-height: 1.45; margin: 0; }

/* ---- Response cards ---- */
.halo-response {
    border: 1px solid var(--halo-border-soft);
    background: rgba(7, 17, 14, 0.58);
    border-radius: 6px;
    padding: 0.9rem 0.95rem;
    margin-bottom: 0.7rem;
}
.halo-response-head { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.62rem; }
.halo-response-head span {
    color: var(--halo-green);
    font: 0.6rem "Consolas", monospace;
    border: 1px solid rgba(181, 232, 121, 0.2);
    border-radius: 3px;
    padding: 0.12rem 0.3rem;
}
.halo-response-head strong { color: var(--halo-muted); font-size: 0.7rem; font-weight: 600; }
.halo-response-body { color: var(--halo-text); font-size: 0.82rem; line-height: 1.55; overflow-wrap: anywhere; }

.st-key-halo_assistant .stButton > button {
    background: rgba(134, 217, 194, 0.045);
    border-color: rgba(134, 217, 194, 0.18);
    color: var(--halo-text);
    font-size: 0.78rem;
    font-weight: 520;
    min-height: 2.45rem;
}
.st-key-halo_assistant button[kind="tertiary"],
.st-key-halo_assistant button[kind="tertiary"] p {
    color: var(--halo-text) !important;
}
.st-key-halo_assistant .stButton > button:hover {
    background: rgba(134, 217, 194, 0.1);
    border-color: rgba(134, 217, 194, 0.38);
    color: var(--halo-text);
}
.st-key-halo_assistant .stTextInput input {
    min-height: 2.65rem;
    font-size: 0.82rem;
}
.st-key-halo_assistant .st-key-halo-submit button {
    background: linear-gradient(180deg, #b5e879, #9fcf65);
    border-color: #526744;
    color: #10180e;
    font-weight: 700;
    min-height: 2.55rem;
}
.st-key-halo_assistant .st-key-halo-submit button:hover {
    background: linear-gradient(180deg, #c1f486, #a9da6e);
    color: #07110e;
    border-color: var(--halo-green);
}

/* ---- Form controls ----
   Assistant-scoped rules outrank the global button style by
   specificity, so quick-question buttons stay subdued. */
.stButton > button, .stFormSubmitButton > button {
    border: 1px solid #526744;
    background: linear-gradient(180deg, #b5e879, #9fcf65);
    color: #10180e;
    border-radius: 5px;
    font-weight: 700;
    transition: filter 120ms ease, transform 120ms ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: var(--halo-green);
    color: #07110e;
    filter: brightness(1.07);
    transform: translateY(-1px);
}
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
    background: #0b1510;
    color: var(--halo-text);
    border-color: var(--halo-border);
    border-radius: 5px;
}
.stRadio [role="radiogroup"] { gap: 0.18rem; }
.stRadio [role="radio"] { padding: 0.45rem 0.55rem; border-radius: 5px; }
.stRadio [role="radio"] p { font-size: 0.88rem; }
.stRadio [role="radio"]:has(input:checked) { background: rgba(181, 232, 121, 0.08); }
[data-testid="stMetric"] {
    background: rgba(16, 27, 22, 0.92);
    border: 1px solid var(--halo-border);
    border-radius: 6px;
    padding: 0.75rem 0.85rem;
}
[data-testid="stMetricLabel"] { color: var(--halo-muted); }
[data-testid="stMetricValue"] { color: var(--halo-text); }
[data-testid="stAlert"] { border-radius: 6px; }
</style>
"""


def appearance_css(theme, accent):
    colors = {
        "Halo Green": ("#b5e879", "#78965d", "#378344"),
        "Blue": ("#81c4ff", "#5b93bc", "#2166a4"),
        "Purple": ("#c4a7f7", "#9475c3", "#7349a8"),
    }
    bright, dim, on_light = colors[accent]
    active = on_light if theme == "Light" else bright
    subdued = on_light if theme == "Light" else dim
    light = """
        :root {
            --halo-bg: #f4f7f5; --halo-panel: #ffffff; --halo-panel-raised: #f0f5f2;
            --halo-border: #cad9cf; --halo-border-soft: rgba(33, 72, 53, 0.16);
            --halo-text: #15261d; --halo-muted: #4e6256; --halo-faint: #587064;
        }
        .stApp { background: #f4f7f5; color: var(--halo-text); }
        [data-testid="stSidebar"] { background: #eaf1ec; }
        [class*="st-key-halocard"], [class*="st-key-halocompact"], .st-key-halo_assistant,
        .halo-metric, [data-testid="stMetric"], .halo-response {
            background: #ffffff !important; box-shadow: 0 8px 22px rgba(24, 52, 34, 0.05);
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
            background: #ffffff; color: var(--halo-text);
        }
        .st-key-halo_settings [role="radiogroup"] button {
            background: #ffffff !important;
            border-color: var(--halo-border) !important;
        }
        .st-key-halo_settings [role="radiogroup"] button[aria-checked="true"] {
            background: color-mix(in srgb, var(--halo-green) 12%, white) !important;
            border-color: var(--halo-green) !important;
        }
        .st-key-halo_settings [role="radiogroup"] button p,
        .st-key-halo_settings [role="combobox"],
        .st-key-halo_settings [role="group"] button {
            color: var(--halo-text) !important;
        }
        .st-key-halo_settings [role="group"] { background: #ffffff !important; }
        .st-key-halo_pref_show_completed label > div:first-of-type {
            background: #c5d5ca !important;
            border: 1px solid #8ca797 !important;
        }
        .st-key-halo_pref_show_completed label:has([role="switch"]:checked) > div:first-of-type {
            background: var(--halo-green) !important;
            border-color: var(--halo-green) !important;
        }
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="stSidebarCollapsedControl"] button span { color: var(--halo-text) !important; }
        [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] button { background: #ffffff !important; }
        .halo-callout { background: rgba(31, 105, 62, 0.06); }
        .stButton > button, .stFormSubmitButton > button,
        .st-key-halo_assistant .st-key-halo-submit button { color: #ffffff; }
        .st-key-halo_settings .stButton > button p { color: #ffffff !important; }
    """ if theme == "Light" else ""
    return f"""<style>
        :root {{ --halo-green: {active}; --halo-green-dim: {subdued}; --halo-cyan: {active}; }}
        .halo-brand-mark, .halo-dot, .halo-system-pulse, .halo-ready i {{ background: {active}; }}
        .stButton > button, .stFormSubmitButton > button,
        .st-key-halo_assistant .st-key-halo-submit button {{
            background: {active}; border-color: {dim};
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover,
        .st-key-halo_assistant .st-key-halo-submit button:hover {{
            background: {active}; border-color: {active};
        }}
        .st-key-halo_settings {{ max-width: 880px; }}
        .halo-settings-section {{
            border-top: 1px solid var(--halo-border-soft);
            margin: 1.65rem 0 0.85rem;
            padding-top: 1.2rem;
            color: var(--halo-text);
            font-size: 1.03rem;
            font-weight: 650;
        }}
        .st-key-halo_settings [data-testid="stSegmentedControl"] button {{
            min-height: 2.45rem;
            padding-inline: 0.8rem;
        }}
        .st-key-halo_pref_accent [role="radiogroup"] {{ flex-wrap: wrap; }}
        .st-key-halo_pref_accent button::before {{
            content: "";
            display: inline-block;
            width: 0.65rem;
            height: 0.65rem;
            margin-right: 0.38rem;
            border-radius: 50%;
            background: #b5e879;
        }}
        .st-key-halo_pref_accent button:nth-child(2)::before {{ background: #81c4ff; }}
        .st-key-halo_pref_accent button:nth-child(3)::before {{ background: #c4a7f7; }}
        {light}
    </style>"""
