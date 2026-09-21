"""Small widget helpers shared by the panels."""
from __future__ import annotations

from typing import Callable, Optional, Sequence

import streamlit as st


def choose(label: str, options: Sequence, key: str, *, format_func: Callable = str,
           default=None, on_change: Optional[Callable] = None, help: Optional[str] = None,
           label_visibility: str = "visible", width: str = "content"):
    """A segmented control that can never end up with nothing selected.

    Streamlit's segmented control deselects when its selected option is clicked
    again; this wrapper remembers the last valid choice and restores it.
    """
    s = st.session_state
    backup = f"__{key}_last"
    options = list(options)
    if s.get(key) not in options:
        fallback = s.get(backup)
        s[key] = fallback if fallback in options else (default if default in options else options[0])
    s[backup] = s[key]

    def _on_change():
        if s.get(key) is None:
            s[key] = s[backup]
        else:
            s[backup] = s[key]
        if on_change is not None:
            on_change()

    return st.segmented_control(
        label, options, key=key, format_func=format_func, on_change=_on_change,
        help=help, label_visibility=label_visibility, width=width,
    )


def section(icon: str, title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f"#### {icon} {title}")
    if subtitle:
        st.caption(subtitle)
