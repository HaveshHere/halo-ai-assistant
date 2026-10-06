from html import escape
from textwrap import dedent

import streamlit as st


def _card_key(title, index, compact):
    slug = "".join(character.lower() if character.isalnum() else "-" for character in f"{title}-{index or ''}")
    prefix = "halocompact" if compact else "halocard"
    return f"{prefix}-{slug.strip('-')}"


def panel(title, body, subtitle="", index=None, compact=False):
    subtitle_html = f'<div class="halo-panel-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    index_html = f'<span class="halo-panel-index">{escape(index)}</span>' if index else ""
    with st.container(border=True, key=_card_key(title, index, compact)):
        st.markdown(
            dedent(
                f"""
                <div class="halo-panel-head">
                    <div><div class="halo-panel-title">{escape(title)}</div>{subtitle_html}</div>
                    {index_html}
                </div>
                """
            ),
            unsafe_allow_html=True,
        )
        if isinstance(body, list):
            for number, item in enumerate(body, start=1):
                title, meta, tag = item
                if not tag:
                    st.markdown(
                        f'<div class="halo-empty">{escape(str(title))}</div>',
                        unsafe_allow_html=True,
                    )
                    continue

                st.markdown(
                    dedent(
                        f"""
                        <div class="halo-row">
                            <div class="halo-row-number">{number:02d}</div>
                            <div><div class="halo-row-title">{escape(str(title))}</div><div class="halo-row-meta">{escape(str(meta))}</div></div>
                            <span class="halo-tag">{escape(str(tag))}</span>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(body, unsafe_allow_html=True)


def metric(label, value, note):
    st.markdown(
        f"""
        <div class="halo-metric">
            <div class="halo-metric-label">{escape(str(label))}</div>
            <div class="halo-metric-value">{escape(str(value))}</div>
            <div class="halo-metric-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rows(items, empty_message="No local records found."):
    if not items:
        return [(empty_message, "", "")]

    normalized = []
    for item in items:
        if isinstance(item, tuple):
            normalized.append(item)
        else:
            normalized.append((item, "", "ROW"))

    return normalized


def callout(text):
    st.markdown(f'<div class="halo-callout">{escape(text)}</div>', unsafe_allow_html=True)


def response_card(title, text, label="HALO"):
    formatted_text = escape(text).replace("\n", "<br>")
    st.markdown(
        dedent(
            f"""
            <div class="halo-response">
                <div class="halo-response-head"><span>{escape(label)}</span><strong>{escape(title)}</strong></div>
                <div class="halo-response-body">{formatted_text}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def sample_banner(text="LOCAL WORKSPACE DATA"):
    st.markdown(
        f'<div class="halo-sample-banner"><span class="halo-dot"></span>{escape(text)}</div>',
        unsafe_allow_html=True,
    )


def page_header(eyebrow, title, description):
    st.markdown(
        dedent(
            f"""
            <div class="halo-page-header">
                <div class="halo-eyebrow">{escape(eyebrow)}</div>
                <div class="halo-page-title">{escape(title)}</div>
                <div class="halo-page-description">{escape(description)}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
