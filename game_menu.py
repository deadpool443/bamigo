import customtkinter as ctk
from PIL import Image
from steam import run_game
import logging
from database import retrieve_games
from customtkinter import CTkImage
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_grid_dimensions(num_games, screen_width, screen_height):
    aspect_ratio = screen_width / screen_height
    
    if aspect_ratio > 1:  # Horizontal display
        num_columns = min(num_games, 4)
        num_rows = math.ceil(num_games / num_columns)
    else:  # Vertical display
        num_rows = min(num_games, 4)
        num_columns = math.ceil(num_games / num_rows)
    
    logging.info(f"Calculated grid dimensions: {num_columns} columns, {num_rows} rows")
    return num_columns, num_rows

def calculate_tile_size(num_games, screen_width, screen_height, num_columns, num_rows, spacing_factor):
    available_width = screen_width - (num_columns + 1) * int(screen_width * spacing_factor)
    available_height = screen_height - (num_rows + 1) * int(screen_height * spacing_factor)

    if available_width < 0 or available_height < 0:
        logging.error("Screen size too small for the given number of tiles and spacing.")
        raise ValueError("Screen size too small for the given number of tiles and spacing.")

    ideal_aspect_ratio = 16 / 9
    tile_width = available_width // num_columns
    tile_height = int(tile_width / ideal_aspect_ratio)

    if tile_height * num_rows > available_height:
        tile_height = available_height // num_rows
        tile_width = int(tile_height * ideal_aspect_ratio)

    tile_width -= 20
    logging.info(f"Calculated tile size: {tile_width}x{tile_height}")
    return tile_width, tile_height

def create_grid_layout(window, games, num_columns, num_rows, tile_width, tile_height, spacing_x, spacing_y, credit_text, controls):
    buttons = []
    grid_layout = ctk.CTkFrame(window)
    grid_layout.pack(expand=True, fill='both')

    for i, game in enumerate(games):
        row = i // num_columns
        column = i % num_columns
        
        button = ctk.CTkButton(grid_layout, text=game[0], command=lambda game_name=game[0], app_id=game[1]: run_game(game_name, app_id, credit_text, controls, window),
                               width=tile_width, height=tile_height)
        button.grid(row=row, column=column, padx=spacing_x, pady=spacing_y)
        buttons.append(button)
        
        image_path = game[3]
        if image_path and image_path != 'None':
            try:
                image = Image.open(image_path)
                ctk_image = CTkImage(image, size=(tile_width, tile_height))
                button.configure(image=ctk_image, compound="top")
            except FileNotFoundError:
                logging.warning(f"Image file not found: {image_path}")
            except Exception as e:
                logging.exception(f"Failed to load image: {image_path}")
        else:
            logging.warning(f"No image found for game: {game[0]}")
    
    logging.info("Grid layout created successfully")
    return grid_layout, buttons

def on_key_press(event, buttons, selected_index, num_columns):
    selected_button_style = {
        "fg_color": "#ff306c",
        "hover_color": "#070630",
        "border_width": 2,
        "border_color": "white",
        "font": ("Arial", 16, "bold")
    }

    default_button_style = {
        "fg_color": ctk.ThemeManager.theme["CTkButton"]["fg_color"],
        "hover_color": ctk.ThemeManager.theme["CTkButton"]["hover_color"],
        "border_width": 0,
        "border_color": "",
    }

    previous_selected_index = selected_index

    if event.keysym == 'Up':
        selected_index = (selected_index - num_columns) % len(buttons)
    elif event.keysym == 'Down':
        selected_index = (selected_index + num_columns) % len(buttons)
    elif event.keysym == 'Left':
        selected_index = (selected_index - 1) % len(buttons)
    elif event.keysym == 'Right':
        selected_index = (selected_index + 1) % len(buttons)
    elif event.keysym == 'Return':
        logging.info(f"Game selected: {buttons[selected_index].cget('text')}")
        buttons[selected_index].invoke()
        return selected_index
    elif event.keysym == 'Escape':
        logging.info("Escape key pressed. Closing game menu.")
        window.destroy()
        return selected_index

    # Reset the style of the previously selected button
    buttons[previous_selected_index].configure(**default_button_style)

    # Apply the selected style to the new button
    buttons[selected_index].configure(**selected_button_style)

    buttons[selected_index].focus_set()
    logging.info(f"Button selected: {buttons[selected_index].cget('text')}")
    return selected_index

def display_game_menu(root, controls, credit_text):
    logging.info("Displaying game menu")
    games = retrieve_games()
    num_games = len(games)
    logging.info(f"Retrieved {num_games} games from the database")

    game_menu_frame = ctk.CTkFrame(root)
    game_menu_frame.pack(fill=ctk.BOTH, expand=True)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    logging.info(f"Screen dimensions: {screen_width}x{screen_height}")

    credits_frame_height = int(screen_height * 0.07)
    game_menu_height = screen_height - credits_frame_height

    num_columns, num_rows = calculate_grid_dimensions(num_games, screen_width, game_menu_height)

    spacing_factor = 0.01
    tile_width, tile_height = calculate_tile_size(num_games, screen_width, game_menu_height, num_columns, num_rows, spacing_factor)

    spacing_x = int(screen_width * spacing_factor)
    spacing_y = int(game_menu_height * spacing_factor)

    grid_layout, buttons = create_grid_layout(game_menu_frame, games, num_columns, num_rows, tile_width, tile_height, spacing_x, spacing_y, credit_text, controls)
    grid_layout.pack(fill=ctk.BOTH, expand=True)

    selected_index = 0
    if len(games) > 0:
        buttons[0].focus_set()
        logging.info(f"Initial button selected: {buttons[0].cget('text')}")

    def handle_key_press(event):
        nonlocal selected_index
        selected_index = on_key_press(event, buttons, selected_index, num_columns)

    root.bind('<KeyPress>', handle_key_press)

    logging.info("Game menu displayed")