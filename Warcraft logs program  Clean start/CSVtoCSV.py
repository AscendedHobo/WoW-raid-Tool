import csv
import os
from pathlib import Path
from datetime import datetime, timedelta

def load_csv(file_name, output_name):
    '''
    Load a CSV file, track encounters, calculate relative fight time,
    and track unit positions for UNIT_DIED events.
    '''
    
    # Define the base directory dynamically (current script directory)
    base_dir = Path(__file__).resolve().parent

    # Construct full paths
    file_path = base_dir / file_name
    output_path = base_dir / output_name

    try:
        with file_path.open(mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            all_rows = []
            encounter_durations = {}
            header = [
                "timestamp", "event type", "Damage source", "Spell destination", 
                "spell id", "spell name", "X coord", "Y coord", "Facing direction", 
                "Aura type", "map id", "encounter name", "encounter id", 
                "relative fight time (s)", "unit died sequence"
            ]
            all_rows.append(header)
            
            current_encounter_id = 0
            current_encounter_start = None
            current_encounter_end = None
            unit_died_counter = 0
            unit_last_positions = {}
            
            group1_events = ["RANGE_DAMAGE", "SPELL_DAMAGE", "SPELL_PERIODIC_DAMAGE",
                             "SPELL_HEAL", "SPELL_PERIODIC_HEAL", "SPELL_CAST_SUCCESS"]
            group2_events = ["SWING_DAMAGE", "SWING_DAMAGE_LANDED"]
            source_events = ["SPELL_CAST_SUCCESS", "SWING_DAMAGE"]
            destination_events = ["RANGE_DAMAGE", "SPELL_DAMAGE", "SPELL_PERIODIC_DAMAGE",
                                  "SPELL_HEAL", "SPELL_PERIODIC_HEAL", "SWING_DAMAGE_LANDED"]
            
            for row in reader:
                if not row:
                    continue
                
                timestamp = row[0].strip()
                event_type = row[1]
                
                try:
                    event_time = datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S.%f")
                except ValueError:
                    event_time = None
                
                if event_type == "ENCOUNTER_START":
                    current_encounter_id += 1
                    current_encounter_start = event_time
                    current_encounter_end = None
                    unit_died_counter = 0
                    unit_last_positions = {}
                    
                    map_id = row[2]
                    encounter_name = row[4]
                    new_row = [
                        timestamp, event_type, "", "", "", "", "", "", "", "", 
                        map_id, encounter_name, current_encounter_id, "0.000", str(unit_died_counter)
                    ]
                    all_rows.append(new_row)
                
                elif event_type == "ENCOUNTER_END":
                    current_encounter_end = event_time
                    map_id = row[2]
                    encounter_name = row[4]
                    relative_time = 0.0
                    if current_encounter_start and current_encounter_end:
                        encounter_duration = (current_encounter_end - current_encounter_start).total_seconds()
                        relative_time = encounter_duration
                    
                    new_row = [
                        timestamp, event_type, "", "", "", "", "", "", "", "", 
                        map_id, encounter_name, current_encounter_id, 
                        f"{relative_time:.3f}", str(unit_died_counter)
                    ]
                    all_rows.append(new_row)
                    encounter_durations[current_encounter_id] = relative_time
                
                if event_type in group1_events + group2_events:
                    try:
                        if event_type in group1_events:
                            x_col, y_col, facing_col = 27, 28, 30
                        else:
                            x_col, y_col, facing_col = 24, 25, 27

                        if event_type in source_events:
                            unit = row[3]
                        else:
                            unit = row[7]

                        x_coord = row[x_col]
                        y_coord = row[y_col]
                        facing_direction = row[facing_col]

                        try:
                            float(x_coord)
                            float(y_coord)
                            unit_last_positions[unit] = (x_coord, y_coord, facing_direction)
                        except (ValueError, IndexError):
                            pass
                    except (IndexError, KeyError, ValueError):
                        pass
                
                if current_encounter_start and event_time:
                    relative_time = (event_time - current_encounter_start).total_seconds()
                else:
                    relative_time = 0.0
                
                if event_type == "UNIT_DIED":
                    try:
                        spell_dest = row[7]
                        if spell_dest.endswith(("-EU", "-US")):
                            unit_died_counter += 1
                            x_coord, y_coord, facing_direction = unit_last_positions.get(spell_dest, ("", "", ""))
                            new_row = [
                                timestamp, event_type, "", spell_dest, "", "", 
                                x_coord, y_coord, facing_direction, "", "", "", current_encounter_id, 
                                f"{relative_time:.3f}", str(unit_died_counter)
                            ]
                            all_rows.append(new_row)
                    except IndexError:
                        new_row = [
                            timestamp, event_type, "", "", "", "", 
                            "", "", "", "", "", "", current_encounter_id, 
                            f"{relative_time:.3f}", str(unit_died_counter)
                        ]
                        all_rows.append(new_row)
                
                else:
                    if event_type in ["SPELL_AURA_REMOVED", "SPELL_AURA_REFRESH", "SPELL_AURA_APPLIED"]:
                        spell_dest = row[2]
                        spell_id = row[3]
                        spell_name = row[4]
                        aura_type = row[5]
                        x_coord, y_coord, facing_direction = unit_last_positions.get(spell_dest, ("", "", ""))
                        new_row = [
                            timestamp, event_type, "", spell_dest, spell_id, spell_name, 
                            x_coord, y_coord, facing_direction, aura_type, "", "", current_encounter_id, 
                            f"{relative_time:.3f}", str(unit_died_counter)
                        ]
                        all_rows.append(new_row)
                    
                    elif event_type in ["RANGE_DAMAGE", "SPELL_CAST_SUCCESS", "SPELL_HEAL", 
                                        "SPELL_DAMAGE", "SPELL_PERIODIC_DAMAGE", "SPELL_PERIODIC_HEAL"]:
                        damage_source = row[3]
                        spell_dest = row[7]
                        spell_id = row[10]
                        spell_name = row[11]
                        x_coord = row[27]
                        y_coord = row[28]
                        facing_direction = row[30]
                        new_row = [
                            timestamp, event_type, damage_source, spell_dest, spell_id, 
                            spell_name, x_coord, y_coord, facing_direction, "", 
                            "", "", current_encounter_id, f"{relative_time:.3f}", str(unit_died_counter)
                        ]
                        all_rows.append(new_row)
                    
                    elif event_type in ["SWING_DAMAGE", "SWING_DAMAGE_LANDED"]:
                        damage_source = row[3]
                        spell_dest = row[7]
                        spell_id = row[10]
                        x_coord = row[24]
                        y_coord = row[25]
                        facing_direction = row[27]
                        new_row = [
                            timestamp, event_type, damage_source, spell_dest, spell_id, 
                            "", x_coord, y_coord, facing_direction, "", "", "", 
                            current_encounter_id, f"{relative_time:.3f}", str(unit_died_counter)
                        ]
                        all_rows.append(new_row)
            
            # Process to filter encounters and adjust IDs
            invalid_encounters = {enc_id for enc_id, duration in encounter_durations.items() if duration <= 35}
            filtered_data_rows = []
            for row in all_rows[1:]:  # Skip header
                enc_id = row[12]
                if enc_id not in invalid_encounters:
                    filtered_data_rows.append(row)
            
            valid_ids = sorted({row[12] for row in filtered_data_rows})
            id_mapping = {old_id: new_id for new_id, old_id in enumerate(valid_ids, start=1)}
            
            for row in filtered_data_rows:
                old_id = row[12]
                row[12] = id_mapping.get(old_id, old_id)
            
            processed_rows = [all_rows[0]] + filtered_data_rows
            
            with output_path.open(mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(processed_rows)
        
        print(f"Filtered CSV successfully created: {output_path}")
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    input_file = "combat_log_with_floats.csv"
    output_file = "filtered_combat_log.csv"
    load_csv(input_file, output_file)