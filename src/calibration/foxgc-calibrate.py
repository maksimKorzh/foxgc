###################################
#
#          Fox Go Cheater
#
#               by
#
#         Code Monkey King
#
###################################

# Packages
from tkinter import messagebox
from tkinter import ttk
import pyautogui as pg
import tkinter as tk
import threading
import json

###################################
#
#        AI control module
#
###################################

# Board mappings
cell_size = 32
offset_y = 56
offset_x = 164

# Side to move
side_to_move = 1

# Coordinates of vertices
set_square = {}

# Init square to coordinates array
def init_coords():
  global set_square
  set_square = {}
  x = offset_x
  y = offset_y
  for col in range(19):
    for row in range(19):
      square = row * 19 + col
      set_square.update({
        'ABCDEFGHJKLMNOPQRST'[row]+str(19-col):
        (int(x), int(y))
      })
      x += cell_size
    x = offset_x
    y += cell_size

# Convert screen to board coordinates
def locate_stone(color):
  try:
    path = 'fox-' + color + '.png'
    stone = pg.locateOnScreen(path)
    col = int((stone.left - offset_x) / cell_size)+1
    row = int((stone.top - offset_y) / cell_size)+1
    move = 'ABCDEFGHJKLMNOPQRST'[col] + str(19-row)
    return move
  except: return ''

# Move moise pointer to a given coord
def move_to():
  update_params()
  move = square_option.get()
  pg.moveTo(set_square[move])

# Calibrate screen coordinates
def calibrate():
  global cheater_running, side_to_move
  old_move = ''
  update_params()
  while cheater_running:
    color = 'black' if side_to_move else 'white'
    move = locate_stone(color)
    if move != '' and move != old_move:
      old_move = move
      pg.moveTo(set_square[move])
      side_to_move ^= 1

###################################
#
#       GUI control module
#
###################################

# Cheater thread
cheater_thread = None
cheater_running = False

# Close app
def on_window_close():
  stop_calibration()
  save_settings()
  root.destroy()

# Update recognition params
def update_params():
  try:
    global cell_size, offset_x, offset_y
    cell_size = int(cell_size_entry.get())
    offset_x = int(offset_x_entry.get())
    offset_y = int(offset_y_entry.get())
    init_coords()
  except:
    messagebox.showerror("Error", "Values should be integers")

# Load user settings
def load_settings():
  global cell_size, offset_x, offset_y
  try:
    with open('settings.json') as f:
      settings = json.loads(f.read())
      cell_size = settings['cell_size']
      offset_x = settings['offset_x']
      offset_y = settings['offset_y']
  except Exception as e: print(repr(e))

# Load user settings
def save_settings():
  update_params()
  with open('settings.json', 'w') as f:
    settings = {
      'cell_size': cell_size,
      'offset_x': offset_x,
      'offset_y': offset_y
    }
    f.write(json.dumps(settings, indent=2))

# Run calibration in background
def start_calibration():
  global cheater_thread, cheater_running
  if cheater_running: return
  cheater_running = True
  cheater_thread = threading.Thread(target=calibrate)
  cheater_thread.start()

# Stop calibration
def stop_calibration():
  global cheater_thread, cheater_running
  cheater_running = False
  if cheater_thread and cheater_thread.is_alive():
    cheater_thread.join()

# How to use
def help():
  messagebox.showinfo(
    'Fox Go Cheater is now running in calibration mode',
    'Below are the steps to follow to check whether Fox Go Cheater is tuned properly:\n\n' + 
    '1. Open Fox Go Server application\n' +
    '2. Open any game currently being played\n' +
    '3. Check whether mouse pointer is following moves\n\n' +
    'If so, you have configured Fox Go Cheater properly,\n' +
    'otherwise keep tuning the parameters.\n\n' +
    'Click "Stop calibration" before making any changes.'
  )

# Create UI
load_settings()
root = tk.Tk()
root.title('Fox Go Cheater')
root.iconphoto(True, tk.PhotoImage(file='foxwq.png'))
selected_square = tk.StringVar()
selected_square.set('A19')
square_option = ttk.Combobox(root, width=10, textvariable=selected_square, values=['A19', 'T19', 'A1', 'T1'], state='readonly')
square_option.grid(row=0, column=0, sticky='ew')
cell_size_entry = ttk.Entry(root, width=10)
cell_size_entry.grid(row=0, column=1, sticky='ew')
cell_size_entry.insert(0, str(cell_size))
offset_x_entry = ttk.Entry(root, width=10)
offset_x_entry.grid(row=0, column=2, sticky='ew')
offset_x_entry.insert(0, str(offset_x))
offset_y_entry = ttk.Entry(root, width=10)
offset_y_entry.grid(row=0, column=3, sticky='ew')
offset_y_entry.insert(0, str(offset_y))
move_to_button = ttk.Button(root, text='Check', command=move_to)
move_to_button.grid(row=1, column=0, sticky='ew')
calibrate_start_button = ttk.Button(root, text='Start', command=start_calibration)
calibrate_start_button.grid(row=1, column=1, sticky='ew')
calibrate_stop_button = ttk.Button(root, text='Stop', command=stop_calibration)
calibrate_stop_button.grid(row=1, column=2, sticky='ew')
help_button = ttk.Button(root, text='Help', command=help)
help_button.grid(row=1, column=3, sticky='ew')

# Run app
root.protocol("WM_DELETE_WINDOW", on_window_close)
root.resizable(False, False)
root.mainloop()
