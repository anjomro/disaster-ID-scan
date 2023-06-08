from pathlib import Path

import toga
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, Pack, BOTTOM


class DisasterUI(toga.App):
    directory: Path

    def startup(self):
        # Main window of the application with title and size
        self.main_window = toga.Window(title="Disaster ID Scanner")

        box = toga.Box(style=Pack(direction=ROW, padding_top=100, alignment=BOTTOM))

        kangoroo_example_image = toga.Image("/home/anjomro/repos/disaster-id-scan/300x200.jpg")
        image_view = toga.ImageView(kangoroo_example_image, id="preview", style=Pack(width=300, height=200))

        select_dialogue = toga.Button("Select directory", on_press=self.select_directory_ui)
        start_video = toga.Button("Start Video")

        control_box = toga.Box(children=[
            start_video,
            select_dialogue
        ])
        box.add(image_view)
        box.add(control_box)

        # Add the content on the main window
        self.main_window.content = box

        # Show the main window
        self.main_window.show()
        self.select_directory_ui()

    def selected_path(self, caller, path: Path):
        if path is None:
            print("Please Select a Path")
        else:
            self.directory = path
        print("fini")

    def select_directory_ui(self, *args):
        self.main_window.select_folder_dialog(title="Select Saving Location", on_result=self.selected_path)


def start_gui():
    DisasterUI("Disaster ID scan", "de.anjomro.disaster-id-scan").main_loop()
