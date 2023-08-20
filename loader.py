import tkinter as tk
from tkinter import ttk, simpledialog
import threading
import logging

# Global variables
message_box = None
timeout_thread = None
timeout_event = None
countdown_var = None
running = True
countdown_triggered_by_button = False
log_file = "Logs/Loader/latest.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Customizable variables
countdown_time = 30
window_width = 300
window_height = 140

# Initialize main window
root = tk.Tk()
root.withdraw()  # Hide the main window

def clear_log_file(file_path):
    with open(file_path, "w") as file:
        pass

def calculate_message_box_position():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    dpi = root.winfo_fpixels('1i')

    x_offset = int(2 * dpi)
    y_offset = int(2 * dpi)

    x = screen_width - window_width - x_offset
    y = screen_height - window_height - y_offset

    return x, y

def create_message_box(title, message, buttons, show_close_button=True):
    global message_box, timeout_thread, timeout_event, countdown_var
    message_box = tk.Toplevel(root)
    message_box.title(title)
    message_box.overrideredirect(1)

    message_box.configure(borderwidth=4, relief=tk.RIDGE)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 14), padding=10)
    style.configure("TButton", font=("Helvetica", 12), padding=10)

    countdown_var = tk.StringVar(value=message)
    message_label = ttk.Label(message_box, textvariable=countdown_var)
    message_label.pack()

    for button_text, button_command in buttons:
        button = ttk.Button(message_box, text=button_text, command=button_command)
        button.pack(side=tk.LEFT if button_text == "Start now" else tk.RIGHT, padx=10, pady=10)

    timeout_event = threading.Event()
    timeout_thread = threading.Thread(target=timeout_callback)
    timeout_thread.start()

    message_box.attributes("-topmost", True)

    if show_close_button:
        message_box.protocol("WM_DELETE_WINDOW", lambda: None)

def on_start_button_click():
    global running, countdown_triggered_by_button
    if not countdown_triggered_by_button:
        running = False
        countdown_triggered_by_button = True
        timeout_event.set()
        message_box.destroy()
        start_afk()
    root.quit()

def on_cancel_button_click():
    global running
    running = False
    timeout_event.set()
    message_box.destroy()

    minutes = ask_minutes()

    if minutes is not None:
        running = True
        logging.info("Reprompting in {} minute{}".format(minutes, ("s" if minutes != 1 else "")))
        root.after((minutes * 60 * 1000) if minutes != 1010 else 1000, start_message_box)

def start_afk():
    logging.info("Starting AFK...")

def update_countdown(i):
    global countdown_triggered_by_button
    if i > 0 and running:
        countdown_var.set(f"Starting AFK in {i}...")
        logging.info(f"Countdown: {i}")
        root.after(1000, update_countdown, i - 1)
    else:
        countdown_var.set("Starting AFK now...")
        if running and i == 0 and not countdown_triggered_by_button:
            logging.info("Countdown finished, calling start_afk() from update_countdown")
            start_afk()
            countdown_triggered_by_button = True
            on_start_button_click()
        else:
            logging.info("Countdown stopped or not at the end")

def timeout_callback():
    update_countdown(countdown_time)

def ask_minutes():
    logging.info("Asking how long until reprompt")
    minutes = simpledialog.askinteger("Auto Anti AFK", "Enter the number of minutes until reprompting:", parent=root, minvalue=1)
    if minutes is None:
        logging.info("Canceled")
        root.quit()
    return minutes

def start_message_box():
    logging.info("Spawning message box")
    
    try:
        create_message_box("Auto Anti AFK", f"Starting AFK in {countdown_time}...", [("Start now", on_start_button_click), ("Cancel", on_cancel_button_click)], show_close_button=False)
    except:
        logging.error("Error spawning message box.")

    x, y = calculate_message_box_position()
    message_box.geometry(f"{window_width}x{window_height}+{x}+{y}")

clear_log_file(log_file)

start_message_box()

root.mainloop()