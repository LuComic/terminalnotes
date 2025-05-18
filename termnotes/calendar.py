import json
import os
from rich.table import Table
from rich.console import Console
import importlib.resources

console = Console()

# Load data.json safely from the installed package
with importlib.resources.path('termnotes', 'data.json') as data_file_path:
  if data_file_path.stat().st_size == 0:
    calendar_items = {}
  else:
    with open(data_file_path, 'r') as f:
      calendar_items = json.load(f)

def open_calendar():
  table = Table(title="Calendar")
  table.add_column("Date", justify="left", style="gray", no_wrap=True)
  table.add_column("Note", justify="left", style="aquamarine1")

  if calendar_items:
    for name, date in calendar_items.items():
      table.add_row(date, name)
  else:
    table.add_row("...", "...")

  console.print(table)
