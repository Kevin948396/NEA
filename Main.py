import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import math

global root 
# User credentials and roles
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
}


class QueueManager:
    def __init__(self):
        self.front_queue = []
        self.other_queue = []

    def simulate_front_queue(self, root):
        self.front_queue.append(1)  # Add a guest to the front queue
        root.after(6000, self.simulate_front_queue, root)  # Simulate arrival every 6 seconds

    def simulate_other_queue(self, root):
        self.other_queue.append(1)  # Add a guest to the other queue
        root.after(3000, self.simulate_other_queue, root)  # Simulate arrival every 3 seconds

    def calculate_queue_time(self):
        total_riders = len(self.front_queue) + len(self.other_queue)
        riders_per_minute = 1000 / 60  # 1000 riders per hour = 16.67 riders per minute
        estimated_time = total_riders / riders_per_minute
        return math.ceil(estimated_time)


class RideManager:
    def __init__(self):
        self.ride_in_progress = False
        self.ride_start_time = 0
        self.ride_duration = 120  # The duration of the ride in seconds (2 minutes)

    def dispatch_ride(self, front_queue, other_queue):
        if self.ride_in_progress:
            messagebox.showinfo("Ride in Progress", "A ride is already in progress. Please wait for it to finish.")
            return

        # Dispatch riders: max 2 from front queue and 26 from other queue
        riders_dispatched = 0
        for _ in range(2):  # Take up to 2 from front queue
            if front_queue:
                front_queue.pop(0)
                riders_dispatched += 1
        for _ in range(26):  # Take up to 26 from other queue
            if other_queue:
                other_queue.pop(0)
                riders_dispatched += 1

        if riders_dispatched > 0:
            self.ride_in_progress = True
            self.ride_start_time = time.time()
            messagebox.showinfo("Ride Dispatched", f"Ride has been dispatched with {riders_dispatched} riders.")
        else:
            messagebox.showwarning("No Riders", "Not enough riders to dispatch a ride.")

    def update_ride_status(self, remaining_time_label):
        if self.ride_in_progress:
            elapsed_time = time.time() - self.ride_start_time
            remaining_time = max(0, self.ride_duration - elapsed_time)
            remaining_time_label.config(text=f"Time Until Ride Finish: {round(remaining_time)} secs")
            if remaining_time <= 0:  # End ride
                self.ride_in_progress = False
                remaining_time_label.config(text="No Ride in Progress")
        else:
            remaining_time_label.config(text="No Ride in Progress")


class UserManager:
    def __init__(self):
        self.current_user_role = None

    def validate_login(self, username, password):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            self.current_user_role = USER_CREDENTIALS[username]["role"]
            return True
        return False


class Application:
    def __init__(self):
        self.queue_manager = QueueManager()
        self.ride_manager = RideManager()
        self.user_manager = UserManager()
        self.root = tk.Tk()
        self.root.title("Login Screen")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda _: self.root.attributes('-fullscreen', False))
        self.root.configure(bg="lightblue")
        self.login_window = None
        self.main_app = None
        self.username_entry = None
        self.password_entry = None

        Thread(target=self.queue_manager.simulate_front_queue, daemon=True, args=(self.root,)).start()
        Thread(target=self.queue_manager.simulate_other_queue, daemon=True, args=(self.root,)).start()

    def show_main_application(self):
        self.main_app = tk.Toplevel(self.root)
        self.main_app.title("Main Dashboard")
        self.main_app.geometry("600x400")
        self.main_app.configure(bg="lightblue")

        tk.Label(self.main_app, text="Queue Management Dashboard", font=("Helvetica", 16, "bold"), bg="lightblue").pack(pady=20)

        # Queue status display
        front_queue_label = tk.Label(self.main_app, text="Front Queue: 0 guests", font=("Helvetica", 12), bg="lightblue")
        front_queue_label.pack(pady=10)

        other_queue_label = tk.Label(self.main_app, text="Other Queue: 0 guests", font=("Helvetica", 12), bg="lightblue")
        other_queue_label.pack(pady=10)

        queue_time_label = tk.Label(self.main_app, text="Estimated Queue Time: 0 mins", font=("Helvetica", 12), bg="lightblue")
        queue_time_label.pack(pady=10)

        remaining_time_label = tk.Label(self.main_app, text="No Ride in Progress", font=("Helvetica", 12), bg="lightblue")
        remaining_time_label.pack(pady=10)

        def update_dashboard():
            # Update queue statistics
            front_queue_label.config(text=f"Front Queue: {len(self.queue_manager.front_queue)} guests")
            other_queue_label.config(text=f"Other Queue: {len(self.queue_manager.other_queue)} guests")
            queue_time_label.config(text=f"Estimated Queue Time: {self.queue_manager.calculate_queue_time()} mins")

            # Check if a ride should automatically dispatch
            if not self.ride_manager.ride_in_progress and len(self.queue_manager.front_queue) >= 2 and len(self.queue_manager.other_queue) >= 26:
                self.ride_manager.dispatch_ride(self.queue_manager.front_queue, self.queue_manager.other_queue)

            # Update ride status
            self.ride_manager.update_ride_status(remaining_time_label)

            self.main_app.after(1000, update_dashboard)  # Update dashboard every second

        # Admin-only manual override
        if self.user_manager.current_user_role == "admin":
            def manual_override():
                def adjust_riders():
                    action = rider_action.get()
                    try:
                        riders = int(rider_entry.get())
                        if riders < 1:
                            messagebox.showwarning("Invalid Input", "Enter a number greater than 0.")
                        else:
                            if action == "Add":
                                for _ in range(riders):
                                    self.queue_manager.front_queue.append(1)
                                    self.queue_manager.other_queue.append(1)
                            elif action == "Remove":
                                for _ in range(riders):
                                    if self.queue_manager.front_queue:
                                        self.queue_manager.front_queue.pop(0)
                                    elif self.queue_manager.other_queue:
                                        self.queue_manager.other_queue.pop(0)
                            update_dashboard()
                    except ValueError:
                        messagebox.showwarning("Invalid Input", "Enter a valid number of riders.")

                rider_window = tk.Toplevel(self.main_app)
                rider_window.title("Add/Remove Riders")
                rider_window.geometry("300x200")

                tk.Label(rider_window, text="Enter number of riders to add/remove:", font=("Helvetica", 12)).pack(pady=10)
                rider_entry = tk.Entry(rider_window, font=("Helvetica", 12))
                rider_entry.pack(pady=10)

                rider_action = tk.StringVar(value="Add")
                tk.Radiobutton(rider_window, text="Add Riders", variable=rider_action, value="Add", font=("Helvetica", 12)).pack(pady=5)
                tk.Radiobutton(rider_window, text="Remove Riders", variable=rider_action, value="Remove", font=("Helvetica", 12)).pack(pady=5)

                tk.Button(rider_window, text="Adjust Riders", command=adjust_riders, font=("Helvetica", 12), bg="lightcoral").pack(pady=10)

            tk.Button(self.main_app, text="Manual Override", command=manual_override, font=("Helvetica", 12), bg="lightcoral").pack(pady=20)
            tk.Button(self.main_app, text="Manual Dispatch", command=lambda: self.ride_manager.dispatch_ride(self.queue_manager.front_queue, self.queue_manager.other_queue), font=("Helvetica", 12), bg="lightgreen").pack(pady=20)

        update_dashboard()

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_manager.validate_login(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}! Role: {self.user_manager.current_user_role}")
            self.login_window.destroy()
            self.show_main_application()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def start(self):
        self.login_window = tk.Frame(self.root, relief="solid", borderwidth=2, padx=20, pady=20)
        self.login_window.pack(pady=50)

        tk.Label(self.login_window, text="Login to Queue Management System", font=("Helvetica", 16, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.login_window, text="Username:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.username_entry = tk.Entry(self.login_window, font=("Helvetica", 12))
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.login_window, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.password_entry = tk.Entry(self.login_window, font=("Helvetica", 12), show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.login_window, text="Login", command=self.validate_login, bg="lightgreen", font=("Helvetica", 12)).grid(row=3, column=0, columnspan=2, pady=20)

        self.root.mainloop()


# Run the application
app = Application()
app.start()
