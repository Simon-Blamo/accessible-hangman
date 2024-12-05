# define the accessibility theme options 
class Theme:
    # for brighter lighting
    LIGHT_MODE = { 
        "mode": "light_mode",
        "button_hover": "lightblue",
        "button_hover_text": "black",
        "guess_background": "lightgrey",
        "guess_text": "black",
        "background": "#F3F3F3",
        "text": "black",
        "button": "lightgrey",
        "button_text": "black",
        "button_border": "black",
        "label": "Light Mode ☀️ (Default)",
        "disabled_btn_background": "white",
        "disabled_btn_text": "black",
        "correct_bg": "#03da00",
        "incorrect_bg": "red",
        "dropdown": "white",
        "dropdown_text": "black",
        "dialog": "white",
        "dialog_text": "black",
        "listbox": "white",
        "listbox_text": "black",
        "menu": "white",
        "menu_text": "black",
        "grade_indicator": "black",
        "win": "green",
        "lose": "red"
    }
    # for lower lighting
    DARK_MODE = {
        "mode": "dark_mode",
        "button_hover": "lightblue",
        "button_hover_text": "black",
        "guess_background": "lightgrey",
        "guess_text": "black",
        "background": "#3A3A3A",
        "text": "white",
        "button": "grey",
        "button_text": "white",
        "button_border": "white",
        "label": "Dark Mode 🌙",
        "disabled_btn_background": "#3A3A3A",
        "disabled_btn_text": "black",
        "correct_bg": "#03da00",
        "incorrect_bg": "red",
        "dropdown": "#2C2C2C",
        "dropdown_text": "white",
        "dialog": "#3A3A3A",
        "dialog_text": "white",
        "listbox": "#2C2C2C",
        "listbox_text": "white",
        "menu": "#2C2C2C",
        "menu_text": "white",
        "grade_indicator": "#4C4C4C",
        "win": "green",
        "lose": "red"
    }
    # for Black and White
    CONTRAST = {
        "mode": "contrast",
        "button_hover": "lightblue",
        "button_hover_text": "black",
        "guess_background": "white",
        "guess_text": "black",
        "background": "white",
        "text": "black",
        "button": "black",
        "button_text": "white",
        "button_border": "black",
        "label": "Black & White Contrast ⚫⚪",
        "disabled_btn_background": "white",
        "disabled_btn_text": "lightgrey",
        "correct_bg": "#03da00",
        "incorrect_bg": "red",
        "dropdown": "white",
        "dropdown_text": "black",
        "dialog": "white",
        "dialog_text": "black",
        "listbox": "white",
        "listbox_text": "black",
        "menu": "white",
        "menu_text": "black",
        "grade_indicator": "black",
        "win": "green",
        "lose": "red"
    }
    # for users with Blue-Yellow color blindness
    BLUE_YELLOW = {
        "mode": "blue_yellow",
        "button_hover": "pink",
        "button_hover_text": "black",
        "guess_background": "white",
        "guess_text": "black",
        "background": "lightgreen",
        "text": "black",
        "button": "green",
        "button_text": "white",
        "button_border": "black",
        "label": "Blue-Yellow Color Blindness 🔵🟡",
        "disabled_btn_background": "lightgreen",
        "disabled_btn_text": "black",
        "correct_bg": "#b5ff00",
        "incorrect_bg": "red",
        "dropdown": "#FFFFE0",
        "dropdown_text": "black",
        "dialog": "#FFFFE0",
        "dialog_text": "black",
        "listbox": "#FFFFE0",
        "listbox_text": "black",
        "menu": "#FFFFE0",
        "menu_text": "black",
        "grade_indicator": "blue",
        "win": "green",
        "lose": "red"
    }
    # for users with Red-Green color blindness
    RED_GREEN = {
        "mode": "red_green",
        "button_hover": "lightblue",
        "button_hover_text": "black",
        "guess_background": "white",
        "guess_text": "black",
        "background": "#ddebff",
        "text": "black",
        "button": "blue",
        "button_text": "white",
        "button_border": "black",
        "label": "Red-Green Color Blindness 🔴🟢",
        "disabled_btn_background": "#ddebff",
        "disabled_btn_text": "black",
        "correct_bg": "DeepSkyBlue",
        "incorrect_bg": "GoldenRod",
        "dropdown": "#E0FFFF",
        "dropdown_text": "black",
        "dialog": "#E0FFFF",
        "dialog_text": "black",
        "listbox": "#E0FFFF",
        "listbox_text": "black",
        "menu": "#E0FFFF",
        "menu_text": "black",
        "grade_indicator": "blue",
        "win": "blue",
        "lose": "GoldenRod"
    }
    # for users with complete color blindness
    MONOCHROMATIC = {
        "mode": "monochromatic",
        "button_hover": "blue",
        "button_hover_text": "white",
        "guess_background": "lightgrey",
        "guess_text": "black",
        "background": "grey",
        "text": "black",
        "button": "lightgrey",
        "button_text": "black",
        "button_border": "black",
        "label": "Monochromatic 🌑",
        "disabled_btn_background": "grey",
        "disabled_btn_text": "black",
        "correct_bg": "#03da00",
        "incorrect_bg": "red",
        "dropdown": "lightgrey",
        "dropdown_text": "black",
        "dialog": "grey",
        "dialog_text": "black",
        "listbox": "lightgrey",
        "listbox_text": "black",
        "menu": "darkgrey",
        "menu_text": "black",
        "grade_indicator": "darkgrey",
        "win": "green",
        "lose": "red"
    }

    Themes = [LIGHT_MODE, DARK_MODE, CONTRAST, BLUE_YELLOW, RED_GREEN, MONOCHROMATIC]