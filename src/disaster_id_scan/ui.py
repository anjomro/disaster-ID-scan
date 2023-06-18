# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2
import tkinter as tk
from pathlib import Path
from tkinter import ttk
import sv_ttk
from tkinter import filedialog
import cv2
from PIL import ImageTk, Image
import threading
import easyocr
from tkcalendar import DateEntry

from disaster_id_scan.mrz import parse_mrz
from disaster_id_scan.store import Person, Registrants


def get_available_cameras():
    camera_indexes = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            camera_indexes.append(i)
        cap.release()
    return camera_indexes


class VideoStreamer:
    possible_resolutions = [
        (640, 480),
        (1024, 600),
        (1024, 640),
        (960, 720),
        (1024, 768),
        (1024, 800),
        (1280, 720),
        (1280, 768),
        (1280, 800),
        (1024, 1024),
        (1080, 1200),
        (1280, 1024),
        (1440, 1024),
        (1440, 1080),
        (1600, 1024),
        (1680, 1050),
        (1600, 1200),
        (1600, 1280),
        (1920, 1080),
        (2048, 1080),
        (1920, 1200),
        (2048, 1152),
        (1920, 1280),
        (2400, 1080),
        (1800, 1440),
        (2048, 1280),
        (1920, 1400),
        (2520, 1080),
        (1920, 1440),
        (2560, 1080),
        (2160, 1440),
        (2560, 1440),
        (2560, 1600),
        (2880, 1440),
        (2960, 1440),
        (2560, 1700),
        (2560, 1800),
        (2560, 1920),
    ]

    def __init__(self, camera_index, image_label):
        self.camera_index = camera_index
        self.image_label = image_label
        self.is_running = False
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        # Set resolution
        w, h = self.get_resolution()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.is_running = True
        self.show_frame()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()

    def get_resolution(self):
        max_w, max_h = self.possible_resolutions[0]
        for w, h in self.possible_resolutions:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            if self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) == w and self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) == h:
                if w * h > max_w * max_h:
                    max_w, max_h = w, h
        return max_w, max_h

    def show_frame(self):
        if not self.is_running:
            return

        _, frame = self.cap.read()
        # Convert the image to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
        # if larger than 640x480, rescale
        width = 1000
        if imgtk.width() > width:
            height = int(imgtk.height() * (width / imgtk.width()))
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame).resize((width, height)))
        self.image_label.imgtk = imgtk
        self.image_label.configure(image=imgtk, width=imgtk.width(), height=imgtk.height())
        self.image_label.after(10, self.show_frame)  # Update the frame every 10 milliseconds


class GUI:
    def __init__(self):
        self.loaded_person_id: int = None
        self.window = tk.Tk()
        self.window.title("Disaster ID Scan")
        # self.style = ttk.Style("cosmo")
        self.store = Registrants()

        self.frame = tk.LabelFrame(self.window, text="Camera")
        self.frame.grid(row=0, column=0, rowspan=4, padx=10, pady=20)
        # Create black placeholder 640x480 as list
        # placeholder_array = [[0 for _ in range(640)] for _ in range(480)]
        # imgtk = ImageTk.PhotoImage(image=Image.fromarray(placeholder_array))
        self.image_label = tk.Label(self.frame)
        self.set_camera_placeholder()
        self.image_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.buttons_frame = tk.LabelFrame(self.frame, text="Actions")
        self.buttons_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, ipady=5, ipadx=5)

        self.camera_indexes = get_available_cameras()

        self.camera_label = ttk.Label(self.buttons_frame, text="Camera:")
        self.camera_label.grid(row=0, column=1, padx=5, sticky="e")
        self.camera_combobox = ttk.Combobox(self.buttons_frame, values=[str(idx) for idx in self.camera_indexes],
                                            state="readonly")
        if self.camera_indexes:
            self.camera_combobox.current(self.camera_indexes[0])
        self.camera_combobox.grid(row=0, column=2, pady=5)

        self.start_stop_video = ttk.Button(self.buttons_frame, text="Start video", command=self.start_or_stop_video)
        self.capture_text = ttk.Button(self.buttons_frame, text="Recognize Text", command=self.capture_frame_text)
        self.select_data_folder = ttk.Button(self.buttons_frame, text="Select Data Folder",
                                             command=self.open_data_folder_selector)
        self.start_stop_video.grid(row=1, column=0, padx=5)
        self.capture_text.grid(row=1, column=1, padx=5)
        self.select_data_folder.grid(row=1, column=2, padx=5)

        # LabelFrame to Load existing person / data
        self.load_frame = ttk.LabelFrame(self.window, text="Load Person")
        self.load_frame.grid(row=1, column=3, columnspan=2, pady=10, padx=10, ipadx=5, ipady=5, sticky="nsew")
        # Create Combobox to select existing person
        self.load_frame.columnconfigure(0, weight=1)
        self.person_combobox = ttk.Combobox(self.load_frame, values=self.store.get_name_list(), state="readonly")
        self.person_combobox.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.load_person_button = ttk.Button(self.load_frame, text="Load Person", command=self.load_person_from_list)
        self.load_person_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.data_frame = ttk.LabelFrame(self.window, text="Data")
        self.data_frame.grid(row=0, column=3, columnspan=2, pady=10, padx=10, sticky="nsew")
        # self.data_frame.pack(pady=10)

        self.first_name_label = ttk.Label(self.data_frame, text="First Name:")
        self.first_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.first_name_entry = ttk.Entry(self.data_frame)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.last_name_label = ttk.Label(self.data_frame, text="Last Name:")
        self.last_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.last_name_entry = ttk.Entry(self.data_frame)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.date_of_birth_label = ttk.Label(self.data_frame, text="Date of Birth:")
        self.date_of_birth_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_of_birth_entry = DateEntry(self.data_frame)
        self.date_of_birth_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.nationality_label = ttk.Label(self.data_frame, text="Nationality:")
        self.nationality_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.nationality_entry = ttk.Entry(self.data_frame)
        self.nationality_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.residence_label = ttk.Label(self.data_frame, text="Residence:")
        self.residence_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.residence_entry = ttk.Entry(self.data_frame)
        self.residence_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.place_of_catastrophe_label = ttk.Label(self.data_frame, text="Place of Catastrophe:")
        self.place_of_catastrophe_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.place_of_catastrophe_entry = ttk.Entry(self.data_frame)
        self.place_of_catastrophe_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        self.place_of_shelter_label = ttk.Label(self.data_frame, text="Place of Shelter:")
        self.place_of_shelter_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.place_of_shelter_entry = ttk.Entry(self.data_frame)
        self.place_of_shelter_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        self.date_of_catastrophe_label = ttk.Label(self.data_frame, text="Date of Catastrophe:")
        self.date_of_catastrophe_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.date_of_catastrophe_entry = DateEntry(self.data_frame)
        self.date_of_catastrophe_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        self.error_label = tk.Label(self.window, text="", fg="red")
        # self.error_label.pack()

        self.video_streamer = None
        self.data_folder_selected = False

        self.create_button = ttk.Button(self.data_frame, text="Create", command=self.create_person)
        self.save_changes_button = ttk.Button(self.data_frame, text="Save Changes", command=self.save_changes)
        self.clear_button = ttk.Button(self.data_frame, text="Reset", command=self.clear_form)
        self.delete_button = ttk.Button(self.data_frame, text="Delete", command=self.delete_person)

        self.create_button.grid(row=4, column=0, pady=20)
        self.save_changes_button.grid(row=4, column=1, pady=20)
        self.clear_button.grid(row=4, column=2)
        self.delete_button.grid(row=4, column=3)

        # Save changes and delete buttons are disabled until a person is loaded
        self.save_changes_button.config(state="disabled")
        self.delete_button.config(state="disabled")

    def start_or_stop_video(self):
        if not self.data_folder_selected:
            self.display_error("Please select a data folder.")
            return

        if self.video_streamer and self.video_streamer.is_running:
            self.video_streamer.stop()
            self.start_stop_video.config(text="Start video")
        else:
            try:
                camera_index = int(self.camera_combobox.get())
            except ValueError:
                self.display_error("Please check that a camera is available and selected.")
                return
            self.video_streamer = VideoStreamer(camera_index, self.image_label)
            self.video_streamer.start()
            self.start_stop_video.config(text="Stop video")

    def set_camera_placeholder(self):
        self.image_label = tk.Label(self.frame, text="No camera active", width=125, height=33, bg="black", fg="white")

    def capture_frame_text(self):
        if not self.video_streamer or not self.video_streamer.is_running:
            self.display_error("Please start the video before recognizing text.")
            return

        frame = self.video_streamer.cap.read()[1]
        reader = easyocr.Reader(['de'])
        text = reader.readtext(frame, paragraph=True, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<')
        print(text)
        for element in text:
            if "<" in element[1]:
                # Assume that it could be the MRZ, try to parse it
                possible_mrz = element[1]
                possible_mrz = possible_mrz.upper()
                parsed = parse_mrz(possible_mrz)
                if parsed is not None:
                    # Set the values in the form
                    self.set_person(parsed)
                    self.set_buttons_enabled(False)
    def open_data_folder_selector(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.data_folder_selected = True
            self.display_error("")
            print("Selected data folder:", folder_selected)
            self.store.set_path(Path(folder_selected))
            self.update_person_combobox()
        else:
            self.data_folder_selected = False
            self.display_error("Please select a data folder.")

    def update_person_combobox(self):
        self.person_combobox['values'] = self.store.get_name_list()

    def get_person_from_form(self) -> Person:
        human = Person()
        human.first_name = self.first_name_entry.get()
        human.last_name = self.last_name_entry.get()
        human.date_of_birth = self.date_of_birth_entry.get_date()
        human.nationality = self.nationality_entry.get()
        human.residence = self.residence_entry.get()
        human.place_of_catastrophe = self.place_of_catastrophe_entry.get()
        human.place_of_shelter = self.place_of_shelter_entry.get()
        human.date_of_catastrophe = self.date_of_catastrophe_entry.get_date()
        return human

    def create_person(self):
        human = self.get_person_from_form()
        self.store.add(human)
        self.store.save()
        self.clear_form()
        self.update_person_combobox()

    def save_changes(self):
        human = self.get_person_from_form()
        # Get the ID of the person that is currently loaded
        person_id, _ = self.store.get_person_by_list_entry(self.person_combobox.get())
        self.store.update(self.loaded_person_id, human)
        self.update_person_combobox()
        # Set the combobox to the person that was just edited
        self.person_combobox.current(person_id)


    def delete_person(self):
        selected_id, _ = self.store.get_person_by_list_entry(self.person_combobox.get())
        self.store.delete(self.loaded_person_id)
        self.clear_form()
        self.update_person_combobox()
        if self.loaded_person_id == selected_id:
            self.person_combobox.current(0)
        elif self.loaded_person_id > selected_id:
            self.person_combobox.current(self.loaded_person_id - 1)
        else:
            self.person_combobox.current(self.loaded_person_id)
        self.set_buttons_enabled(False)

    def clear_form(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.date_of_birth_entry.set_date(None)
        self.nationality_entry.delete(0, tk.END)
        self.residence_entry.delete(0, tk.END)
        # Don't clear the place of catastrophe and shelter, because they are often the same
        # self.place_of_catastrophe_entry.delete(0, tk.END)
        # self.place_of_shelter_entry.delete(0, tk.END)
        # self.date_of_catastrophe_entry.set_date(None)
        self.set_buttons_enabled(False)

    def set_text(self, entry: tk.Entry, text: str):
        # Sets the text of an entry, removes old text
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def set_text_if_not_none(self, entry: tk.Entry, text: str):
        # Sets the text of an entry, only if the text is not None
        if text is not None:
            self.set_text(entry, text)

    def set_person(self, person: Person):
        # Sets the values in the form to the values of the person object
        self.set_text(self.first_name_entry, person.first_name)
        self.set_text(self.last_name_entry, person.last_name)
        self.date_of_birth_entry.set_date(person.date_of_birth)
        self.set_text(self.residence_entry, person.residence)
        self.set_text(self.nationality_entry, person.nationality)
        self.set_text_if_not_none(self.place_of_catastrophe_entry, person.place_of_catastrophe)
        self.set_text_if_not_none(self.place_of_shelter_entry, person.place_of_shelter)
        if person.date_of_catastrope is not None:
            self.date_of_catastrophe_entry.set_date(person.date_of_catastrope)

    def load_person_from_list(self):
        # Get the choosen list entry from combobox
        selected_person = self.person_combobox.get()
        # Get the person object from the self.store
        person_id, person = self.store.get_person_by_list_entry(selected_person)
        # Set the values in the form
        self.set_person(person)
        # Set the loaded person id
        self.loaded_person_id = person_id
        # Enable the save and delete button
        self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled: bool):
        '''
        Enables or disables the save and delete button. They should only be enabled if a person is loaded.
        '''
        self.save_changes_button.config(state=tk.NORMAL if enabled else tk.DISABLED)
        self.delete_button.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def display_error(self, message):
        self.error_label.config(text=message)

    def start_gui(self):
        sv_ttk.use_light_theme()
        self.window.mainloop()
        self.window.destroy()


def start_gui():
    gui = GUI()
    gui.start_gui()


start_gui()
