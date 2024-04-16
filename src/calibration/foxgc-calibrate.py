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

# Side to move (1 black, 0 white)
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
    col = int((stone.left - offset_x) / cell_size)
    row = int((stone.top - offset_y) / cell_size)
    if stone.left - offset_x > 0: col += 1
    if stone.top - offset_y > 0: row += 1
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
    global offset_x, offset_y
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
      offset_x = settings['offset_x']
      offset_y = settings['offset_y']
  except Exception as e: print(repr(e))

# Load user settings
def save_settings():
  update_params()
  with open('settings.json', 'w') as f:
    settings = {
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
  root.title('Fox Go Calibrate (Match)')

# Stop calibration
def stop_calibration():
  global cheater_thread, cheater_running, side_to_move
  side_to_move = 1
  cheater_running = False
  if cheater_thread and cheater_thread.is_alive():
    cheater_thread.join()
    root.title('Fox Go Calibrate (Idle)')

# How to use
def help():
  messagebox.showinfo(
    'Fox Go Calibrate',
    'Fox Go Cheater is an application that uses optical board recognition ' +
    'to synchronize Fox Go application\'s board position with AI\'s one, therefore ' +
    'we need to make sure that the absolute screen X, Y corrdinates, corresponding to ' +
    'board vertices perfectly match with Fox Go Cheater\'s internal values.\n\n' +
    '1366x768 is recommended screen resolution, default offsets should work with it "as is". ' +
    'If you have higher resolution make sure to minimize Fox Go app window, ' +
    'and adjust X, Y offsets (defaults are: X = 164, Y = 56). ' +
    'Stone width should be equal to 32 pixels, you can screenshot Fox Go server app board ' +
    ' and use MS Paint to check the stone size. ' +
    'If stone size has any other value Fox Go Cheater would not work.\n\n' +
    'To calibrate Fox Go Cheater move its window somewhere to the right so that it does not ' +
    'overlap the board, open Fox Go server application, open any game that has ended, ' +
    'navigate to move 1 so that you see empty board, ' +
    'then click "Check" button. When "A19" corner is selected ' +
    'mouse pointer should move to board top left corner. Choose "T19", "A1" and "T1" ' +
    'to check top right, bottom left and bottom right corners respectively.\n\n' +
    'If mouse pointer perfectly lands on corresponding square points you can click ' +
    '"start" button and click "next move" in Fox Go server app - ' +
    'mouse pointer should automatically move to the last move being made on board. ' +
    'If you can see mouse pointer perfectly following moves every time you ' +
    'click "next move" button you may close this tool and start playing on Fox using AI.'
  )

# Create UI
load_settings()
root = tk.Tk()
root.title('Fox Go Calibrate (Idle)')
root.iconbitmap('foxwq.ico')
selected_square = tk.StringVar()
selected_square.set('A19')
square_option = ttk.Combobox(root, width=10, textvariable=selected_square, values=['A19', 'T19', 'A1', 'T1'], state='readonly')
square_option.grid(row=0, column=0, sticky='ew')
offset_x_entry = ttk.Entry(root, width=10)
offset_x_entry.grid(row=0, column=1, sticky='ew')
offset_x_entry.insert(0, str(offset_x))
offset_y_entry = ttk.Entry(root, width=10)
offset_y_entry.grid(row=0, column=2, sticky='ew')
offset_y_entry.insert(0, str(offset_y))
move_to_button = ttk.Button(root, text='Check', command=move_to)
move_to_button.grid(row=1, column=0, sticky='ew')
calibrate_start_button = ttk.Button(root, text='Start', command=start_calibration)
calibrate_start_button.grid(row=1, column=1, sticky='ew')
calibrate_stop_button = ttk.Button(root, text='Stop', command=stop_calibration)
calibrate_stop_button.grid(row=1, column=2, sticky='ew')

# Run app
root.protocol("WM_DELETE_WINDOW", on_window_close)
root.resizable(False, False)
root.attributes("-topmost", True)
help()
root.mainloop()
