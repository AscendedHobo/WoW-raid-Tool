import csv
import re
import sys
from pathlib import Path

# Get the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Accept input log file from command-line argument
if len(sys.argv) < 2:
    print("Error: No log file provided. Usage: python script.py <log_file_path>")
    sys.exit(1)

log_file_path = Path(sys.argv[1])

# Define the output filtered log CSV file path
floats_csv_path = script_dir / "combat_log_with_floats.csv"

# List of metadata event types to exclude
excluded_events = {"COMBAT_LOG_VERSION", "MAP_CHANGE", "COMBATANT_INFO"}

# List of encounter tracking, death, and spell aura events to keep
included_events = {"ENCOUNTER_START", "ENCOUNTER_END", "UNIT_DIED", "SPELL_AURA_APPLIED", 
                  "SPELL_AURA_REMOVED", "SPELL_AURA_REFRESH"}

# Function to process aura events into structured format
def process_aura_event(timestamp, event_fields):
    try:
        # Extract relevant fields from the aura event
        event_type = event_fields[0]
        source_guid = event_fields[1]
        source_name = event_fields[2].strip('"')  # Remove quotes
        dest_guid = event_fields[5]
        dest_name = event_fields[6].strip('"')    # Remove quotes
        spell_id = event_fields[9]
        spell_name = event_fields[10].strip('"')  # Remove quotes
        aura_type = event_fields[-1]              # BUFF or DEBUFF
        
        # Return structured format
        return [
            timestamp,
            event_type,
            dest_name,      # Destination player name
            spell_id,
            spell_name,
            aura_type
        ]
    except (IndexError, Exception) as e:
        print(f"Error processing aura event: {e}")
        print(f"Event fields: {event_fields}")
        return None

# Read the combat log and filter lines
filtered_data = []

# Regex pattern to match only floating-point numbers (must have a decimal)
float_pattern = re.compile(r"[-+]?[0-9]*\.[0-9]+")

# Read and process the combat log file
if log_file_path.exists():  # Check if the file exists
    with log_file_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            # Ensure the line has content
            line = line.strip()
            if len(line) < 25:  # Skip malformed lines
                continue
            
            # Split on the first space after the timestamp
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
                
            timestamp_part = parts[0].strip()
            event_part = parts[1].strip()
            
            # Parse the event part as CSV
            event_fields = next(csv.reader([event_part], delimiter=','))
            event_type = event_fields[0].strip()
            
            # Skip explicitly excluded events
            if event_type in excluded_events:
                continue
            
            # Handle aura events specially
            if event_type in {"SPELL_AURA_APPLIED", "SPELL_AURA_REMOVED", "SPELL_AURA_REFRESH"}:
                processed_event = process_aura_event(timestamp_part, event_fields)
                if processed_event:
                    filtered_data.append(processed_event)
                continue
                
            # Handle other included events
            if event_type in included_events:
                filtered_data.append([timestamp_part] + event_fields)
                continue
                
            # Use regex to check if the event part contains floating-point numbers
            if float_pattern.search(event_part):
                filtered_data.append([timestamp_part] + event_fields)

    # Define headers for the CSV file
    headers = ["Timestamp", "Event Type", "Destination Player", "Spell ID", "Spell Name", "Aura Type"]

    # Save filtered lines to a CSV file
    with floats_csv_path.open("w", encoding="utf-8", newline='') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)  # Write headers
        writer.writerows(filtered_data)

    print(f"Combat log lines containing floats, death events, and spell auras saved to: {floats_csv_path}")
else:
    print(f"Error: Log file not found at {log_file_path}")
