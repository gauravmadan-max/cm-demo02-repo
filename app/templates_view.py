"""Dynamic greeting banner rendering."""

from flask import render_template_string


def render_greeting_banner(name: str) -> str:
    """Render an HTML status banner addressed to the user."""
    template = (
        "<!doctype html>"
        "<html><body>"
        f"<h1>Welcome, {name}!</h1>"
        "<p>OpsPortal Status: Online</p>"
        "</body></html>"
    )
    return render_template_string(template)
