import tkinter as tk
from tkinter import ttk, messagebox
import json
from ttkbootstrap import Style

# --- Helper functions ---

def save_all_notes_to_file(notes):
    try:
        with open("notes.json", "w") as f:
            # ensure_ascii=False, for Polish characters
            json.dump(notes, f, indent=4, ensure_ascii=False) 
        return True
    except Exception as e:
        messagebox.showerror("Saving error", f"Failed to save: {e}")
        return False
    
def get_next_id(notes):
    if not notes:
        return "1"
    try:
        max_id = max(int(k) for k in notes.keys())
        return str(max_id + 1)
    except ValueError:
        return "1"
    
def get_current_tab():
    tab_id = notebook.select()
    current_tab_frame = notebook.nametowidget(tab_id)

    title_entry_widget = None
    content_text_widget = None

    for widget in current_tab_frame.winfo_children():
        if isinstance(widget, tk.Entry) and getattr(widget, 'is_title_field', False):
            title_entry_widget = widget
        elif isinstance(widget, tk.Text) and getattr(widget, 'is_content_field', False):
            content_text_widget = widget

    current_title = notebook.tab(tab_id, "text")
    current_id = getattr(current_tab_frame, "note_id", None)
    
    return tab_id, current_tab_frame, title_entry_widget, content_text_widget, current_title, current_id

# --- Main functions ---

def load_notes():    
    for note_id, note_data in notes.items():
        title = note_data.get("title", f"No title (ID: {note_id})")
        content = note_data.get("content", "")

        note_frame = ttk.Frame(notebook, padding=5)
        note_frame.note_id = note_id

        title_entry = ttk.Entry(note_frame, font=("TkDefaultFont", 12, "bold"))
        title_entry.insert(0, title)
        title_entry.pack(fill=tk.X, pady=(0, 5))
        title_entry.is_title_field = True # for get_current_tab
        
        scrollbar = ttk.Scrollbar(note_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        note_content_text = tk.Text(note_frame, width=40, height=10, 
                                    yscrollcommand=scrollbar.set, wrap=tk.WORD)
        note_content_text.insert(tk.END, content)
        note_content_text.pack(fill=tk.BOTH, expand=True)
        note_content_text.is_content_field = True # for get_current_tab

        scrollbar.config(command=note_content_text.yview)

        notebook.add(note_frame, text=title)

def add_note():
    new_id = get_next_id(notes)
    title = f"New Note ({new_id})"

    note_frame = ttk.Frame(notebook, padding=5)
    note_frame.note_id = new_id

    title_entry = ttk.Entry(note_frame, font=("TkDefaultFont", 12, "bold"))
    title_entry.insert(0, title)
    title_entry.pack(fill=tk.X, pady=(0, 5))
    title_entry.is_title_field = True

    scrollbar = ttk.Scrollbar(note_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    content_entry = tk.Text(note_frame, width=40, height=10, 
                            yscrollcommand=scrollbar.set, wrap=tk.WORD)
    content_entry.pack(fill=tk.BOTH, expand=True)
    content_entry.is_content_field = True
    
    scrollbar.config(command=content_entry.yview)

    notebook.add(note_frame, text=title)
    notebook.select(note_frame)

    notes[new_id] = {"title": title, "content": ""}
    save_all_notes_to_file(notes)


def delete_note():
    tab_id, current_tab_frame, title_entry, content_text, current_title, current_id = get_current_tab()

    if current_id is None:
        messagebox.showwarning("Warning", 
                             "This tab hasn't been saved yet. Use 'X' to close it, or save it first.")
        return

    confirm = messagebox.askyesno("Delete note",
                                  f"Are you sure you want to delete '{current_title}'?")
    
    if confirm:
        notebook.forget(tab_id)

        try:
            notes.pop(current_id)

            if save_all_notes_to_file(notes):
                messagebox.showinfo("Success", f"Note '{current_title}' deleted.")
        
        except KeyError:
            messagebox.showerror("Error", 
                                 f"Note with ID {current_id} not found in data file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during deletion: {e}")

def save_current_note():
    tab_id, current_tab_frame, title_entry, content_text, _, current_id = get_current_tab()

    if not current_id:
        messagebox.showwarning("Warning", "Please select or create a note first.")
        return
    
    new_title = title_entry.get().strip() if title_entry else "Untitled Note"
    
    content = content_text.get("1.0",tk.END).strip() if content_text else ""

    if not new_title:
        messagebox.showwarning("Warning", "Note title cannot be empty.")
        return
        
    if not content and len(new_title) < 5:
        messagebox.showwarning("Warning", "Note content cannot be empty.")
        return

    notes[current_id] = {
        "title": new_title,
        "content": content
    }

    if save_all_notes_to_file(notes):
        notebook.tab(tab_id, text=new_title) 
        messagebox.showinfo("Updated", f"Note '{new_title}' (ID: {current_id}) saved successfully.")

# --- Configuration and global data ---

root = tk.Tk()
root.title("Ptak Note")
root.geometry("600x600")
style = Style(theme="journal")
style.configure("TNotebook.Tab", font=("TkDefaultFont", 11, "bold")) 

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Load saved notes
notes = {}
try:
    with open("notes.json", "r") as f:
        notes = json.load(f)
except FileNotFoundError:
    pass


# Add buttons to the main window
new_button = ttk.Button(root, text="New note",
                        command=add_note, style="info.TButton")
new_button.pack(side=tk.LEFT, padx=10, pady=10)

delete_button = ttk.Button(root, text="Delete note",
                            command=delete_note, style="primary.TButton")
delete_button.pack(side=tk.LEFT, padx=10, pady=10)

update_button = ttk.Button(root, text="Update/save note",
                            command=save_current_note, style="success.TButton")
update_button.pack(side=tk.LEFT, padx=10, pady=10)

load_notes()

root.mainloop()