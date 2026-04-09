import calendar
from datetime import datetime

def generate_calendar():
  now = datetime.now()
  current_day = now.day
  current_month = now.month
  current_year = now.year
  
  # Get the calendar as a string
  cal_string = calendar.month(current_year, current_month)
  
  # Split into lines to process
  lines = cal_string.split('\n')
  
  # Process each line to highlight the current day
  processed_lines = []
  for line in lines:
    # Skip header lines (month/year and day names)
    if current_month in [1,2,3,4,5,6,7,8,9,10,11,12] and any(month_name in line for month_name in calendar.month_name[1:]):
      processed_lines.append(f"[bold cyan]{line}[/bold cyan]")
    elif 'Mo Tu We Th Fr Sa Su' in line:
      processed_lines.append(f"[dim]{line}[/dim]")
    else:
      # Process day lines
      new_line = ""
      i = 0
      while i < len(line):
        # Check if we're looking at a space followed by a digit (single digit days)
        if i < len(line) - 1 and line[i] == ' ' and line[i + 1].isdigit():
          # Look ahead to see if it's a single digit or double digit
          if i + 2 < len(line) and line[i + 2].isdigit():
            # Double digit - extract both digits
            num_str = line[i + 1:i + 3]
            if int(num_str) == current_day:
              new_line += f"[bold aquamarine1] {num_str}[/bold aquamarine1]"
            else:
              new_line += f" {num_str}"
            i += 3
          else:
            # Single digit
            num_str = line[i + 1]
            if int(num_str) == current_day:
              new_line += f"[bold aquamarine1] {num_str}[/bold aquamarine1]"
            else:
              new_line += f" {num_str}"
            i += 2
        elif line[i].isdigit() and i == 0:
          # Handle case where line starts with a digit (shouldn't happen in normal calendar)
          num_str = ""
          j = i
          while j < len(line) and line[j].isdigit():
            num_str += line[j]
            j += 1
          if int(num_str) == current_day:
            new_line += f"[bold aquamarine1]{num_str}[/bold aquamarine1]"
          else:
            new_line += num_str
          i = j
        else:
          new_line += line[i]
          i += 1
      processed_lines.append(new_line)
  
  return '\n'.join(processed_lines)