import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from PIL import Image, ImageTk
import sqlite3
from database import create_database, update_game_in_database, insert_game_into_database, game_exists_in_database

def show_games(parent_window):
    parent_window.title("Game Settings")
    parent_window.attributes('-topmost', True)  # Make the window stay on top of other windows

    def on_save():
        for item in tree.get_children():
            game_id, game_name, game_executable, game_image, show_game = tree.item(item)['values']
            show_game = 1 if show_game == "Yes" else 0
            update_game_in_database(game_id, game_name, game_executable, game_image, show_game)
        parent_window.destroy()
        return True

    style = ttk.Style()
    style.theme_use("darkly")

    tree_frame = ttk.Frame(parent_window)
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Executable", "Image", "Show Game"), show="headings")
    tree.heading("ID", text="App ID")
    tree.heading("Name", text="Game Name")
    tree.heading("Executable", text="Executable Path")
    tree.heading("Image", text="Image")
    tree.heading("Show Game", text="Show Game")
    tree.pack(fill=BOTH, expand=True)

    font_size = 12
    style.configure("Treeview", font=("Arial", font_size), rowheight=int(font_size * 2.5))
    style.configure("Treeview.Heading", font=("Arial", font_size, "bold"))

    conn = sqlite3.connect("steam_games.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()
    conn.close()

    for game in games:
        game_id, game_name, game_executable, game_image, show_game = game
        show_game_text = "Yes" if show_game == 1 else "No"
        tree.insert("", END, values=(game_id, game_name, game_executable, game_image, show_game_text))

    def on_cell_edit(event):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if column == "#2":
            entry = ttk.Entry(tree_frame, width=40)
            entry.place(x=event.x, y=event.y, anchor=NW)
            entry.insert(0, tree.set(item, column))
            entry.focus()

            def on_enter(event):
                new_value = entry.get()
                tree.set(item, column, new_value)
                entry.destroy()

            entry.bind("<Return>", on_enter)
        elif column == "#3":
            executable_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
            if executable_path:
                tree.set(item, column, executable_path)
        elif column == "#4":
            image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
            if image_path:
                tree.set(item, column, image_path)
                image = Image.open(image_path)
                image.thumbnail((50, 50))
                photo = ImageTk.PhotoImage(image)
                tree.item(item, image=photo)
                tree.image = photo
        elif column == "#5":
            show_game = tree.set(item, column)
            if show_game == "Yes":
                tree.set(item, column, "No")
            else:
                tree.set(item, column, "Yes")

    tree.bind("<Double-1>", on_cell_edit)

    button_frame = ttk.Frame(parent_window)
    button_frame.pack(pady=10)

    save_button = ttk.Button(button_frame, text="Save", command=on_save, style="primary.TButton", width=20)
    save_button.pack()

    parent_window.mainloop()

    return False

