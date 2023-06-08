import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import cv2
from PIL import ImageTk, Image
import threading
import easyocr
from tkcalendar import DateEntry

from disaster_id_scan.mrz import parse_mrz

def get_available_cameras():
    camera_indexes = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            camera_indexes.append(i)
        cap.release()
    return camera_indexes


class VideoStreamer:
    def __init__(self, camera_index, image_label):
        self.camera_index = camera_index
        self.image_label = image_label
        self.is_running = False
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.is_running = True
        self.show_frame()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()

    def show_frame(self):
        if not self.is_running:
            return

        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk
        self.image_label.configure(image=imgtk)
        self.image_label.after(10, self.show_frame)  # Update the frame every 10 milliseconds


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Simple GUI")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.image_label = tk.Label(self.window)
        self.image_label.pack(pady=10)

        self.frame = tk.Frame(self.window)
        self.frame.pack()

        self.camera_indexes = get_available_cameras()

        self.camera_label = ttk.Label(self.frame, text="Camera:")
        self.camera_label.grid(row=0, column=0, padx=5)
        self.camera_combobox = ttk.Combobox(self.frame, values=self.camera_indexes, state="readonly")
        self.camera_combobox.current(0)
        self.camera_combobox.grid(row=0, column=1, padx=5)

        self.buttons_frame = tk.Frame(self.window)
        self.buttons_frame.pack()

        self.start_stop_video = ttk.Button(self.buttons_frame, text="Start video", command=self.start_or_stop_video)
        self.capture_text = ttk.Button(self.buttons_frame, text="Recognize Text", command=self.capture_frame_text)
        self.select_data_folder = ttk.Button(self.buttons_frame, text="Select Data Folder",
                                             command=self.open_data_folder_selector)
        self.start_stop_video.grid(row=0, column=0, padx=5)
        self.capture_text.grid(row=0, column=1, padx=5)
        self.select_data_folder.grid(row=0, column=2, padx=5)

        self.data_frame = ttk.Frame(self.window)
        self.data_frame.pack(pady=10)

        self.first_name_label = ttk.Label(self.data_frame, text="First Name:")
        self.first_name_label.grid(row=0, column=0, padx=5, pady=5)
        self.first_name_entry = ttk.Entry(self.data_frame)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.last_name_label = ttk.Label(self.data_frame, text="Last Name:")
        self.last_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.last_name_entry = ttk.Entry(self.data_frame)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.date_of_birth_label = ttk.Label(self.data_frame, text="Date of Birth:")
        self.date_of_birth_label.grid(row=2, column=0, padx=5, pady=5)
        self.date_of_birth_entry = DateEntry(self.data_frame)
        self.date_of_birth_entry.grid(row=2, column=1, padx=5, pady=5)

        self.nationality_label = ttk.Label(self.data_frame, text="Nationality:")
        self.nationality_label.grid(row=3, column=0, padx=5, pady=5)
        self.nationality_entry = ttk.Entry(self.data_frame)
        self.nationality_entry.grid(row=3, column=1, padx=5, pady=5)

        self.residence_label = ttk.Label(self.data_frame, text="Residence:")
        self.residence_label.grid(row=0, column=2, padx=5, pady=5)
        self.residence_entry = ttk.Entry(self.data_frame)
        self.residence_entry.grid(row=0, column=3, padx=5, pady=5)

        self.place_of_catastrophe_label = ttk.Label(self.data_frame, text="Place of Catastrophe:")
        self.place_of_catastrophe_label.grid(row=1, column=2, padx=5, pady=5)
        self.place_of_catastrophe_entry = ttk.Entry(self.data_frame)
        self.place_of_catastrophe_entry.grid(row=1, column=3, padx=5, pady=5)

        self.place_of_shelter_label = ttk.Label(self.data_frame, text="Place of Shelter:")
        self.place_of_shelter_label.grid(row=2, column=2, padx=5, pady=5)
        self.place_of_shelter_entry = ttk.Entry(self.data_frame)
        self.place_of_shelter_entry.grid(row=2, column=3, padx=5, pady=5)

        self.date_of_catastrophe_label = ttk.Label(self.data_frame, text="Date of Catastrophe:")
        self.date_of_catastrophe_label.grid(row=3, column=2, padx=5, pady=5)
        self.date_of_catastrophe_entry = DateEntry(self.data_frame)
        self.date_of_catastrophe_entry.grid(row=3, column=3, padx=5, pady=5)

        self.error_label = tk.Label(self.window, text="", fg="red")
        self.error_label.pack()

        self.video_streamer = None
        self.data_folder_selected = False

        self.submit_button = ttk.Button(self.window, text="Submit", command=self.submit_click)
        self.reset_button = ttk.Button(self.window, text="Reset", command=self.clear_click)
        self.submit_button.pack(side=tk.LEFT, padx=5, pady=10)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=10)

    def start_or_stop_video(self):
        if not self.data_folder_selected:
            self.display_error("Please select a data folder.")
            return

        if self.video_streamer and self.video_streamer.is_running:
            self.video_streamer.stop()
            self.start_stop_video.config(text="Start video")
        else:
            camera_index = int(self.camera_combobox.get())
            self.video_streamer = VideoStreamer(camera_index, self.image_label)
            self.video_streamer.start()
            self.start_stop_video.config(text="Stop video")

    def capture_frame_text(self):
        if not self.video_streamer or not self.video_streamer.is_running:
            self.display_error("Please start the video before recognizing text.")
            return

        frame = self.video_streamer.cap.read()[1]
        reader = easyocr.Reader(['de'])
        text = reader.readtext(frame, paragraph=True)
        print(text)
        for element in text:
            if "<" in element[1]:
                # Assume that it could be the MRZ, try to parse it
                possible_mrz = element[1]
                possible_mrz = possible_mrz.upper()
                parsed = parse_mrz(possible_mrz)
                if parsed is not None:
                    # Set the values in the form
                    self.first_name_entry.insert(0, parsed.first_name)
                    self.last_name_entry.insert(0, parsed.last_name)
                    self.date_of_birth_entry.set_date(parsed.date_of_birth)
                    self.residence_entry.insert(0, parsed.residence)



    def open_data_folder_selector(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.data_folder_selected = True
            self.display_error("")
            print("Selected data folder:", folder_selected)
        else:
            self.data_folder_selected = False
            self.display_error("Please select a data folder.")

    def submit_click(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        date_of_birth = self.date_of_birth_entry.get_date()
        nationality = self.nationality_entry.get()
        residence = self.residence_entry.get()
        place_of_catastrophe = self.place_of_catastrophe_entry.get()
        place_of_shelter = self.place_of_shelter_entry.get()
        date_of_catastrophe = self.date_of_catastrophe_entry.get_date()

        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("Date of Birth:", date_of_birth)
        print("Nationality:", nationality)
        print("Residence:", residence)
        print("Place of Catastrophe:", place_of_catastrophe)
        print("Place of Shelter:", place_of_shelter)
        print("Date of Catastrophe:", date_of_catastrophe)


    def clear_click(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.date_of_birth_entry.set_date(None)
        self.nationality_entry.delete(0, tk.END)
        self.residence_entry.delete(0, tk.END)
        # Don't clear the place of catastrophe and shelter, because they are often the same
        #self.place_of_catastrophe_entry.delete(0, tk.END)
        #self.place_of_shelter_entry.delete(0, tk.END)
        #self.date_of_catastrophe_entry.set_date(None)

    def display_error(self, message):
        self.error_label.config(text=message)

    def start_gui(self):
        self.window.mainloop()


def start_gui():
    gui = GUI()
    gui.start_gui()


start_gui()
