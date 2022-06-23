"""Contains webapp CSS styling."""
# %% Dash app styling
# Styling for content.  Add left margin so content is to the right of sidebar.
content_style = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "margin-top": "0rem",
    "padding": "2rem 1rem",
}

# Style arguments for the sidebar.
sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}

# Styles for paragraphs embedded in divs in side bar
sidebar_div_style = {
    "display": "table",
    "border-bottom-style": "solid",
    "border-width": "thin",
    "padding": "1em 1em 0.2em 1em"
}

paragraph_style = {
    "text-align": "center",
    "vertical-align": "middle",
    "display": "table-cell",
    "font-weight": "bold"
}
