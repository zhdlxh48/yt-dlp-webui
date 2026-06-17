from __future__ import annotations

import webbrowser


def open_dashboard(url: str) -> None:
    webbrowser.open(url, new=2, autoraise=True)

