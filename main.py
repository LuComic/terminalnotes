from datetime import datetime
import os
import shutil
import appdirs
import gnureadline as readline
import pyperclip
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.box import DOUBLE_EDGE
import glob
import platform
import subprocess

console = Console()

def clear_terminal():
  if platform.system() == "Windows":
    os.system("cls")
  else:
    os.system("clear")

# Get the system-specific Notes folder
# BASE_DIR = appdirs.user_data_dir("Termnotes", "Termnotes")
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Termnotes")
CONFIG_FILE = "config.json"
in_folder = None  # Tracks current folder

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

# Function to check if name already exists
def check_name(name):
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f]
  found_notes = []

  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [f.replace(".md", "") for f in os.listdir(folder_path) if f.endswith(".md") and name in f]
      found_notes.extend([(folder, note) for note in notes])

  if not found_notes and not found_folders:
    return True
  return False

def filename_completer(text, state):
  """
  Completer function for filenames within the current context.
  """
  matches = []
  if in_folder:
    # Complete note filenames within the current folder
    folder_path = os.path.join(BASE_DIR, in_folder)
    note_files = glob.glob(os.path.join(folder_path, text + '*.md'))
    matches.extend([os.path.basename(f).replace('.md', '') for f in note_files])
  else:
    # Complete folder names in the base directory
    folder_paths = glob.glob(os.path.join(BASE_DIR, text + '*'))
    matches.extend([os.path.basename(f) for f in folder_paths if os.path.isdir(f)])

  try:
    return matches[state]
  except IndexError:
    return None

readline.set_completer(filename_completer)
readline.set_completer_delims(' \t\n')
readline.parse_and_bind("tab: menu-complete")
readline.set_completion_display_matches_hook(None) # Use the default display hook

def setup():
  """Ensures the base Notes directory exists."""
  if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def list_folders():
  """Lists all folders inside the Notes directory."""
  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

  if not folders:
    content = "[dim]└── Create a folder with 'nf name'[/dim]"
  else:
    folder_lines = []
    for i, folder in enumerate(folders):
      if i == len(folders) - 1:  # Last item in the list
        if folder != "Calendar":
          folder_lines.append(f"[bold]{folder}[/bold] (d)")
        else:
          folder_lines.append(f"[bold aquamarine1]{folder}[/bold aquamarine1] (C)")
      else:
        if folder != "Calendar":
          folder_lines.append(f"[bold]{folder}[/bold] (d)")
        else:
          folder_lines.append(f"[bold aquamarine1]{folder}[/bold aquamarine1] (C)")
    content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  inner_panel = Panel(content, title="[bold blue]Folders[/bold blue]", expand=True, box=DOUBLE_EDGE)  # Customize title color
  empty_panel = Panel("Nothing open", title="", expand=True, box=DOUBLE_EDGE)

  console.print("\n")
  console.print(inner_panel)
  console.print(empty_panel)
  console.print("\n")

def list_notes(folder):
  """Lists all notes inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found.[/bold red]\n")
    return

  notes = [f.replace(".md", "") for f in os.listdir(folder_path) if f.endswith(".md")]

  if folder == "Calendar":
    import calendar_func
    content = calendar_func.generate_calendar()
  elif not notes:
    content = "[dim]└── Create a note with 'nn name'[/dim]"
  else:
    note_lines = []
    for i, note in enumerate(notes):
      if i == len(notes) - 1:
        note_lines.append(f"[bold]{note}[/bold] (n)")
      else:
        note_lines.append(f"[bold]{note}[/bold] (n)")
    content = "\n".join([f"├── {line}" for line in note_lines[:-1]] + [f"└── {note_lines[-1]}"])

  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

  folder_lines = []
  for i, some_folder in enumerate(folders):
    if some_folder == folder:  # Give the selected fodler an underline
      if some_folder == "Calendar":
        folder_lines.append(f"[bold underline aquamarine1]{some_folder}[/bold underline aquamarine1] (C)")
      else:
        folder_lines.append(f"[bold underline]{some_folder}[/bold underline] (d)")        
    else:
      if some_folder == "Calendar":
        folder_lines.append(f"[bold aquamarine1]{some_folder}[/bold aquamarine1] (C)")
      else:
        folder_lines.append(f"[bold]{some_folder}[/bold] (d)")
  folder_content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  all_folders_panel = Panel(folder_content, title="[bold blue]Folders[/bold blue]", expand=True, box=DOUBLE_EDGE)

  panel_title = f"[bold blue]{folder}[/bold blue]"  # Customize title color
  folder_panel = Panel(content, title=panel_title, expand=True, box=DOUBLE_EDGE)

  console.print("\n")
  console.print(all_folders_panel)
  console.print(folder_panel)
  console.print("\n")

def create_folder(name):
  """Creates a new folder inside Notes."""
  folder_path = os.path.join(BASE_DIR, name)
  if check_name(name):
    os.makedirs(folder_path, exist_ok=True)
    if name != "Calendar" and name != "quick_notes":
      print(f"\n[bold green]New folder '{name}' created.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def create_note(folder, name, song=None):
  """Creates a new note inside a folder, storing plain tags."""
  folder_path = os.path.join(BASE_DIR, folder)

  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found. Create the folder first.[/bold red]\n")
    return

  if check_name(name):
    note_path = os.path.join(folder_path, f"{name}.md")
      # Create the file if it doesn't exist
    if not os.path.exists(note_path):
      with open(note_path, "w") as f:
        if song is not None:
          f.write("# Title: \n\n## Chords\n\n---\n\n---\n\n## Lyrics\n\n---\n\n---\n\n## Chorus\n\n---\n\n---")
        else:
          f.write(f"-- {name} --")
    subprocess.run(["nvim", note_path])
    print(f"\n[bold green]New note '{name}' created in '{folder}'.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def search(query):
  """Searches for folders, notes by name, or notes by tags (reading plain tags) and prompts to open."""
  global in_folder
  found_notes_by_name = []
  found_notes_by_tag = {}
  search_term = query.lower()

  if query.startswith("#"):
    tag_to_search = query[1:].strip().lower()
    for folder in os.listdir(BASE_DIR):
      folder_path = os.path.join(BASE_DIR, folder)
      if os.path.isdir(folder_path):
        for note_file in os.listdir(folder_path):
          if note_file.endswith(".md"):
            note_path = os.path.join(folder_path, note_file)
            note_name = note_file.replace(".md", "")
            try: # Added try-except for potentially empty files
              with open(note_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.lower().startswith("tags:"):
                  tags_str = first_line[len("tags:"):].strip()
                  # Read plain tags, split, strip, and lowercase
                  note_tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
                  if tag_to_search in note_tags:
                    if note_name not in found_notes_by_tag:
                      found_notes_by_tag[note_name] = folder
            except Exception as e:
              print(f"[dim]Skipping note {folder}/{note_name} due to read error: {e}[/dim]")


  if found_notes_by_tag:
    results_content = "[bold blue]Notes found by tag:[/bold blue]\n"
    tag_items = list(found_notes_by_tag.items())
    for i, (name, folder) in enumerate(tag_items):
      if i == len(tag_items) - 1:
        results_content += f"└── [bold]{folder}/{name}[/bold] (n)"
      else:
        results_content += f"├── [bold]{folder}/{name}[/bold] (n)\n"
    results_panel = Panel(results_content, title="[bold green]Tag Search Results[/bold green]", box=DOUBLE_EDGE)
    console.print("\n")
    console.print(results_panel)
    choice = Prompt.ask("\nType 'o + note name' to open or 'c' to cancel").strip().lower()
    if choice != 'c' and choice.startswith('o '):
      name = choice[2:].strip()
      if len(name) > 0:
        folder_to_open = ""
        exact_match = False
        # First try exact matches
        for search_name, folder in found_notes_by_tag.items():
          if search_name.lower() == name.lower():
            folder_to_open = folder
            name = search_name  # Use the actual case from the filename
            exact_match = True
            break

        # If no exact match, try partial matches
        if not exact_match:
          matches = []
          for search_name, folder in found_notes_by_tag.items():
            if name.lower() in search_name.lower():
              matches.append((search_name, folder))

          # If we have just one match, use it
          if len(matches) == 1:
            name, folder_to_open = matches[0]
          # If multiple matches, ask the user to be more specific
          elif len(matches) > 1:
            console.print("\n[bold yellow]Multiple matches found:[/bold yellow]")
            for i, (match_name, match_folder) in enumerate(matches):
              console.print(f"{i+1}: {match_folder}/{match_name}")
            console.print("\n[bold yellow]Please use more specific name or full note name.[/bold yellow]\n")
            return

        if folder_to_open:
          if os.path.exists(os.path.join(BASE_DIR, folder_to_open, f"{name}.md")):
            read_note(folder_to_open, name)
            in_folder = folder_to_open
            return
          else:
            console.print("\n[bold red]Note not found in the specified folder.[/bold red]\n")
            return
        else:
          console.print("\n[bold red]No note found matching that name.[/bold red]\n")
          return
      else:
        console.print("\n[bold red]Invalid open format.[/bold red]\n")
        return
    elif choice == 'c':
      console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
      return
    else:
      console.print("[bold red]\nInvalid choice.[/bold red]\n")
      return

  # Search folders (exact match only)
  found_folders = [
    f for f in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, f)) and f.lower() == search_term
  ]

  # Search notes (exact match only)
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [
        (folder, f.replace(".md", ""))
        for f in os.listdir(folder_path)
        if f.endswith(".md") and f.lower().replace('.md', '') == search_term
      ]
      found_notes_by_name.extend(notes)

  if not found_folders and not found_notes_by_name:
    console.print("\n[bold red]No matching folders or notes found[/bold red]\n")
    return

  search_results = []
  if found_folders:
    search_results.append("[bold blue]Folder:[/bold blue]")
    for folder in found_folders:
      search_results.append(f"├── [bold]{folder}[/bold] (d)")
  if found_notes_by_name:
    if found_folders:
      search_results.append("\n[bold blue]Note:[/bold blue]")
    else:
      search_results.append("[bold blue]Note:[/bold blue]")
    for folder, note in found_notes_by_name:
      search_results.append(f"└── [bold]{folder}/{note}[/bold] (n)")

  results_content = "\n".join(search_results)
  results_panel = Panel(
    results_content, title="[bold green]Search Results[/bold green]", box=DOUBLE_EDGE
  )
  console.print("\n")
  console.print(results_panel)

  choice = Prompt.ask(
    f"\nType 'o' to open or 'c' to cancel search"
  ).lower()

  if choice == "o":
    if len(found_folders) == 1 and not found_notes_by_name:
      folder_to_open = found_folders[0]
      if os.path.exists(os.path.join(BASE_DIR, folder_to_open)):
        clear_terminal()
        print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
        print("'Help' for commands.")
        in_folder = folder_to_open
        list_notes(in_folder)
        return
    elif not found_folders and len(found_notes_by_name) == 1:
      clear_terminal()
      print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
      print("'Help' for commands.")
      folder, note_to_open = found_notes_by_name[0]
      read_note(folder, note_to_open)
      list_notes(folder)
      in_folder = folder
      return
    elif found_folders or found_notes_by_name:
      print("\n[bold yellow]Multiple results found. Please be more specific or use 'o folder/note_name'[/bold yellow]\n")
      return
  elif choice == "c":
    console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
  else:
    console.print("[bold red]\nInvalid choice.[/bold red]\n")

def read_note(folder, name):
  """Reads and displays a note, applying styling to tags and Markdown headings"""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.md")

  if not os.path.exists(note_path):
    list_notes(in_folder)
    console.print(f"[bold red]Note '{name}' not found in '{folder}'.[/bold red]\n")
    return

  list_notes(in_folder)

  subprocess.run(["nvim", os.path.join(BASE_DIR, folder, f"{name}.md")])

def delete_note_or_folder(name, is_folder):
  """Deletes a note or folder."""
  path = os.path.join(BASE_DIR, name)

  if is_folder:
    if os.path.exists(path) and os.path.isdir(path):
      shutil.rmtree(path)
      if name == "Calendar":
        print(f"\n[bold green]Calendar deleted.[/bold green]\n")
      else:
        print(f"\n[bold green]Folder '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Folder not found.[/bold red]\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".md")
    if os.path.exists(note_path):
      os.remove(note_path)
      print(f"\n[bold green]Note '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Note not found.[/bold red]\n")

def edit_note_or_folder(name):
  global in_folder
  folder_path = os.path.join(BASE_DIR, name)
  if not os.path.exists(folder_path) or not os.path.isdir(folder_path): # Check if it's actually a folder
    print("\n[bold red]Folder not found.[/bold red]\n")
    return

  print("\nEnter a new name for the folder:")
  new_folder_name = input().strip()

  # Use the global check_name for folders in the base directory
  if new_folder_name and new_folder_name != name and check_name(new_folder_name):
    new_folder_path = os.path.join(BASE_DIR, new_folder_name)
    os.rename(folder_path, new_folder_path)
    print(f"\n[bold green]Folder renamed to '{new_folder_name}'.[/bold green]\n")

    # No need to update in_folder here, as we are not inside any folder when renaming one
  elif not new_folder_name:
        print("\n[bold red]Folder name cannot be empty.[/bold red]\n")
  elif new_folder_name == name:
        print("\n[dim]Name unchanged.[/dim]\n")
  else: # Name exists or other issue
    print("\n[bold red]Invalid or duplicate folder name.[/bold red]\n")

def move_note_or_folder(source, destination):
  """Moves a note or folder to a new destination."""
  # Resolve source and destination paths relative to BASE_DIR
  if source.endswith(".md") is False:
    source = f"{source}.md"
  source_path = os.path.abspath(os.path.join(BASE_DIR, source.strip()))
  destination_path = os.path.abspath(os.path.join(BASE_DIR, destination.strip()))

  # Check if the source exists
  if not os.path.exists(source_path):
    print(f"\n[bold red]Source '{source}' not found.[/bold red]\n")
    return

  # Check if the destination is a valid folder
  if not os.path.exists(destination_path) or not os.path.isdir(destination_path):
    print(f"\n[bold red]Destination folder '{destination}' not found.[/bold red]\n")
    return

  try:
    # Perform the move operation
    shutil.move(source_path, destination_path)
    print(f"\n[bold green]'{source}' moved to '{destination}'.[/bold green]\n")
  except Exception as e:
    print(f"\n[bold red]Error moving: {e}[/bold red]\n")


def run():
  # Initialize storage
  setup()
  global in_folder

  print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
  print("'Help' for commands.")
  list_folders()

  if "Calendar" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
    create_folder("Calendar") 

  while True:
    choice = console.input("[bold blue]cmd: [/bold blue]").strip()

    if choice.startswith("o "):  # Open a folder or note
      clear_terminal()
      print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
      print("'Help' for commands.")
      name = choice[2:]
      if in_folder:
        read_note(in_folder, name)
      else:
        if os.path.exists(os.path.join(BASE_DIR, name)):
          in_folder = name
          list_notes(name)
        else:
          list_folders()
          print("[bold red]Folder not found.[/bold red]\n")

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
        create_note(in_folder, name)
      else:
          print("\nGo into a folder to create a note.\n")

    elif choice.startswith("ns "):
      if in_folder:
        name = choice[3:]
        create_note(in_folder, name, "yes")
      else:
        print("\nGo into a folder to create a note.\n")

    elif choice == "l":  # List folders or notes
      clear_terminal()
      print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
      print("'Help' for commands.")
      if in_folder:
        list_notes(in_folder)
      else:
        list_folders()

    elif choice == "b":  # Go back to folders
      clear_terminal()
      print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
      print("'Help' for commands.")
      if in_folder:
        in_folder = None
        list_folders()
      else:
        list_folders()
        print("Nowhere to go.\n")

    elif choice.startswith("e "):  # Edit folder or note
      if in_folder:
        console.print("\n[bold red]Go into the root folder to edit a folder.[/bold red]")
      else:
        name = choice[2:]
        edit_note_or_folder(name)

    elif choice.startswith("s "):
      name = choice[2:]
      search(name)

    elif choice == "help":
        console.print("\n[bold blue]Commands:[/bold blue]\n\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a folder/note\nl - list folders/notes\nb - back to folders\ne name - edit folder\ns name - search\ndn - creates a daily note in the 'dailys' folder\nhelp - displays commands\ninst - more specific instructions\nq - quit\nq - quit\ntab - autocomplete\nmv folder/note destination - moves a note to the destination folder\n")

    elif choice == "inst":
        console.print("\n[bold blue]Instructions:[/bold blue]\n\n[bold]o name[/bold] - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n[bold]nf name[/bold] - creates a folder with the given name into the root folder\n[bold]nn name[/bold] - create a new note with the given name. Must be inside of a folder!\n[bold]dn[/bold] - creates a new note with the current dater. Adds it to the 'dailys' folder, if not created then it will create it.\n[bold]d name[/bold] - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n[bold]l[/bold] - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n[bold]b[/bold] - takes you back to the root folder\n[bold]e name[/bold] - it allows you to edit the folder name\n[bold]s name[/bold] - search for folder or note. If found, you can open the folder in which it was found (search is case sensitive)\n([bold]f[/bold]) - type of (folder)\n([bold]n[/bold]) - type of (note)\n[bold]help[/bold] - displays commands\n[bold]inst[/bold] - more specific instructions\n[bold]q[/bold] - quits the application\n[bold]mv folder/note destination[/bold] - moves a note to the destination folder. [bold]Does not work for names with spaces[/bold]\n[bold]tab[/bold] - autocomplete\n")

    elif choice == "q":
      break

    elif choice == "dn":
      clear_terminal()
      if "dailys" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
        create_folder("dailys")
      in_folder = "dailys"
      print(f"[bold green]You are in 'dailys' folder.[/bold green]\n")
      name = datetime.today().strftime('%Y-%m-%d')
      create_note(in_folder, name)

    elif choice.startswith("mv "):
      specification = choice[3:].strip()
      if " " not in specification:
        print("\n[bold red]Invalid format. Use 'mv source destination'.[/bold red]\n")
      else:
        # Split the input into source and destination, accounting for spaces in names
        try:
          source, destination = specification.split(" ", 1)
          move_note_or_folder(source.strip(), destination.strip())
        except ValueError:
          print("\n[bold red]Invalid format. Use 'mv source destination'.[/bold red]\n")

    else:
      print("\n[bold red]Invalid command.[/bold red]\n")


if __name__ == "__main__":
    run()