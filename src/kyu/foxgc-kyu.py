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
import wexpect
import json
import sys

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
    col = int((stone.left - offset_x) / cell_size)
    row = int((stone.top - offset_y) / cell_size)
    if stone.left - offset_x > 0: col += 1
    if stone.top - offset_y > 0: row += 1
    move = 'ABCDEFGHJKLMNOPQRST'[col] + str(19-row)
    return move
  except: return ''

# Init engine
def init_engine():
  c = wexpect.spawn('gnugo.bat')
  init_commands = [
    'name',
    'version',
    'protocol_version',
    'komi 7.5',
    'boardsize 19',
    'clear_board'
  ]
  for command in init_commands:
    c.sendline(command)
    c.expect('= (.*)', timeout=-1)
    print(command + '\n' + c.after.strip())
  return c

# Play move
def play_move(c, move, color):
  c.sendline('play ' + color[0].upper() + ' ' + move)
  try: c.expect('= (.*)', timeout=-1)
  except: pass

# Generate engine move
def genmove(c, side_to_move):
  c.sendline('reg_genmove ' + ('B' if side_to_move else 'W'))
  try: c.expect('= (.*)', timeout=-1)
  except: return genmove(c, side_to_move)
  best_move = c.after.split()[-1]
  if len(best_move) < 2:
    return genmove(c, side_to_move)
  return best_move

# Engine plays game
def play_game():
  global side_to_move
  init_coords()
  c = init_engine()
  move_count = 0
  try: move_gen = int(selected_move.get())
  except: move_gen = 1
  move_start = move_gen if side_to_move else move_gen+1
  side_to_move = 0
  old_move = ''
  while cheater_running:
    color = 'white' if side_to_move else 'black'
    engine_color = 'black' if side_to_move else 'white'
    move = ''
    move = locate_stone(color)
    if move_start == 1 and move_count == 0:
       side_to_move = 1
       move_count += 1
       best_move = genmove(c, side_to_move)
       play_move(c, best_move, engine_color)
       print(' Generated move:', best_move)
       pg.moveTo(set_square[best_move])
       pg.click()
    if move == '' or move == old_move: continue
    try:
      play_move(c, move, color)
      old_move = move
      print(' Parsed move:', move)
      pg.moveTo(set_square[move])
      move_count = move_count + 1
      if move_count == 1 and move_gen == 1: move_count += 1
      if move_count >= move_start:
        best_move = genmove(c, side_to_move)
        play_move(c, best_move, engine_color)
        print(' Generated move:', best_move)
        pg.moveTo(set_square[best_move])
        pg.click()
      else: side_to_move ^= 1
    except:
      if best_move == 'PASS': messagebox.showinfo('Fox Go Cheater [6K]', 'AI has passed')
      else: messagebox.showinfo('Fox Go Cheater', 'AI has resigned')

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
  stop_playing()
  root.destroy()

# Load user settings
def load_settings():
  global cell_size, offset_x, offset_y
  try:
    with open('settings.json') as f:
      settings = json.loads(f.read())
      offset_x = settings['offset_x']
      offset_y = settings['offset_y']
  except:
    messagebox.showerror('Error', 'File "settings.json" is not found, run "foxgc-calibrate.exe" first.')
    sys.exit(1)

# Run calibration in background
def start_playing(side):
  global cheater_thread, cheater_running, side_to_move
  side_to_move = side
  if cheater_running: return
  cheater_running = True
  cheater_thread = threading.Thread(target=play_game)
  cheater_thread.start()
  root.title('Fox Go Cheater [6K] (Match)')

# Stop calibration
def stop_playing():
  global cheater_thread, cheater_running
  cheater_running = False
  if cheater_thread and cheater_thread.is_alive():
    cheater_thread.join()
    root.title('Fox Go Cheater [6K] (Idle)')

# How to use
def help():
  messagebox.showinfo(
    'Fox Go Cheater [6K]',
    'Open Fox Go app, start a game and click "Play Black" or "Play White" ' +
    'depending on which color you play. Click "Stop" to continue playing on your own.\n\n'
    'If you want to input some opening moves change the value of the option box ' +
    'to specify the move after which AI would jump in.\n\n' +
    'Wait until Fox Go Cheater recognizes the last move played, otherwise ' +
    'sync would be broken and AI would fail to play.'
  )

# Create UI
load_settings()
root = tk.Tk()
root.title('Fox Go Cheater [6K] (Idle)')
root.iconbitmap('foxwq.ico')
selected_move = tk.StringVar()
move_start_option = ttk.Combobox(root, width=2, textvariable=selected_move, values=['1', '2', '4', '6', '8', '10', '12'])
move_start_option.grid(row=0, column=0)
selected_move.set('1')
play_black_button = ttk.Button(root, width=15, text='Play Black', command=lambda: start_playing(1))
play_black_button.grid(row=0, column=1, sticky='ew')
play_white_button = ttk.Button(root, width=15, text='Play White', command=lambda: start_playing(0))
play_white_button.grid(row=0, column=2, sticky='ew')
stop_button = ttk.Button(root, width=15, text='Stop', command=stop_playing)
stop_button.grid(row=0, column=3, sticky='ew')

# Run app
root.protocol("WM_DELETE_WINDOW", on_window_close)
root.resizable(False, False)
root.attributes('-topmost', True)
help()
root.mainloop()
