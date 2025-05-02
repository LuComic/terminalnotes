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

  if not folders:
    content = "[dim]└── Create a folder with 'nf name'[/dim]"
  else:
    folder_lines = []
    for i, folder in enumerate(folders):
      if i == len(folders) - 1:  # Last item in the list
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
      else:
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
    content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  inner_panel = Panel(content, title="[bold blue]Folders[/bold blue]", expand=True)  # Customize title color
  empty_panel = Panel("Nothing open", title="", expand=True)

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

  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]

  if not notes:
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
    if i == len(folders) - 1:  # Last item in the list
      folder_lines.append(f"[bold]{some_folder}[/bold] (f)")
    else:
      folder_lines.append(f"[bold]{some_folder}[/bold] (f)")
  folder_content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  all_folders_panel = Panel(folder_content, title="[bold blue]Folders[/bold blue]", expand=True)  # Customize title color

  panel_title = f"[bold blue]{folder}[/bold blue]"  # Customize title color
  folder_panel = Panel(content, title=panel_title, expand=True)

  console.print("\n")
  console.print(all_folders_panel)
  console.print(folder_panel)
  console.print("\n")

def create_folder(name):
  """Creates a new folder inside Notes."""
  folder_path = os.path.join(BASE_DIR, name)
  if check_name(name):
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n[bold green]New folder '{name}' created.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def create_note(folder, name, tags, content):
  """Creates a new note inside a folder, storing plain tags."""
  folder_path = os.path.join(BASE_DIR, folder)

  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found. Create the folder first.[/bold red]\n")
    return

  # Process tags into a plain comma-separated string
  if tags:
    lines = tags.splitlines()
    # Clean tags: remove leading/trailing whitespace and any leading '#'
    cleaned_tags = [line.strip().lstrip('#') for line in lines if line.strip()]
    # Join plain tags with comma and space
    final_tags = ", ".join(cleaned_tags)
  else:
    final_tags = ""

  if check_name(name):
    note_path = os.path.join(folder_path, f"{name}.txt")
    with open(note_path, "w") as file:
      # Write the plain tags string
      file.write(f"Tags: {final_tags}\n\n")
      file.write(content)
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
          if note_file.endswith(".txt"):
            note_path = os.path.join(folder_path, note_file)
            note_name = note_file.replace(".txt", "")
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
    results_panel = Panel(results_content, title="[bold green]Tag Search Results[/bold green]")
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
          if os.path.exists(os.path.join(BASE_DIR, folder_to_open, f"{name}.txt")):
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
        (folder, f.replace(".txt", ""))
        for f in os.listdir(folder_path)
        if f.endswith(".txt") and f.lower().replace('.txt', '') == search_term
      ]
      found_notes_by_name.extend(notes)

  if not found_folders and not found_notes_by_name:
    console.print("\n[bold red]No matching folders or notes found[/bold red]\n")
    return

  search_results = []
  if found_folders:
    search_results.append("[bold blue]Folder:[/bold blue]")
    for folder in found_folders:
      search_results.append(f"├── [bold]{folder}[/bold] (f)")
  if found_notes_by_name:
    if found_folders:
      search_results.append("\n[bold blue]Note:[/bold blue]")
    else:
      search_results.append("[bold blue]Note:[/bold blue]")
    for folder, note in found_notes_by_name:
      search_results.append(f"└── [bold]{folder}/{note}[/bold] (n)")

  results_content = "\n".join(search_results)
  results_panel = Panel(
    results_content, title="[bold green]Search Results[/bold green]"
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
        in_folder = folder_to_open
        list_notes(in_folder)
        return
    elif not found_folders and len(found_notes_by_name) == 1:
      folder, note_to_open = found_notes_by_name[0]
      read_note(folder, note_to_open)
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
  """Reads and displays a note, applying styling to tags and Markdown headings."""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.txt")
  word_count = 0

  if not os.path.exists(note_path):
    console.print(f"\n[bold red]Note '{name}' not found in '{folder}'.[/bold red]\n")
    return

  try:
    with open(note_path, "r") as file:
        lines = file.readlines() # Read all lines at once
  except Exception as e:
    console.print(f"\n[bold red]Error reading note '{name}': {e}[/bold red]\n")
    return

  words = []
  modified_lines = []
  tags_line_processed = False # Flag to ensure we only process the first Tags line

  for i, line in enumerate(lines):
      clean_line = line.strip() # Use stripped line for checks, original for words/output

      # --- Tag Styling ---
      if not tags_line_processed and clean_line.lower().startswith("tags:"):
          tags_str = clean_line[len("tags:"):].strip()
          if tags_str: # Only style if there are tags
              plain_tags = [tag.strip() for tag in tags_str.split(',')]
              styled_tags = [f"[bold pale_violet_red1]#{tag}[/bold pale_violet_red1]" for tag in plain_tags if tag]
              modified_lines.append("Tags: " + ", ".join(styled_tags))
          else:
              modified_lines.append("Tags: ") # Keep empty tags line as is
          tags_line_processed = True
      # --- Markdown Styling ---
      elif clean_line.startswith("# "): # Standard Markdown heading requires space
          modified_line = f"[bold]{clean_line.lstrip('#').strip()}[/bold]"
          modified_lines.append(modified_line)
          # Count words in headings too, if desired (excluding the '#')
          words.extend(clean_line.lstrip('#').strip().split())
      elif clean_line.startswith("-[]"):
          modified_line = f"[bold red]- [/bold red]{clean_line.lstrip('-[]').strip()}"
          modified_lines.append(modified_line)
          words.extend(clean_line.lstrip('-[]').strip().split())
      elif clean_line.startswith("-[+]"):
          modified_line = f"[bold green]+ [/bold green]{clean_line.lstrip('-[+]').strip()}"
          modified_lines.append(modified_line)
          words.extend(clean_line.lstrip('-[+]').strip().split())
      elif clean_line.startswith("- "):
          modified_line = f"{" " * 4}• {clean_line.lstrip('- ').strip()}"
          modified_lines.append(modified_line)
          words.extend(clean_line.lstrip('- ').strip().split())
      # --- Regular Content ---
      else:
          # Add the original line (with potential leading/trailing whitespace preserved for formatting)
          modified_lines.append(line.rstrip('\n')) # Avoid double newlines
          # Only count words if it's not the tags line or the blank line after tags
          if i > 1 or not tags_line_processed: # Adjust index check if needed
              words.extend(clean_line.split())

  # Reconstruct content for display
  content_for_display = "\n".join(modified_lines)
  word_count = len(words)

  title = f"[bold blue]{name} | {word_count} words[/bold blue]"

  folder_path = os.path.join(BASE_DIR, folder)
  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]
  note_lines = []
  for i, note in enumerate(notes):
    if i == len(notes) - 1:
      note_lines.append(f"[bold]{note}[/bold] (n)")
    else:
      note_lines.append(f"[bold]{note}[/bold] (n)")
  folder_content = "\n".join([f"├── {line}" for line in note_lines[:-1]] + [f"└── {note_lines[-1]}"])
  folder_title = f"[bold blue]{folder}[/bold blue]"
  folder_panel = Panel(folder_content, title=folder_title, expand=True)
  # Added newline before content for spacing
  note_panel = Panel("\n" + content_for_display, title=title, expand=True)

  console.print("\n")
  console.print(folder_panel)
  console.print(note_panel)
  console.print("\n")

def delete_note_or_folder(name, is_folder):
  """Deletes a note or folder."""
  path = os.path.join(BASE_DIR, name)

  if is_folder:
    if os.path.exists(path) and os.path.isdir(path):
      shutil.rmtree(path)
      print(f"\n[bold green]Folder '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Folder not found.[/bold red]\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".txt")
    if os.path.exists(note_path):
      os.remove(note_path)
      print(f"\n[bold green]Note '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Note not found.[/bold red]\n")

def edit_note_or_folder(name):
  """Edits a note (rename, modify tags, modify content) or renames a folder, working with plain tags."""
  global in_folder

  if in_folder:  # Editing a note
    note_path = os.path.join(BASE_DIR, in_folder, f"{name}.txt")

    if not os.path.exists(note_path):
      print("\n[bold red]Note not found.[/bold red]\n")
      return

    # Step 1: Rename the note (optional)
    print("\nPress Enter to keep the current name, or type a new name:")
    new_name_input = input().strip() # Renamed variable to avoid conflict

    # Use check_name relative to the *current* folder for notes
    def check_note_name_in_folder(folder, note_name_to_check):
        folder_path = os.path.join(BASE_DIR, folder)
        if not os.path.isdir(folder_path):
            return True # Folder doesn't exist, so name is available technically
        existing_notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]
        return note_name_to_check not in existing_notes

    if new_name_input and new_name_input != name and check_note_name_in_folder(in_folder, new_name_input):
      new_path = os.path.join(BASE_DIR, in_folder, f"{new_name_input}.txt")
      os.rename(note_path, new_path)
      print(f"\n[bold green]Note renamed to '{new_name_input}'.[/bold green]")
      name = new_name_input  # Update name
      note_path = new_path  # Update path
    elif new_name_input and new_name_input != name:
        print(f"\n[bold red]Note name '{new_name_input}' already exists in folder '{in_folder}'.[/bold red]\n")
        # Optionally return here or let the user proceed with editing content under the old name
        # Let's proceed for now

    # Read existing content including the tags line
    try:
        with open(note_path, "r") as f:
            all_lines = f.readlines()
    except Exception as e:
        print(f"\n[bold red]Error reading note for editing: {e}[/bold red]\n")
        return

    # Extract plain tags from the first line
    old_tags_list = []
    if all_lines:
        first_line = all_lines[0].strip()
        if first_line.lower().startswith("tags:"):
            tag_string = first_line[len("tags:"):].strip()
            if tag_string: # Check if there are any tags
                # Split plain tags
                old_tags_list = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
        else:
             # If first line isn't tags, assume no tags initially
             all_lines.insert(0, "Tags: \n") # Add a placeholder Tags line
             all_lines.insert(1, "\n") # Add blank line after tags

    print(f"\n[bold blue]Current tags:[/bold blue]")
    if not old_tags_list:
        print("[dim]No tags defined.[/dim]")
    else:
        for i, tag in enumerate(old_tags_list, 1):
            print(f"{i}: {tag}") # Display plain tags

    new_tags = old_tags_list[:] # Start editing with current tags

    # Tag editing loop
    while True:
      command = console.input("[bold blue]\nEdit Tags:[/bold blue]\n'line number' to edit\n'a' to add\n'd + line number' to delete\n'c + line number' to copy\n'save' to save tags:\n\n[bold blue]cmd: [/bold blue]").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nAdd tag(s) (one per line, enter 'save' when finished):")
        while True:
          new_tag_input = input().strip()
          if new_tag_input.lower() == "save":
            break
          # Add the plain tag directly, clean it first
          cleaned_add_tag = new_tag_input.lstrip('#').strip()
          if cleaned_add_tag: # Avoid adding empty tags
             new_tags.append(cleaned_add_tag)
             print(f"[dim]Added: {cleaned_add_tag}[/dim]")
      elif command.isdigit():
        line_number = int(command) - 1
        if 0 <= line_number < len(new_tags):
          print(f"Current tag {line_number + 1}: {new_tags[line_number]}")
          edited_tag_input = input("Edited tag: ").strip()
          # Edit the plain tag, clean it
          cleaned_edit_tag = edited_tag_input.lstrip('#').strip()
          if cleaned_edit_tag:
            new_tags[line_number] = cleaned_edit_tag
          else:
            print("[bold yellow]Tag cannot be empty. Deleting instead.[/bold yellow]")
            del new_tags[line_number] # Delete if user provides empty input
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_tags):
          deleted_tag = new_tags.pop(line_number)
          print(f"\n[bold green]Tag '{deleted_tag}' (nr {line_number + 1}) deleted.[/bold green]")
          # Re-display tags after deletion
          print(f"\n[bold blue]Current tags:[/bold blue]")
          if not new_tags:
              print("[dim]No tags defined.[/dim]")
          else:
              for i, tag in enumerate(new_tags, 1):
                  print(f"{i}: {tag}")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_tags):
          copied_tag = new_tags[line_number]
          pyperclip.copy(copied_tag) # Copy plain tag
          print(f"\n[bold green]Tag '{copied_tag}' (nr {line_number + 1}) copied to clipboard.[/bold green]")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      else:
        print("[bold red]Invalid command.[/bold red]")

    # Format final plain tags for saving
    final_tags_plain = ", ".join(new_tags) # Join the list of plain tags

    # Update the first line in all_lines with the new plain tags
    all_lines[0] = f"Tags: {final_tags_plain}\n"

    # Ensure there's a blank line after tags if content exists
    if len(all_lines) > 1 and all_lines[1].strip() != "":
        all_lines.insert(1, "\n")
    elif len(all_lines) == 1: # Only tag line exists
        all_lines.append("\n") # Add the blank line


    # --- Content Editing ---
    # Use lines starting *after* the Tags line and the potential blank line
    old_content_lines = all_lines[2:]

    print(f"\n[bold blue]Current content:[/bold blue]")
    if not old_content_lines:
        print("[dim]Note is empty.[/dim]")
    else:
        for i, line in enumerate(old_content_lines):
            print(f"{i+1}: {line.strip()}") # Display content lines indexed from 1

    new_content_lines = old_content_lines[:]  # Copy old content lines for editing

    # Content editing loop
    while True:
      command = console.input("[bold blue]\nEdit Content:[/bold blue]\n'line number' to edit\n'a' to append\n'd + line number' to delete\n'c + line number' to copy\n'save' to save content:\n\n[bold blue]cmd: [/bold blue]").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nType new lines (enter 'save' when finished):")
        while True:
          new_line_input = input()
          if new_line_input.lower() == "save":
            break
          new_content_lines.append(new_line_input + "\n")  # Append new lines
      elif command.isdigit():
        line_number = int(command) - 1 # Adjust to 0-based index for the list
        if 0 <= line_number < len(new_content_lines):
          print(f"Current line {line_number + 1}: {new_content_lines[line_number].strip()}")
          new_text = input("New text: ").strip()
          # Keep the newline consistent
          new_content_lines[line_number] = new_text + "\n"
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1 # Adjust to 0-based index
        if 0 <= line_number < len(new_content_lines):
          deleted_line = new_content_lines.pop(line_number)
          print(f"\n[bold green]Line {line_number + 1} deleted: '{deleted_line.strip()}'[/bold green]")
          # Re-display content numbers might be helpful here if list is long
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1 # Adjust to 0-based index
        if 0 <= line_number < len(new_content_lines):
            copied_line = new_content_lines[line_number]
            pyperclip.copy(copied_line)
            print(f"\n[bold green]Line {line_number + 1} copied to clipboard.[/bold green]")
        else:
            print("[bold red]Invalid line number.[/bold red]")
      else:
        print("[bold red]Invalid command.[/bold red]")

    # Combine updated tags line and updated content lines
    final_lines_to_write = all_lines[:2] + new_content_lines

    # Save updated tags and content back to the file
    try:
        with open(note_path, "w") as file:
            file.writelines(final_lines_to_write)
        print("\n[bold green]Note updated successfully.[/bold green]\n")
    except Exception as e:
        print(f"\n[bold red]Error writing updated note: {e}[/bold red]\n")


  else:  # Renaming a folder
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
  if source.endswith(".txt") is False:
    source = f"{source}.txt"
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
  quick_note_opened = False
  if quick_note_opened is False:
    if "quick_notes" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
      create_folder("quick_notes")
    in_folder = "quick_notes"
    list_notes(in_folder)
    name = f'{datetime.strftime(datetime.now(), "%d.%m.%y-%H:%M")}'
    tags = ""

    print("Note content (enter 'save' to finish or 'exit' to discard note):")
    content = ""
    while True:
      line = input()
      if line.lower() == "save":  # Stop when the user types "done"
        create_note(in_folder, name, tags, content)
        break
      elif line.lower() == "exit":
        console.print("\n[bold yellow]Note discarded[/bold yellow]\n")
        break
      content += line + "\n"  # Add the line to the note content

    quick_note_opened = True

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

        print("Note tags (each on a new line, enter 'save' to finish):")
        tags = ""
        while True:
          line = input()
          if line.lower() == "save":
            break
          tags += line + "\n"

        print("Note content (enter 'save' to finish or 'exit' to discard note):")
        content = ""
        while True:
          line = input()
          if line.lower() == "save":  # Stop when the user types "done"
            create_note(in_folder, name, tags, content)
            break
          elif line.lower() == "exit":
            console.print("\n[bold yellow]Note discarded[/bold yellow]\n")
            break
          content += line + "\n"  # Add the line to the note content

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
        console.print("\n[bold blue]Commands:[/bold blue]\n\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a folder/note\nl - list folders/notes\nb - back to folders\ne name - edit folder/note\ns name - search\ndn - creates a daily note in the 'dailys' folder\nhelp - displays commands\nhelp+ - more specific instructions\nq - quit\nmd - markdown syntax\nmv folder/note destination - moves a note to the destination folder\n")

    elif choice == "help+":
        console.print("\n[bold blue]Instructions:[/bold blue]\n\n[bold]o name[/bold] - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n[bold]nf name[/bold] - creates a folder with the given name into the root folder\n[bold]nn name[/bold] - create a new note with the given name. Must be inside of a folder!\n[bold]dn[/bold] - creates a new note with the current dater. Adds it to the 'dailys' folder, if not created then it will create it.\n[bold]d name[/bold] - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n[bold]l[/bold] - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n[bold]b[/bold] - takes you back to the root folder\n[bold]e name[/bold] - if you're in the root folder, it allows you to edit a folder name, if you're in a folder, it allows you to edit the note name and its contents\n[bold]s name[/bold] - search for folder or note. If found, you can open the folder in which it was found (search is case sensitive)\n([bold]f[/bold]) - type of (folder)\n([bold]n[/bold]) - type of (note)\n[bold]help[/bold] - displays commands\n[bold]help+[/bold] - more specific instructions\n[bold]q[/bold] - quits the application\n[bold]md[/bold] - markdown syntax\n[bold]mv folder/note destination[/bold] - moves a note to the destination folder. [bold]Does not work for names with spaces[/bold]\n")

    elif choice == "q":
      break
    
    elif choice == "md":
      console.print("\n[bold blue]Markdown:[/bold blue]\n\n[bold]-[][/bold] - uncomplete todo\n[bold]-[+][/bold] - complete todo\n[bold]-[/bold] - list item\n[bold]#[/bold] - header\n")

    elif choice == "dn":
      if "dailys" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
        create_folder("dailys")
      in_folder = "dailys"
      print(f"[bold green]You are in 'dailys' folder.[/bold green]\n")
      name = datetime.today().strftime('%Y-%m-%d')

      print("Note tags (each on a new line, enter 'save' to finish):")
      tags = ""
      while True:
        line = input()
        if line.lower() == "save":
          break
        tags += line + "\n"

      print("Note content (enter 'save' to finish):")

      content = ""
      while True:
        line = input()
        if line.lower() == "save":  # Stop when the user types "done"
          break
        content += line + "\n"  # Add the line to the note content
      create_note(in_folder, name, tags, content)

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
