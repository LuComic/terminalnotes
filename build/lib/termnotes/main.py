#!/usr/bin/env python3

from datetime import datetime
import os
import shutil
import appdirs
import readline
import pyperclip
import json

def load_theme_color():
    """Load the theme color from the config file."""
    if os.path.exists(CONFIG_FILE):  # Check if file exists
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("theme_color", 39)  # Default if not found
    return 39  # Return default if file doesn't exist

# Function to check if name already exists
def check_name(name):
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f]
  found_notes = []
  
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt") and name in f]
      found_notes.extend([(folder, note) for note in notes])

  if not found_notes and not found_folders:
    return True
  return False

# Get the system-specific Notes folder
BASE_DIR = appdirs.user_data_dir("Termnotes", "Termnotes")
CONFIG_FILE = "config.json"
auto_complete_names = ["skibidi"]
in_folder = None  # Tracks current folder
theme_color = load_theme_color()

# Autocomplete for names
class MyCompleter(object):  # Custom completer

  def __init__(self, options):
    self.update_options(options)

  def update_options(self, options):
    """Update the options and re-sort them."""
    self.options = sorted(options)

  def complete(self, text, state):
    if state == 0:  # On first trigger, build possible matches
      if text:  # Cache matches (entries that start with entered text)
        self.matches = [s for s in self.options if s and s.startswith(text)]
      else:  # No text entered, all matches possible
        self.matches = self.options[:]

      # Return match indexed by state
      try: 
        return self.matches[state]
      except IndexError:
        return None

# Initialize the completer
completer = MyCompleter(auto_complete_names)
readline.set_completer(completer.complete)
readline.parse_and_bind('tab: complete')

# Now, to update the completer when auto_complete_names changes:
def update_completer():
  global completer
  completer.update_options(auto_complete_names)

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

def setup():
  """Ensures the base Notes directory exists."""
  if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def list_folders():
  """Lists all folders inside the Notes directory."""
  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
  global theme_color

  print(f"\n\033[1;{theme_color}mFolders:\033[0m")

  if not folders:
    print(f"└── Create a folder with 'nf name'\n")  # Last folder gets a different symbol
    return

  for i, folder in enumerate(folders):
    if i == len(folders) - 1:  # Last item in the list
      print(f"└── {folder} (f)\n")  # Last folder gets a different symbol
    else:
      print(f"├── {folder} (f)")

def list_notes(folder):
  """Lists all notes inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  global theme_color
  if not os.path.exists(folder_path):
    print("\n\033[31mFolder not found.\033[0m\n")
    return
  
  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]

  print(f"\n\033[1;{theme_color}m{folder}:\033[0m")

  if not notes:
    print(f"└── Create a note with 'nn name'\n")  # Last folder gets a different symbol
    return

  for i, note in enumerate(notes):
    if i == len(notes) - 1:
      print(f"└── {note} (n)\n")  # Last note
    else:
      print(f"├── {note} (n)")

def create_folder(name):
  """Creates a new folder inside Notes."""
  folder_path = os.path.join(BASE_DIR, name)
  global auto_complete_names
  if check_name(name):
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n\033[32mNew folder '{name}' created.\033[0m\n")
    auto_complete_names.append(name)  # Add folder name to the autocomplete list
    update_completer()
  else:
    print("\n\033[31mThere's already a file with that name.\033[0m\n")


def create_note(folder, name, content):
  """Creates a new note inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  global auto_complete_names

  if not os.path.exists(folder_path):
    print("\n\033[31mFolder not found. Create the folder first.\033[0m\n")
    return

  if check_name(name):
    auto_complete_names.append(name)  # Add note name to autocomplete
    update_completer()
    note_path = os.path.join(folder_path, f"{name}.txt")
    with open(note_path, "w") as file:
      file.write(content)
    print(f"\n\033[32mNew note '{name}' created in '{folder}'.\033[0m\n")
  else:
    print("\n\033[31mThere's already a file with that name.\033[0m\n")

def search(name):
  """Searches for a folder or note and prompts the user to open its containing folder."""
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f]
  found_notes = []
  global in_folder
  global theme_color
  
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt") and name in f]
      found_notes.extend([(folder, note) for note in notes])
  
  if not found_folders and not found_notes:
    print("\n\033[31mNo matching folders or notes found.\033[0m\n")
    return
  
  print(f"\n\033[1;{theme_color}mSearch Results:\033[0m")
  
  for folder in found_folders:
    print(f"├── {folder} (f)")
  
  for folder, note in found_notes:
    print(f"└── {folder}/{note} (n)")
    
  print("\nType the folder name to open it or 'c' to cancel:")
  choice = input(f"\033[1;{theme_color}mFolder: \033[0m").strip()

  if os.path.exists(os.path.join(BASE_DIR, choice)):
    in_folder = choice
    list_notes(choice)
  elif choice.lower() == "c":
    print("\n\033[31mSearch canceled.\033[0m\n")
  else:
    print("\n\033[31mInvalid choice.\033[0m\n")

def read_note(folder, name):
  """Reads and displays a note."""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.txt")
  if not os.path.exists(note_path):
    print("\n\033[31mNote not found.\033[0m\n")
    return

  with open(note_path, "r") as file:
    content = file.read()
  
  print(f"\n--- {name} ---\n\n{content}")

def delete_note_or_folder(name, is_folder):
  """Deletes a note or folder."""
  path = os.path.join(BASE_DIR, name)
  global auto_complete_names
  
  if is_folder:
    if os.path.exists(path) and os.path.isdir(path):
      if name in auto_complete_names:
          auto_complete_names.remove(name)
          update_completer()
      shutil.rmtree(path)
      print(f"\n\033[32mFolder '{name}' deleted.\033[0m\n")
    else:
      print("\n\033[31mFolder not found.\033[0m\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".txt")
    if os.path.exists(note_path):
      if name in auto_complete_names:
        auto_complete_names.remove(name)
        update_completer()
      os.remove(note_path)
      print(f"\n\033[32mNote '{name}' deleted.\033[0m\n")
    else:
      print("\n\033[31mNote not found.\033[0m\n")

def edit_note_or_folder(name):
  """Edits a note (rename and modify content) or renames a folder."""
  global in_folder
  global theme_color
  global auto_complete_names

  if in_folder:  # Editing a note
    note_path = os.path.join(BASE_DIR, in_folder, f"{name}.txt")

    if not os.path.exists(note_path):
      print("\n\033[31mNote not found.\033[0m\n")
      return

    # Step 1: Rename the note (optional)
    print("\nPress Enter to keep the current name, or type a new name:")
    new_name = input().strip()

    if new_name and new_name != name and check_name(new_name):
      new_path = os.path.join(BASE_DIR, in_folder, f"{new_name}.txt")
      auto_complete_names.remove(name)
      auto_complete_names.append(new_name)
      os.rename(note_path, new_path)
      print(f"\nNote renamed to '{new_name}'.\n")
      name = new_name  # Update name
      note_path = new_path  # Update path

    # Step 2: Edit existing content
    with open(note_path, "r") as file:
      old_content = file.readlines()

    print(f"\n\033[1;{theme_color}mCurrent content:\033[0m")
    for i, line in enumerate(old_content, 1):
      print(f"{i}: {line.strip()}")

    new_content = old_content[:]  # Copy old content

    while True:
      command = input(f"\n\033[1;{theme_color}mEnter:\033[0m\n'line number' to edit\n'a' to append\n'd + line number' to delete\n'c + line number' to copy line\n'save' to save:\n\n\033[1;{theme_color}mcmd: \033[0m").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nType new lines (enter 'save' when finished):")
        while True:
          new_line = input()
          if new_line.lower() == "save":
            break
          new_content.append(new_line + "\n")  # Append new lines
      elif command.isdigit():
        line_number = int(command) - 1
        if 0 <= line_number < len(new_content):
          print(f"Current: {new_content[line_number].strip()}")
          new_text = input("New text: ").strip()
          if new_text:
            new_content[line_number] = new_text + "\n"  # Modify the line
        else:
          print("\033[31mInvalid line number.\033[0m")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
          del new_content[line_number]  # Delete the specified line
          print(f"\n\033[32mLine {line_number + 1} deleted.\033[0m")
        else:
          print("\033[31mInvalid line number.\033[0m")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
            copied_line = new_content[line_number]  # Copy the specified line
            pyperclip.copy(copied_line)  # Copy the line to the clipboard
            print(f"\n\033[32mLine {line_number + 1} copied to clipboard.\033[0m")
        else:
            print("\033[31mInvalid line number.\033[0m")
      else:
        print("\033[31mInvalid command.\033[0m")

    # Save updated content
    with open(note_path, "w") as file:
      file.writelines(new_content)
    
    print("\n\033[32mNote updated successfully.\033[0m\n")

  else:  # Renaming a folder
    folder_path = os.path.join(BASE_DIR, name)
    if not os.path.exists(folder_path):
      print("\n\033[31mFolder not found.\033[0m\n")
      return

    print("\nEnter a new name for the folder:")
    new_name = input().strip()

    if new_name and new_name != name and check_name(name):
      auto_complete_names.remove(name)
      auto_complete_names.append(new_name)
      new_folder_path = os.path.join(BASE_DIR, new_name)
      os.rename(folder_path, new_folder_path)
      print(f"\n\033[32mFolder renamed to '{new_name}'.\033[0m\n")

      if in_folder == name:
        in_folder = new_name  # Update reference

def run():
  # Initialize storage
  setup()
  global in_folder
  global theme_color

  print(r"""
  _       __     __                             __      
  | |     / /__  / /________  ____ ___  ___     / /_____ 
  | | /| / / _ \/ / ___/ __ \/ __ `__ \/ _ \   / __/ __ \
  | |/ |/ /  __/ / /__/ /_/ / / / / / /  __/  / /_/ /_/ /
  |__/|__/\___/_/\___/\____/_/ /_/ /_/\___/   \__/\____/ 
    / /____  _________ ___  ____  ____  / /____  _____   
  / __/ _ \/ ___/ __ `__ \/ __ \/ __ \/ __/ _ \/ ___/   
  / /_/  __/ /  / / / / / / / / / /_/ / /_/  __(__  )    
  \__/\___/_/  /_/ /_/ /_/_/ /_/\____/\__/\___/____/     
  """)
  print("Get started by entering 'help' for commands.\n")
  list_folders()

  while True:
    choice = input(f"\033[1;{theme_color}mcmd: \033[0m")

    if choice.startswith("o "):  # Open a folder or note
      name = choice[2:]
      if in_folder:
        read_note(in_folder, name)
      else:
        if os.path.exists(os.path.join(BASE_DIR, name)):
          in_folder = name
          list_notes(name)
        else:
          print("\n\033[31mFolder not found.\033[0m\n")

    elif choice.startswith("d "):  # Delete folder or note
      name = choice[2:]
      if in_folder:
        delete_note_or_folder(os.path.join(in_folder, name), is_folder=False)
      else:
        delete_note_or_folder(name, is_folder=True)

    elif choice.startswith("nf "):  # New folder
      name = choice[3:]
      create_folder(name)

    elif choice.startswith("nn "):  # New note
      if in_folder:
        name = choice[3:]
        print("Note content (enter 'save' to finish):")
          
        content = ""
        while True:
          line = input()
          if line.lower() == "save":  # Stop when the user types "done"
            break
          content += line + "\n"  # Add the line to the note content
        
        create_note(in_folder, name, content)
      else:
          print("\nGo into a folder to create a note.\n")


    elif choice == "l":  # List folders or notes
      if in_folder:
        list_notes(in_folder)
      else:
        list_folders()

    elif choice == "b":  # Go back to folders
      if in_folder:
        in_folder = None
        list_folders()
      else:
        print("\nNowhere to go.\n")

    elif choice.startswith("e "):  # Edit folder or note
      name = choice[2:]
      edit_note_or_folder(name)

    elif choice.startswith("s "):
      name = choice[2:]
      search(name)

    elif choice.startswith("t "):
      color = choice[2:]
      if color == "black":
        theme_color = 30
      elif color == "red":
        theme_color = 31
      elif color == "green":
        theme_color = 32
      elif color == "yellow":
        theme_color = 33
      elif color == "blue":
        theme_color = 34
      elif color == "magenta":
        theme_color = 35
      elif color == "cyan":
        theme_color = 36
      elif color == "white":
        theme_color = 37
      else:
        print("\n\033[31mInvalid color.\033[0m\n")

      with open(CONFIG_FILE, "w") as f:
        json.dump({"theme_color": theme_color}, f)

    elif choice == "help":
      print(f"\n\033[1;{theme_color}mCommands:\n\033[0m\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a folder/note\nl - list folders/notes\nb - back to folders\ne - edit folder/note\ns name - search (case sensitive)\ndn - creates a daily note in the 'daily' folder\nhelp - displays commands\nhelp+ - more specific instructions\nq - quit\n")

    elif choice == "help+":
      print(f"\n\033[1;{theme_color}mInstructions:\033[0m\n\n\033[1mo name\033[0m - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n\033[1mnf name\033[0m - creates a folder with the given name into the root folder\n\033[1mnn name\033[0m - create a new note with the given name. Must be inside of a folder!\n\033[1mdn\033[0m - creates a new note with the current dater. Adds it to the 'dailys' folder, if not created then it will create it.\n\033[1md name\033[0m - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n\033[1ml\033[0m - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n\033[1mb\033[0m - takes you back to the root folder\n\033[1me\033[0m - if you're in the root folder, it allows you to edit a folder name, if you're in a folder, it allows you to edit the note name and its contents\n\033[1ms\033[0m - search for folder or note. If found, you can open the folder in which it was found (search is case sensitive)\n(f) - type of (folder)\n(n) - type of (note)\n\033[1mhelp\033[0m - displays commands\n\033[1mhelp+\033[0m - more specific instructions\n\033[1mt color\033[0m - choose a theme color:\nblack\nred\ngreen\nyellow\nblue\nmagenta\ncyan\nwhite\n\033[1mq\033[0m - quits the application\n")

    elif choice == "q":
      break

    elif choice == "dn":
      if "dailys" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
        create_folder("dailys")
      in_folder = "dailys"
      print(f"\033[32mYou are in 'dailys' folder.\033[0m\n")
      name = datetime.today().strftime('%Y-%m-%d')
      print("Note content (enter 'save' to finish):")
        
      content = ""
      while True:
        line = input()
        if line.lower() == "save":  # Stop when the user types "done"
          break
        content += line + "\n"  # Add the line to the note content
      create_note(in_folder, name, content)

    else:
      print("\033[31mInvalid command.\033[0m\n")
