import threading
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
import time
from PIL import Image, ImageTk  # Make sure to install Pillow for image handling

# MySQL connection setup
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="0000",  # Replace with your MySQL password
        database="taskreminder"  # Replace with your database name
    )

# Database initialization
def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            datetime DATETIME,
            status ENUM('pending', 'completed') DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

# Background thread to check for reminders
def reminder_notifier():
    while True:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, datetime FROM reminders WHERE status='pending'")
        reminders = cursor.fetchall()

        for reminder in reminders:
            reminder_time = reminder[2]
            if datetime.now() >= reminder_time:
                messagebox.showinfo("Reminder Notification", f"Reminder: {reminder[1]}")
                cursor.execute("UPDATE reminders SET status='completed' WHERE id=%s", (reminder[0],))
                conn.commit()

        conn.close()
        time.sleep(10)  # Check every 10 seconds

# GUI Application class
class TaskReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Reminder App")
        self.root.geometry("1200x600")
        

        # Load background image
        self.background_image = ImageTk.PhotoImage(file="background.png")  # Replace with your image path
        background_label = tk.Label(root, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        # Main Buttons
        tk.Button(root, text="Add Reminder", command=self.add_reminder_window,bg="white",width=50).place(x=100,y=200)
        tk.Button(root, text="View Reminders", command=self.view_reminders_window,bg="white",width=50).place(x=100,y=260)
        tk.Button(root, text="Exit", command=root.quit,bg="white",width=25).place(x=180,y=320)

    def add_reminder_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Reminder")
        add_window.geometry("1200x600")
      

        # Load background image
        background_label = tk.Label(add_window, image=self.background_image)
        background_label.pack()
        header_label = tk.Label(add_window, text="Add a New Reminder", font=("Helvetica", 16, "bold"))
        header_label.place(x=550, y=60)

        tk.Label(add_window, text="Title:").place(x=100,y=200)
        title_entry = tk.Entry(add_window)
        title_entry.place(x=150,y=200)

        tk.Label(add_window, text="Description:").place(x=60,y=230)
        desc_entry = tk.Entry(add_window)
        desc_entry.place(x=150,y=230)

        tk.Label(add_window, text="Date & Time (YYYY-MM-DD HH:MM:SS):").place(x=70,y=270)
        datetime_entry = tk.Entry(add_window)
        datetime_entry.place(x=100,y= 320)
        # ttk.Label(add_window, text='Choose date').place(x=50, y=400)
        # cal = DateEntry(add_window, width=12, background='darkblue',foreground='white', borderwidth=2, year=2010)
        # cal.place(x=50, y=400)

        # cal = DateEntry(add_window, width=12, background='darkblue',foreground='white', borderwidth=2, year=2010)
        # cal.pack(padx=10, pady=10)
        def save_reminder():
            title = title_entry.get()
            description = desc_entry.get()
            datetime_str = datetime_entry.get()

            try:
                reminder_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO reminders (title, description, datetime) VALUES (%s, %s, %s)",
                               (title, description, reminder_time))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Reminder added successfully!")
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid date/time format. Please use YYYY-MM-DD HH:MM:SS.")

        tk.Button(add_window, text="Save", command=save_reminder,width=20).place(x=100,y=360)

    def view_reminders_window(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("View Reminders")
        view_window.geometry("500x500")

        # Load background image
        background_label = tk.Label(view_window, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        self.tree = ttk.Treeview(view_window, columns=("ID", "Title", "Date & Time", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Date & Time", text="Date & Time")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True)
        def load_reminders():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, datetime, status FROM reminders")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()
       
       

        def delete_reminder():
            selected_item = self.tree.selection()
            if selected_item:
                reminder_id = self.tree.item(selected_item[0], "values")[0]
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reminders WHERE id=%s", (reminder_id,))
                conn.commit()
                conn.close()
                self.tree.delete(selected_item)
        load_reminders()
        tk.Button(view_window, text="Delete Selected", command=delete_reminder).pack(pady=10)
        tk.Button(view_window, text="Edit Selected", command=self.edit_reminder).pack(pady=10)        



   
       
            
        
    def edit_reminder(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a reminder to edit.")
            return

        global reminder_id
        reminder_id = self.tree.item(selected_item[0], "values")[0]
        current_title = self.tree.item(selected_item[0], "values")[1]
        global title_entry
        global datetime_entry
        current_datetime = self.tree.item(selected_item[0], "values")[2]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Reminder")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Edit Reminder", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(edit_window, text="Title:").pack(pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.insert(0, current_title)
        title_entry.pack(pady=5)

        tk.Label(edit_window, text="Date & Time (YYYY-MM-DD HH:MM:SS):").pack(pady=5)
        datetime_entry = tk.Entry(edit_window)
        datetime_entry.insert(0, current_datetime)
        
        datetime_entry.pack(pady=5)
        tk.Button(edit_window, text="Save Changes", command=self.save_changes).place(x=15,y=16)
        

    def save_changes(self):
           
            date=datetime_entry.get()

            try:
                        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        conn = connect_db()
                        cursor = conn.cursor()

                        cursor.execute("UPDATE reminders SET status='pending',  title=%s, datetime=%s WHERE id=%s",
                                    (title_entry.get(),date, reminder_id))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Reminder updated successfully!")
                        edit_window.destroy()
                        # Refresh the reminders in the view window
                        self.load_reminders()  # Assuming you have a method to refresh the view
            except ValueError:
                        messagebox.showerror("Error", "Invalid date/time format. Please use YYYY-MM-DD HH:MM:SS.")


# Main Application Execution
if __name__ == "__main__":
    initialize_db()

    root = tk.Tk()
    app = TaskReminderApp(root)
    root.resizable(0,0)
    # Start the reminder notifier in a separate thread
    notifier_thread = threading.Thread(target=reminder_notifier, daemon=True)
    notifier_thread.start()

    root.mainloop()    