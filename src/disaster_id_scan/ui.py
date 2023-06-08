import toga


def button_handler(widget):
    print("hello")


def build(app):
    box = toga.Box()

    button = toga.Button("Hello world", on_press=button_handler)
    button.style.padding = 50
    button.style.flex = 1
    box.add(button)

    return box


def start_gui():
    toga.App("Disaster ID scan", "de.anjomro.disaster-id-scan", startup=build).main_loop()