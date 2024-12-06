import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import math

# User credentials and roles
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
}

# Queue lists
front_queue = []
other_queue = []

# Global variables
current_user_role = None
ride_in_progress = False  # Track if the ride is currently in progress
ride_start_time = 0  # The time the ride started
ride_duration = 120  # The duration of the ride in seconds (2 minutes)
boarding_time = 5  # Time it takes to board/unboard a rider in seconds
riders_to_dispatch = 28  # Max number of riders per ride
ride_time_left = ride_duration  # Time left for the current ride

# Simulate guest arrivals for the front queue
def simulate_front_queue():
    # Adds guests to the front queue at a rate of one every 6 seconds
    front_queue.append(1)
    root.after(6000, simulate_front_queue)

# Simulate guest arrivals for the other queue at a rate of 3 seconds
def simulate_other_queue():
    other_queue.append(1)
    root.after(3000, simulate_other_queue)

# Calculate estimated queue time based on the number of riders and capacity
def calculate_queue_time():
    total_riders = len(front_queue) + len(other_queue)
    riders_per_minute = 1000 / 60  # 1000 riders per hour = 16.67 riders per minute
    estimated_time = total_riders / riders_per_minute
    return math.ceil(estimated_time)

# Main Application for Logged-in Users
def show_main_application():
    global ride_in_progress
    global ride_start_time

    main_app = tk.Toplevel(root)
    main_app.title("Main Dashboard")
    main_app.geometry("600x400")
    main_app.configure(bg="lightblue")

    tk.Label(main_app, text="Queue Management Dashboard", font=("Helvetica", 16, "bold"), bg="lightblue").pack(pady=20)

    # Queue status display
    def update_dashboard():
        global ride_in_progress
        global ride_start_time
        global ride_time_left

        # Calculate the estimated queue time
        estimated_time = calculate_queue_time()

        front_queue_label.config(text=f"Front Queue: {len(front_queue)} guests")
        other_queue_label.config(text=f"Other Queue: {len(other_queue)} guests")
        queue_time_label.config(text=f"Estimated Queue Time: {estimated_time} mins")

        if ride_in_progress:
            remaining_time = max(0, ride_time_left - (time.time() - ride_start_time))
            remaining_time_label.config(text=f"Time Until Ride Finish: {round(remaining_time)} secs")
            if remaining_time == 0:
                ride_in_progress = False
                remaining_time_label.config(text="No Ride in Progress")
        else:
            remaining_time_label.config(text="No Ride in Progress")

        main_app.after(1000, update_dashboard)  # Update every second

    front_queue_label = tk.Label(main_app, text="Front Queue: 0 guests", font=("Helvetica", 12), bg="lightblue")
    front_queue_label.pack(pady=10)

    other_queue_label = tk.Label(main_app, text="Other Queue: 0 guests", font=("Helvetica", 12), bg="lightblue")
    other_queue_label.pack(pady=10)

    queue_time_label = tk.Label(main_app, text="Estimated Queue Time: 0 mins", font=("Helvetica", 12), bg="lightblue")
    queue_time_label.pack(pady=10)

    remaining_time_label = tk.Label(main_app, text="No Ride in Progress", font=("Helvetica", 12), bg="lightblue")
    remaining_time_label.pack(pady=10)

    # Admin-only controls
    if current_user_role == "admin":
        def manual_override():
            # Manual override for admin to add/remove riders
            def adjust_riders():
                action = rider_action.get()
                try:
                    riders = int(rider_entry.get())
                    if riders < 1:
                        messagebox.showwarning("Invalid Input", "Please enter a number greater than 0.")
                    else:
                        if action == "Add":
                            for _ in range(riders):
                                front_queue.append(1)
                                other_queue.append(1)
                        elif action == "Remove":
                            removed = 0
                            for _ in range(riders):
                                if front_queue:
                                    front_queue.pop(0)
                                    removed += 1
                                elif other_queue:
                                    other_queue.pop(0)
                                    removed += 1
                            messagebox.showinfo("Riders Removed", f"Successfully removed {removed} riders.")
                        update_dashboard()
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Please enter a valid number of riders.")

            rider_window = tk.Toplevel(main_app)
            rider_window.title("Add/Remove Riders")
            rider_window.geometry("300x200")

            tk.Label(rider_window, text="Enter number of riders to add/remove:", font=("Helvetica", 12)).pack(pady=10)

            rider_entry = tk.Entry(rider_window, font=("Helvetica", 12))
            rider_entry.pack(pady=10)

            rider_action = tk.StringVar(value="Add")
            add_radio = tk.Radiobutton(rider_window, text="Add Riders", variable=rider_action, value="Add", font=("Helvetica", 12))
            remove_radio = tk.Radiobutton(rider_window, text="Remove Riders", variable=rider_action, value="Remove", font=("Helvetica", 12))
            add_radio.pack(pady=5)
            remove_radio.pack(pady=5)

            adjust_button = tk.Button(rider_window, text="Adjust Riders", font=("Helvetica", 12), command=adjust_riders, bg="lightcoral", relief="raised", bd=4)
            adjust_button.pack(pady=10)

        def dispatch_ride():
            global ride_in_progress, ride_start_time
            if ride_in_progress:
                messagebox.showinfo("Ride in Progress", "A ride is already in progress. Please wait for it to finish.")
                return

            # Dispatch available riders
            riders_dispatching = min(riders_to_dispatch, len(front_queue) + len(other_queue))
            for _ in range(riders_dispatching):
                if front_queue:
                    front_queue.pop(0)
                elif other_queue:
                    other_queue.pop(0)

            if riders_dispatching > 0:
                ride_in_progress = True
                ride_start_time = time.time()
                messagebox.showinfo("Ride Dispatched", f"Ride has been dispatched with {riders_dispatching} riders.")
                update_dashboard()
            else:
                messagebox.showwarning("No Riders", "There are no riders available to dispatch.")

        dispatch_button = tk.Button(main_app, text="Dispatch Ride", command=dispatch_ride, bg="lightgreen", font=("Helvetica", 12), relief="raised", bd=4)
        dispatch_button.pack(pady=20)

        manual_override_button = tk.Button(main_app, text="Manual Override", command=manual_override, bg="lightcoral", font=("Helvetica", 12), relief="raised", bd=4)
        manual_override_button.pack(pady=20)

    update_dashboard()

# Login validation
def validate_login():
    global current_user_role
    username = username_entry.get()
    password = password_entry.get()
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
        current_user_role = USER_CREDENTIALS[username]["role"]
        messagebox.showinfo("Login Successful", f"Welcome, {username}! Role: {current_user_role}")
        login_window.destroy()
        show_main_application()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

root = tk.Tk()
root.title("Login Screen")

# Enable full screen
root.attributes('-fullscreen', True)

# Exit full screen with Escape key
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

root.bind('<Escape>', exit_fullscreen)

# Set background color
root.configure(bg="lightblue")

login_window = tk.Frame(root, relief="solid", borderwidth=2, padx=20, pady=20)
login_window.pack(pady=50)

title_label = tk.Label(login_window, text="Login to Shaman Queue Management System", font=("Helvetica", 16, "bold"), fg="darkblue")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

username_label = tk.Label(login_window, text="Username:", font=("Helvetica", 12))
username_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

username_entry = tk.Entry(login_window, font=("Helvetica", 12))
username_entry.grid(row=1, column=1, padx=10, pady=10)

password_label = tk.Label(login_window, text="Password:", font=("Helvetica", 12))
password_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

password_entry = tk.Entry(login_window, font=("Helvetica", 12), show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10)

login_button = tk.Button(login_window, text="Login", command=validate_login, bg="lightgreen", font=("Helvetica", 12), relief="raised", bd=4)
login_button.grid(row=3, column=0, columnspan=2, pady=20)

Thread(target=lambda: simulate_front_queue(), daemon=True).start()
Thread(target=lambda: simulate_other_queue(), daemon=True).start()

root.mainloop()
