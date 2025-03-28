#!/usr/bin/env python3

import os
import shutil
import appdirs

# Get the system-specific Notes folder
BASE_DIR = appdirs.user_data_dir("Termnotes", "Termnotes")
in_folder = None  # Tracks current folder

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

def setup():
  """Ensures the base Notes directory exists."""
  if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def list_folders():
  """Lists all folders inside the Notes directory."""
  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

  print("\n\033[1;36mFolders:\033[0m")

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
  if not os.path.exists(folder_path):
    print("\n\033[31mFolder not found.\033[0m\n")
    return
  
  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]

  print(f"\n\033[1;36m{folder}:\033[0m")

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
  os.makedirs(folder_path, exist_ok=True)
  print(f"\n\033[32mNew folder '{name}' created\033[0m\n")

def create_note(folder, name, content):
  """Creates a new note inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path):
    print("\n\033[31mFolder not found. Create the folder first.\033[0m\n")
    return
  
  note_path = os.path.join(folder_path, f"{name}.txt")
  with open(note_path, "w") as file:
    file.write(content)
  
  print(f"\n\033[32mNew note '{name}' created in '{folder}'.\033[0m\n")

def search(name):
  """Searches for a folder or note and prompts the user to open its containing folder."""
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f]
  found_notes = []
  global in_folder
  
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt") and name in f]
      found_notes.extend([(folder, note) for note in notes])
  
  if not found_folders and not found_notes:
    print("\n\033[31mNo matching folders or notes found.\033[0m\n")
    return
  
  print("\n\033[1;36mSearch Results:\033[0m")
  
  for folder in found_folders:
    print(f"├── {folder} (f)")
  
  for folder, note in found_notes:
    print(f"└── {folder}/{note} (n)")
    
  print("\nType the folder name to open it or 'c' to cancel:")
  choice = input().strip()

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
  
  if is_folder:
    if os.path.exists(path) and os.path.isdir(path):
      shutil.rmtree(path)
      print(f"\nFolder '{name}' deleted.\n")
    else:
      print("\n\033[31mFolder not found.\033[0m\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".txt")
    if os.path.exists(note_path):
      os.remove(note_path)
      print(f"\nNote '{name}' deleted.\n")
    else:
      print("\n\033[31mNote not found.\033[0m\n")

def edit_note_or_folder(name):
  """Edits a note (rename and modify content) or renames a folder."""
  global in_folder

  if in_folder:  # Editing a note
    note_path = os.path.join(BASE_DIR, in_folder, f"{name}.txt")

    if not os.path.exists(note_path):
      print("\n\033[31mNote not found.\033[0m\n")
      return

    # Step 1: Rename the note (optional)
    print("\nPress Enter to keep the current name, or type a new name:")
    new_name = input().strip()

    if new_name and new_name != name:
      new_path = os.path.join(BASE_DIR, in_folder, f"{new_name}.txt")
      os.rename(note_path, new_path)
      print(f"\nNote renamed to '{new_name}'.\n")
      name = new_name  # Update name
      note_path = new_path  # Update path

    # Step 2: Edit existing content
    with open(note_path, "r") as file:
      old_content = file.readlines()

    print("\n\033[1mCurrent content:\033[0m (Type a line number to edit, 'a' to append new content, 'd + line number' to delete, 'done' to finish)")
    for i, line in enumerate(old_content, 1):
      print(f"{i}: {line.strip()}")

    new_content = old_content[:]  # Copy old content

    while True:
      command = input("\nEnter line number to edit, 'a' to append, 'd + line number' to delete, or 'save' to save: ").strip()

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
          print(f"\nLine {line_number + 1} deleted.")
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

    if new_name and new_name != name:
      new_folder_path = os.path.join(BASE_DIR, new_name)
      os.rename(folder_path, new_folder_path)
      print(f"\nFolder renamed to '{new_name}'.\n")

      if in_folder == name:
        in_folder = new_name  # Update reference

def run():
  # Initialize storage
  setup()
  global in_folder

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
  print("\n\033[1;36mCommands:\033[0m\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a note/folder\nl - list folders\nb - back to folders\ne - edit folder/note\ns name - search\nhelp - displays commands\nhelp+ - more specific instructions\n")
  print("Get started by entering 'l' to list your root folder directory.\n")

  while True:
    choice = input()

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

    elif choice == "help":
      print("\n\033[1;36mCommands:\033[0m\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a note/folder\nl - list folders\nb - back to folders\ne - edit folder/note\ns name - search\nhelp - displays commands\nhelp+ - more specific instructions\n")

    elif choice == "help+":
      print("\n\033[1;36mInstructions:\033[0m\n\n\033[1mo name\033[0m - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n\033[1mnf name\033[0m - creates a folder with the given name into the root folder\n\033[1mnn name\033[0m - create a new note with the given name. Must be inside of a folder!\n\033[1md name\033[0m - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n\033[1ml\033[0m - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n\033[1mb\033[0m - takes you back to the root folder\n\033[1me\033[0m - if you're in the root folder, it allows you to edit a folder name, if you're in a folder, it allows you to edit the note name and its contents\n\033[1ms\033[0m - search for folder or note. If found, you can open the folder in which it was found\n(f) - type of (folder)\n(n) - type of (note)\n\033[1mhelp\033[0m - displays commands\n\033[1mhelp+\033[0m - more specific instructions\n")

    else:
      print("\033[31mInvalid command.\033[0m\n")
