import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import json
from cryptography.fernet import Fernet, InvalidToken

MASTER_PASSWORD = "admin123"
NOTES_FILE = "encrypted_notes.json"

if not os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, 'w') as f:
        json.dump({}, f)

class EncryptedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Notepad")
        self.notes = self.load_notes()
        self.current_note_title = None
        self.current_note_key = None
        self.current_note_password = None

        # login screen
        self.login_frame = tk.Frame(root)
        tk.Label(self.login_frame, text="Enter Master Password").pack(pady=5)
        self.pass_entry = tk.Entry(self.login_frame, show="*")
        self.pass_entry.pack()
        self.pass_entry.bind('<Return>', lambda event: self.check_password())
        tk.Button(self.login_frame, text="Login", command=self.check_password).pack(pady=10)
        self.login_frame.pack(padx=10, pady=10)

        # main interface
        self.main_frame = tk.Frame(root)
        self.left_panel = tk.Frame(self.main_frame)
        self.right_panel = tk.Frame(self.main_frame)

        tk.Button(self.left_panel, text="Create New Note", command=self.create_note).pack(pady=5)

        self.delete_button = tk.Button(self.left_panel, text="Delete Note", command=self.delete_note)
        self.delete_button.pack(pady=5)
        self.delete_button.pack_forget() # hide

        self.notes_listbox = tk.Listbox(self.left_panel, width=30)
        self.notes_listbox.pack(fill=tk.Y, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self.open_note)

        self.note_text = tk.Text(self.right_panel)
        self.note_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.save_button = tk.Button(self.right_panel, text="Save Changes", command=self.save_changes)
        self.save_button.pack(pady=5)
        self.save_button.pack_forget() # hide

        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def check_password(self):
        if self.pass_entry.get() == MASTER_PASSWORD:
            self.login_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            self.refresh_notes_list()
        else:
            messagebox.showerror("Error", "Wrong password!")

    def revert_selection(self):
        if self.current_note_title:
            index = list(self.notes.keys()).index(self.current_note_title)
            self.notes_listbox.selection_clear(0, tk.END)
            self.notes_listbox.selection_set(index)
        else:
            self.notes_listbox.selection_clear(0, tk.END)

    def load_notes(self):
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)

    def save_notes(self):
        with open(NOTES_FILE, 'w') as f:
            json.dump(self.notes, f)

    def refresh_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        for title in self.notes:
            self.notes_listbox.insert(tk.END, title)

    def create_note(self):
        def save_new_note():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            password = password_entry.get().strip()

            if not title or not password:
                messagebox.showerror("Error", "Title and password are required.")
                return
            if title in self.notes:
                messagebox.showerror("Error", "Note with this title already exists.")
                return

            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted_content = cipher.encrypt(content.encode()).decode()

            self.notes[title] = {
                "key": key.decode(),
                "content": encrypted_content,
                "password": password
            }
            self.save_notes()
            self.refresh_notes_list()
            create_window.destroy()

        create_window = tk.Toplevel(self.root)
        create_window.title("Create New Note")
        create_window.geometry("400x300")

        tk.Label(create_window, text="Title").pack(pady=2)
        title_entry = tk.Entry(create_window)
        title_entry.pack(fill=tk.X, padx=10)

        tk.Label(create_window, text="Content").pack(pady=2)
        content_text = tk.Text(create_window, height=8)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Label(create_window, text="Password").pack(pady=2)
        password_entry = tk.Entry(create_window, show="*")
        password_entry.pack(fill=tk.X, padx=10)

        tk.Button(create_window, text="Create Note", command=save_new_note).pack(pady=10)

    def open_note(self, event):
        selected = self.notes_listbox.curselection()
        if not selected:
            return

        title = self.notes_listbox.get(selected)
        password = simpledialog.askstring("Password", f"Enter password for '{title}':", show="*")

        if password is None:
            self.revert_selection()
            return

        note = self.notes[title]

        if password == note["password"]:
            try:
                cipher = Fernet(note["key"].encode())
                content = cipher.decrypt(note["content"].encode()).decode()
                self.note_text.delete(1.0, tk.END)
                self.note_text.insert(tk.END, content)

                self.current_note_title = title
                self.current_note_key = note["key"]
                self.current_note_password = note["password"]

                self.save_button.pack()
                self.delete_button.pack()

            except InvalidToken:
                messagebox.showerror("Error", "Failed to decrypt note.")
        else:
            messagebox.showerror("Error", "Incorrect password!")
            self.revert_selection()

    def save_changes(self):
        if not self.current_note_title or not self.current_note_key:
            return

        content = self.note_text.get(1.0, tk.END).strip()
        cipher = Fernet(self.current_note_key.encode())
        encrypted_content = cipher.encrypt(content.encode()).decode()

        self.notes[self.current_note_title] = {
            "key": self.current_note_key,
            "content": encrypted_content,
            "password": self.current_note_password
        }
        self.save_notes()
        messagebox.showinfo("Saved", f"Changes to '{self.current_note_title}' saved.")

    def delete_note(self):
        selected = self.notes_listbox.curselection()
        if not selected:
            return
        title = self.notes_listbox.get(selected)

        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete '{title}'?")
        if confirm:
            del self.notes[title]
            self.save_notes()
            self.refresh_notes_list()
            self.note_text.delete(1.0, tk.END)

            self.save_button.pack_forget()
            self.delete_button.pack_forget()

            self.current_note_title = None
            self.current_note_key = None
            self.current_note_password = None

if __name__ == '__main__':
    root = tk.Tk()
    app = EncryptedNotepad(root)
    root.mainloop()