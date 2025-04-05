#!/usr/bin/env python3

from datetime import datetime
import os
import shutil
import appdirs
import readline
import pyperclip
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

console = Console()

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
auto_complete_names = []
in_folder = None  # Tracks current folder

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

  if not folders:
    content = "[dim]└── Create a folder with 'nf name'[/dim]\n"
  else:
    folder_lines = []
    for i, folder in enumerate(folders):
      if i == len(folders) - 1:  # Last item in the list
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
      else:
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
    content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  panel = Panel(content, title="[bold blue]Folders[/bold blue]")  # Customize title color
  console.print("\n")
  console.print(panel)
  console.print("\n")

def list_notes(folder):
  """Lists all notes inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found.[/bold red]\n")
    return
  
  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]

  if not notes:
      content = "[dim]└── Create a note with 'nn name'[/dim]\n"
  else:
    note_lines = []
    for i, note in enumerate(notes):
      if i == len(notes) - 1:
        note_lines.append(f"[bold]{note}[/bold] (n)")
      else:
        note_lines.append(f"[bold]{note}[/bold] (n)")
    content = "\n".join([f"├── {line}" for line in note_lines[:-1]] + [f"└── {note_lines[-1]}"])

  panel_title = f"[bold blue]{folder}[/bold blue]"  # Customize title color
  panel = Panel(content, title=panel_title)
  console.print("\n")
  console.print(panel)
  console.print("\n")

def create_folder(name):
  """Creates a new folder inside Notes."""
  folder_path = os.path.join(BASE_DIR, name)
  global auto_complete_names
  if check_name(name):
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n[bold green]New folder '{name}' created.[/bold green]\n")
    auto_complete_names.append(name)  # Add folder name to the autocomplete list
    update_completer()
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def create_note(folder, name, content):
  """Creates a new note inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  global auto_complete_names

  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found. Create the folder first.[/bold red]\n")
    return

  if check_name(name):
    auto_complete_names.append(name)  # Add note name to autocomplete
    update_completer()
    note_path = os.path.join(folder_path, f"{name}.txt")
    with open(note_path, "w") as file:
      file.write(content)
    print(f"\n[bold green]New note '{name}' created in '{folder}'.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def search(name):
  """Searches for folders or notes and prompts to open."""
  found_folders = [
    f for f in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f
  ]
  found_notes = []

  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [
        f.replace(".txt", "")
        for f in os.listdir(folder_path)
        if f.endswith(".txt") and name in f
      ]
      found_notes.extend([(folder, note) for note in notes])

  if not found_folders and not found_notes:
    console.print("\n[bold red]No matching folders or notes found[/bold red]\n")
    return

  search_results = []
  if found_folders:
    search_results.append("[bold blue]Folder:[/bold blue]")
    for folder in found_folders:
      search_results.append(f"├── [bold]{folder}[/bold] (f)")
  if found_notes:
    if found_folders:
      search_results.append("\n[bold blue]Note:[/bold blue]")
    else:
      search_results.append("[bold blue]Note:[/bold blue]")
    for folder, note in found_notes:
      search_results.append(f"└── [bold]{folder}/{note}[/bold] (n)")

  results_content = "\n".join(search_results)
  results_panel = Panel(
    results_content, title="[bold green]Search Results[/bold green]"
  )
  console.print(results_panel)

  choice = Prompt.ask(
    f"\nType the folder name to open it or 'c' to cancel",
    default="c",
  )

  if os.path.exists(os.path.join(BASE_DIR, choice)):
    global in_folder
    in_folder = choice
    list_notes(choice)
  elif choice.lower() == "c":
    console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
  else:
    console.print("[bold red]\nInvalid choice.[/bold red]\n")

def read_note(folder, name):
  """Reads and displays a note within a Rich Panel (simple version)."""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.txt")
  title = f"[bold blue]{name}[/bold blue]"

  if not os.path.exists(note_path):
    console.print(f"\n[bold red]Note '{name}' not found in '{folder}'.[/bold red]\n")

  with open(note_path, "r") as file:
    content = file.read()
  panel = Panel("\n" + content, title=title)
  console.print("\n")
  console.print(panel)
  console.print("\n")

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
      print(f"[bold green]Folder '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Folder not found.[/bold red]\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".txt")
    if os.path.exists(note_path):
      if name in auto_complete_names:
        auto_complete_names.remove(name)
        update_completer()
      os.remove(note_path)
      print(f"\n[bold red]Note '{name}' deleted.[/bold red]\n")
    else:
      print("\n\[bold red]Note not found.[/bold red]\n")

def edit_note_or_folder(name):
  """Edits a note (rename and modify content) or renames a folder."""
  global in_folder
  global auto_complete_names

  if in_folder:  # Editing a note
    note_path = os.path.join(BASE_DIR, in_folder, f"{name}.txt")

    if not os.path.exists(note_path):
      print("\n[bold red]Note not found.[/bold red]\n")
      return

    # Step 1: Rename the note (optional)
    print("\nPress Enter to keep the current name, or type a new name:")
    new_name = input().strip()

    if new_name and new_name != name and check_name(new_name):
      new_path = os.path.join(BASE_DIR, in_folder, f"{new_name}.txt")
      auto_complete_names.remove(name)
      auto_complete_names.append(new_name)
      os.rename(note_path, new_path)
      print(f"\n[bold green]Note renamed to '{new_name}'.[/bold green]\n")
      name = new_name  # Update name
      note_path = new_path  # Update path

    # Step 2: Edit existing content
    with open(note_path, "r") as file:
      old_content = file.readlines()

    print(f"\n[bold blue]Current content:[/bold blue]")
    for i, line in enumerate(old_content, 1):
      print(f"{i}: {line.strip()}")

    new_content = old_content[:]  # Copy old content

    while True:
      command = console.input("[bold blue]\nEnter:[/bold blue]\n'line number' to edit\n'a' to append\n'd + line number' to delete\n'c + line number' to copy line\n'save' to save:\n\n[bold blue]cmd: [/bold blue]").strip()

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
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
          del new_content[line_number]  # Delete the specified line
          print(f"\n[bold green]Line {line_number + 1} deleted.[/bold green]")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
            copied_line = new_content[line_number]  # Copy the specified line
            pyperclip.copy(copied_line)  # Copy the line to the clipboard
            print(f"\n[bold green]Line {line_number + 1} copied to clipboard.[/bold green]")
        else:
            print("[bold red]Invalid line number.[/bold red]")
      else:
        print("[bold red]Invalid command.[/bold red]")

    # Save updated content
    with open(note_path, "w") as file:
      file.writelines(new_content)
    
    print("\n[bold green]Note updated successfully.[/bold green]\n")

  else:  # Renaming a folder
    folder_path = os.path.join(BASE_DIR, name)
    if not os.path.exists(folder_path):
      print("\n[bold red]Folder not found.[/bold red]\n")
      return

    print("\nEnter a new name for the folder:")
    new_name = input().strip()

    if new_name and new_name != name and check_name(name):
      auto_complete_names.remove(name)
      auto_complete_names.append(new_name)
      new_folder_path = os.path.join(BASE_DIR, new_name)
      os.rename(folder_path, new_folder_path)
      print(f"\n[bold green]Folder renamed to '{new_name}'.[/bold green]\n")

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
  print("Get started by entering 'help' for commands.\n")
  list_folders()

  while True:
    choice = console.input("[bold blue]cmd: [/bold blue]").strip()

    if choice.startswith("o "):  # Open a folder or note
      name = choice[2:]
      if in_folder:
        read_note(in_folder, name)
      else:
        if os.path.exists(os.path.join(BASE_DIR, name)):
          in_folder = name
          list_notes(name)
        else:
          print("\n[bold red]Folder not found.[/bold red]\n")

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
        console.print("\n[bold blue]Commands:[/bold blue]\no [bold]name[/bold] - open a folder/note\nnf [bold]name[/bold] - create a new folder\nnn [bold]name[/bold] - create a new note\nd [bold]name[/bold] - delete a folder/note\nl - list folders/notes\nb - back to folders\ne - edit folder/note\ns [bold]name[/bold] - search (case sensitive)\ndn - creates a daily note in the 'daily' folder\n[bold]help[/bold] - displays commands\n[bold]help+[/bold] - more specific instructions\nq - quit\n")

    elif choice == "help+":
        console.print("\n[bold blue]Instructions:[/bold blue]\n\n[bold]o name[/bold] - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n[bold]nf name[/bold] - creates a folder with the given name into the root folder\n[bold]nn name[/bold] - create a new note with the given name. Must be inside of a folder!\n[bold]dn[/bold] - creates a new note with the current dater. Adds it to the 'dailys' folder, if not created then it will create it.\n[bold]d name[/bold] - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n[bold]l[/bold] - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n[bold]b[/bold] - takes you back to the root folder\n[bold]e[/bold] - if you're in the root folder, it allows you to edit a folder name, if you're in a folder, it allows you to edit the note name and its contents\n[bold]s name[/bold] - search for folder or note. If found, you can open the folder in which it was found (search is case sensitive)\n([bold]f[/bold]) - type of (folder)\n([bold]n[/bold]) - type of (note)\n[bold]help[/bold] - displays commands\n[bold]help+[/bold] - more specific instructions\n[bold]q[/bold] - quits the application\n") 

    elif choice == "q":
      break

    elif choice == "dn":
      if "dailys" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
        create_folder("dailys")
      in_folder = "dailys"
      print(f"[bold green]You are in 'dailys' folder.[/bold green]\n")
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
      print("[bold red]Invalid command.[/bold red]\n")
