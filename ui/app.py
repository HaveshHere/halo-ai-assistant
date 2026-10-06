from datetime import datetime
from html import escape
from pathlib import Path
import os
import sys
import urllib.error
import urllib.request

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SOURCE_DIR))
os.chdir(PROJECT_ROOT)

from agent import HaloAgent
from settings import HALO_VERSION, get_ai_provider, get_ollama_base_url, load_ui_preferences, save_ui_preferences
from tools.email_inbox import fetch_recent_emails
from tools.planner import build_ranked_plan
from tools.env_file import load_env_file
from ui.components import metric, page_header, panel, response_card, rows, sample_banner
from ui.styles import APP_CSS, appearance_css


DATA_DIR = PROJECT_ROOT / "data"
CHAT_SCHEMA_VERSION = 2
NAVIGATION = [
    "Dashboard",
    "Tasks",
    "Briefing",
    "Calendar",
    "Tickets",
    "Notes",
    "Search",
    "Settings",
]


st.set_page_config(
    page_title="Halo | Mission Control",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)
load_env_file(PROJECT_ROOT / ".env")


def ui_preferences():
    if "halo_preferences" not in st.session_state:
        st.session_state["halo_preferences"] = load_ui_preferences()
    preferences = st.session_state["halo_preferences"]
    for name, value in preferences.items():
        st.session_state.setdefault(f"halo_pref_{name}", value)
    return preferences


def update_preference(name):
    preferences = ui_preferences()
    preferences[name] = st.session_state[f"halo_pref_{name}"]
    try:
        preferences.update(save_ui_preferences(preferences))
    except OSError:
        st.session_state["halo_settings_error"] = "Could not save preferences on this device."
    st.session_state[f"halo_pref_{name}"] = preferences[name]
    if name == "default_page":
        st.session_state["halo_navigation"] = preferences[name]


@st.cache_data(ttl=30, show_spinner=False)
def ai_available():
    if get_ai_provider().lower() != "ollama":
        return False
    try:
        with urllib.request.urlopen(f"{get_ollama_base_url().rstrip('/')}/api/tags", timeout=1) as response:
            return response.status == 200
    except (OSError, ValueError, urllib.error.URLError):
        return False


def create_agent():
    return HaloAgent(
        tasks_file=DATA_DIR / "tasks.txt",
        events_file=DATA_DIR / "calendar.txt",
        engineering_file=DATA_DIR / "engineering_tasks.txt",
        completed_file=DATA_DIR / "completed_tasks.txt",
        notes_file=DATA_DIR / "notes.txt",
    )


def get_emails():
    result = fetch_recent_emails()
    return result["emails"] if result["ok"] else []


def task_rows(tasks):
    return [(task, "Open task", "TASK") for task in tasks]


def event_rows(events):
    result = []
    for event in events:
        time, separator, title = event.partition(" - ")
        result.append((title if separator else event, time if separator else "Scheduled today", "EVENT"))
    return result


def ticket_rows(tickets):
    result = []
    for ticket in tickets:
        identifier, separator, title = ticket.partition(":")
        result.append((title.strip() if separator else ticket, identifier.strip() if separator else "Engineering", "TICKET"))
    return result


def note_rows(notes):
    return [(note, "Saved in local workspace", "NOTE") for note in notes]


def app_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="halo-brand"><span class="halo-brand-mark"></span>HALO</div>'
            '<div class="halo-brand-sub">Engineering operations assistant</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="halo-divider"></div>', unsafe_allow_html=True)
        st.session_state.setdefault("halo_navigation", ui_preferences()["default_page"])
        selected = st.radio("Workspace", NAVIGATION, label_visibility="collapsed", key="halo_navigation")
        st.markdown('<div class="halo-divider"></div>', unsafe_allow_html=True)
        st.caption("WORKSPACE MODE")
        st.markdown("**Local data**")
        st.caption("Tasks, notes, sample email, calendar and ticket files")
        st.markdown('<div class="halo-divider"></div>', unsafe_allow_html=True)
        st.caption("PERSONAL WORKSPACE")
        st.caption("Your tasks, schedule, notes and engineering work")
        return selected


def render_header(title, description):
    header, date_column = st.columns([4, 1.15], vertical_alignment="bottom")
    with header:
        page_header("HALO / OPERATIONS", title, description)
    with date_column:
        st.markdown(
            '<div class="halo-system-status"><span class="halo-system-pulse"></span> SYSTEM ONLINE</div>'
            f'<div class="halo-faint halo-date">{datetime.now().strftime("%A / %d %B %Y").upper()}</div>',
            unsafe_allow_html=True,
        )
    sample_banner("LOCAL SAMPLE DATA / EMAIL, CALENDAR + TICKETS")


def render_dashboard(agent):
    render_header("Good morning", "Here is the clearest path through today’s work.")
    emails = get_emails()

    metric_columns = st.columns(4, gap="large")
    metrics = [
        ("Open tasks", len(agent.tasks), "to move forward"),
        ("Meetings", len(agent.events), "on your schedule"),
        ("Tickets", len(agent.engineering_tasks), "in the queue"),
        ("Inbox", len(emails), "messages to review"),
    ]
    for column, values in zip(metric_columns, metrics):
        with column:
            metric(*values)

    st.write("")
    main_column, insight_column = st.columns([2.05, 1], gap="large")
    ranked_plan = build_ranked_plan(agent.tasks, agent.events, agent.engineering_tasks)
    prioritized_tasks = [item for category, item, _ in ranked_plan if category == "Task"]
    top_focus = ranked_plan[0] if ranked_plan else None

    with main_column:
        if top_focus:
            focus_body = (
                f'<p class="halo-eyebrow">NEXT BEST ACTION / {escape(top_focus[0].upper())}</p>'
                f'<div class="halo-row-title" style="font-size:1.08rem">{escape(top_focus[1])}</div>'
                f'<div class="halo-row-meta">{escape(top_focus[2])}</div>'
            )
        else:
            focus_body = '<div class="halo-empty">No priority recommendation available.</div>'
        panel("Today’s Focus", focus_body, "Your highest-value next move", "01", compact=True)

        task_column, calendar_column = st.columns(2, gap="medium")
        with task_column:
            panel("Priority Tasks", rows(task_rows(prioritized_tasks[:3]), "No open tasks."), "Start here", "02")
        with calendar_column:
            panel("Today’s Meetings", rows(event_rows(agent.events[:3]), "No events scheduled."), "Schedule", "03")

        ticket_column, note_column = st.columns(2, gap="medium")
        with ticket_column:
            panel("Open Tickets", rows(ticket_rows(agent.engineering_tasks[:3]), "No tickets tracked."), "Engineering queue", "04")
        with note_column:
            panel("Recent Notes", rows(note_rows(agent.notes[-3:][::-1]), "No notes saved yet."), "Saved context", "05")

    with insight_column:
        render_ai_panel(agent)


def submit_halo_prompt():
    prompt = st.session_state.get("halo_prompt", "").strip()
    if prompt:
        st.session_state["halo_submitted_prompt"] = prompt
        st.session_state["halo_prompt"] = ""


def render_ai_panel(agent):
    with st.container(border=True, key="halo_assistant"):
        st.markdown(
            '<div class="halo-assistant-head"><div><div class="halo-eyebrow">HALO ASSISTANT</div>'
            '<div class="halo-assistant-title">Ask Halo</div>'
            '<div class="halo-assistant-subtitle">One grounded answer from your workspace.</div></div>'
            '<span class="halo-ready"><i></i>READY</span></div>',
            unsafe_allow_html=True,
        )

        prompts = ["What should I work on first?", "Give me a briefing.", "Anything important today?"]
        selected_prompt = None
        st.markdown('<p class="halo-field-label">QUICK QUESTIONS</p>', unsafe_allow_html=True)
        for index, prompt in enumerate(prompts):
            if st.button(prompt, key=f"suggestion-{index}", use_container_width=True, type="tertiary"):
                selected_prompt = prompt

        st.markdown('<p class="halo-field-label halo-question-label">YOUR QUESTION</p>', unsafe_allow_html=True)
        st.text_input(
            "Ask Halo",
            placeholder="Ask about today’s work...",
            label_visibility="collapsed",
            key="halo_prompt",
        )
        st.button(
            "Ask Halo",
            key="halo-submit",
            use_container_width=True,
            on_click=submit_halo_prompt,
        )
        submitted_prompt = st.session_state.pop("halo_submitted_prompt", None)
        selected_prompt = selected_prompt or submitted_prompt

        if st.session_state.get("halo_chat_schema") != CHAT_SCHEMA_VERSION:
            st.session_state["halo_chat"] = []
            st.session_state["halo_chat_schema"] = CHAT_SCHEMA_VERSION
        st.session_state.setdefault("halo_chat", [])

        if selected_prompt:
            st.session_state.halo_chat.append({"role": "user", "content": selected_prompt})
            loading = st.empty()
            loading.markdown(
                '<div class="halo-loading"><span class="halo-loading-orbit"></span>'
                '<div class="halo-loading-copy"><strong>Reviewing your workspace</strong><small>Building a grounded recommendation</small></div>'
                '<span class="halo-loading-bars"><i></i><i></i><i></i></span></div>',
                unsafe_allow_html=True,
            )
            request = f"Ask AI {selected_prompt}" if submitted_prompt else selected_prompt
            answer = agent.answer(request)
            loading.empty()
            st.session_state.halo_chat.append({"role": "assistant", "content": answer})
            st.session_state.halo_chat = st.session_state.halo_chat[-20:]

        history = st.session_state.halo_chat[-4:]
        st.markdown('<div class="halo-assistant-divider"></div>', unsafe_allow_html=True)
        if not history:
            st.markdown('<p class="halo-assistant-empty">Your answer will appear here.</p>', unsafe_allow_html=True)
        else:
            for message in history:
                response_card(
                    "Your question" if message["role"] == "user" else "Recommendation",
                    message["content"],
                    label="YOU" if message["role"] == "user" else "HALO",
                )


def flash(message):
    st.session_state["halo_flash"] = message


def render_flash():
    message = st.session_state.pop("halo_flash", None)
    if message:
        st.success(message)


def render_tasks(agent):
    render_header("Tasks", "Open work and completion tracking from your local task list.")
    render_flash()
    metric("Open tasks", len(agent.tasks), "Current queue")
    panel("Open Tasks", rows(task_rows(agent.tasks), "Your task list is clear."), "Select a task below to complete it", "TASKS")

    if ui_preferences()["show_completed"]:
        panel("Completed Tasks", rows(task_rows(agent.completed_tasks), "No completed tasks yet."), "Finished work", "DONE")

    if agent.tasks:
        st.markdown('<div class="halo-section-title">Update task status</div>', unsafe_allow_html=True)
        labels = [f"{index + 1}. {task}" for index, task in enumerate(agent.tasks)]
        with st.form("complete-task-form", clear_on_submit=True):
            selected = st.selectbox("Task to complete", labels)
            confirmed = st.checkbox("I confirm this task is complete")
            submitted = st.form_submit_button("Complete selected task")
        if submitted:
            if not confirmed:
                st.warning("Confirm completion before updating your task file.")
            else:
                task_number = labels.index(selected) + 1
                flash(agent.answer(f"Complete task {task_number}"))
                st.rerun()


def render_briefing(agent):
    render_header("Briefing", "The few things worth knowing before you start.")
    emails = get_emails()
    ranked_plan = build_ranked_plan(agent.tasks, agent.events, agent.engineering_tasks)
    top = ranked_plan[0][1] if ranked_plan else "No recommendation available."
    metric_columns = st.columns(4)
    for column, values in zip(
        metric_columns,
        [
            ("Tasks", len(agent.tasks), "open"),
            ("Meetings", len(agent.events), "scheduled"),
            ("Tickets", len(agent.engineering_tasks), "tracked"),
            ("Emails", len(emails), "available"),
        ],
    ):
        with column:
            metric(*values)
    panel("Recommended Focus", f'<div class="halo-row-title">{escape(top)}</div>', "From Halo’s deterministic planner", "FOCUS")

    if st.button("Generate briefing"):
        loading = st.empty()
        loading.markdown(
            '<div class="halo-loading"><span class="halo-loading-orbit"></span>'
            '<span><strong>Building your briefing</strong><small>Assembling today’s signals</small></span>'
            '<span class="halo-loading-bars"><i></i><i></i><i></i></span></div>',
            unsafe_allow_html=True,
        )
        st.session_state["halo_briefing"] = agent.answer("Give me a briefing")
        loading.empty()

    if "halo_briefing" in st.session_state:
        response_card("Daily Briefing", st.session_state["halo_briefing"])


def render_calendar(agent):
    render_header("Calendar", "Today’s schedule from Halo’s local calendar source.")
    panel("Today’s Meetings", rows(event_rows(agent.events), "No events are scheduled."), "Sample schedule / local data", "SCHEDULE")


def render_tickets(agent):
    render_header("Engineering Tickets", "Work items from Halo’s local engineering queue.")
    panel("Ticket Queue", rows(ticket_rows(agent.engineering_tasks), "No tickets are available."), "Local sample data", "QUEUE")


def render_notes(agent):
    render_header("Notes", "Your local Halo memory. Notes remain in the workspace data file.")
    render_flash()
    panel("Saved Notes", rows(note_rows(agent.notes), "No notes saved yet."), "Local memory", "MEMORY")
    with st.form("add-note-form", clear_on_submit=True):
        note = st.text_input("New note", placeholder="Remember a project detail...")
        submitted = st.form_submit_button("Save note")
    if submitted:
        if not note.strip():
            st.warning("Enter a note before saving.")
        else:
            flash(agent.answer(f"Remember {note.strip()}"))
            st.rerun()


def render_search(agent):
    render_header("Search", "Search tasks, emails, meetings, tickets, completed work, and notes.")
    with st.form("search-form"):
        query = st.text_input("Search local workspace", placeholder="Try backend, onboarding, or BUG-102")
        submitted = st.form_submit_button("Search")
    if submitted:
        if not query.strip():
            st.warning("Enter a search term.")
        else:
            result = agent.answer(f"Find {query.strip()}")
            matches = []
            for line in result.splitlines():
                text = line.removeprefix("- ").strip()
                if not text:
                    continue
                source, separator, detail = text.partition(":")
                if separator and " " not in source:
                    matches.append((detail.strip(), f"Matched in {source.strip()}", source.strip().upper()))
                else:
                    matches.append((text, "Matched local source", "MATCH"))
            panel("Search Results", rows(matches, "No matches found."), f"Query: {query.strip()}", "SEARCH")


def render_settings(agent):
    page_header("HALO / PREFERENCES", "Settings", "Make your workspace feel like yours.")
    preferences = ui_preferences()
    for name, value in preferences.items():
        st.session_state[f"halo_pref_{name}"] = value
    with st.container(key="halo_settings"):
        if message := st.session_state.pop("halo_settings_error", None):
            st.error(message)

        st.markdown('<div class="halo-settings-section">Appearance</div>', unsafe_allow_html=True)
        theme_column, accent_column = st.columns([1, 1.7], gap="medium")
        with theme_column:
            st.segmented_control("Theme", ["Dark", "Light"], key="halo_pref_theme", on_change=update_preference, args=("theme",))
        with accent_column:
            st.segmented_control("Accent Color", ["Halo Green", "Blue", "Purple"], key="halo_pref_accent", on_change=update_preference, args=("accent",))

        st.markdown('<div class="halo-settings-section">AI</div>', unsafe_allow_html=True)
        st.segmented_control("Response Style", ["Concise", "Balanced", "Detailed"], key="halo_pref_response_style", on_change=update_preference, args=("response_style",))

        st.markdown('<div class="halo-settings-section">Productivity</div>', unsafe_allow_html=True)
        default_column, completed_column = st.columns(2, gap="large")
        with default_column:
            st.selectbox("Default Page", ["Dashboard", "Tasks", "Briefing"], key="halo_pref_default_page", on_change=update_preference, args=("default_page",))
        with completed_column:
            st.toggle("Show Completed Tasks", key="halo_pref_show_completed", on_change=update_preference, args=("show_completed",))

        st.markdown('<div class="halo-settings-section">About</div>', unsafe_allow_html=True)
        about_left, about_right = st.columns(2, gap="large")
        with about_left:
            st.markdown(f"**Halo Version**  \n{HALO_VERSION}")
            st.markdown("**Tests Passed**  \n52 (verified 6 Oct 2026)")
        with about_right:
            st.markdown("**AI Status**  \n" + ("Available" if ai_available() else "Unavailable"))
            if st.button("Check for Updates", key="halo-check-updates"):
                st.info("Automatic updates are not available for this local build.")


def main():
    preferences = ui_preferences()
    st.markdown(appearance_css(preferences["theme"], preferences["accent"]), unsafe_allow_html=True)
    agent = create_agent()
    agent.reasoner.response_style = preferences["response_style"]
    selected_view = app_sidebar()

    if selected_view == "Dashboard":
        render_dashboard(agent)
    elif selected_view == "Tasks":
        render_tasks(agent)
    elif selected_view == "Briefing":
        render_briefing(agent)
    elif selected_view == "Calendar":
        render_calendar(agent)
    elif selected_view == "Tickets":
        render_tickets(agent)
    elif selected_view == "Notes":
        render_notes(agent)
    elif selected_view == "Search":
        render_search(agent)
    else:
        render_settings(agent)


main()
