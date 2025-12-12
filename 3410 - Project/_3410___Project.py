# ECED3410 - Group 3 Project
# Alice Balser - B00954620
# Connor McDonald - B00820907

import json
import re
from datetime import datetime
from tkinter import SE, SEL

class Database:

    def __init__(self):
        self.records = []
        self.userType = "General"

    def pilotStats(self):
        print("\n=== Pilot Statistics ===")
        print("Type 0 at any time to return.\n")

        # Step 1 — Ask for pilotID
        pilotID = input("Enter pilotID (AA1234): ").strip()
        if pilotID == "0":
            return

        # Step 2 — Collect all flights for this pilot
        flights = [r for r in self.records if r["pilotID"] == pilotID]

        if len(flights) == 0:
            print("\nThe pilot requested does not exist in the database.\n")
            return

        # Step 3 — Sort flights by departureDate (earliest → latest)
        def parse_date(d):
            return datetime.strptime(d, "%H:%M %d/%m/%Y")

        flights_sorted = sorted(flights, key=lambda r: parse_date(r["departureDate"]))

        first_flight_date = flights_sorted[0]["departureDate"]
        last_flight_date  = flights_sorted[-1]["departureDate"]

        first_dt = parse_date(first_flight_date)
        last_dt  = parse_date(last_flight_date)

        delta = last_dt - first_dt

        # Step 4 — Collect airline list
        airlines = sorted({r["airline"] for r in flights})

        # Step 5 — Print results
        print(f"\nPilot: {pilotID}")
        print("-----------------------------------")
        print(f"Total Flights: {len(flights)}")
        print(f"Career Length: {delta.days} days")
        print(f"First Flight: {first_flight_date}")
        print(f"Last Flight: {last_flight_date}\n")

        print(f"Airlines flown for ({len(airlines)}):")
        for a in airlines:
            print(f"- {a}")

        print()  # spacing


    def removeRecord(self):
        print("\n=== Delete Flight Record ===")
        print("Type 0 at any time to return.\n")

        # STEP 1 — Ask for ID
        searchedID = input("Enter a flightID to delete (FLT######): ").strip()

        if searchedID == "0":
            return

        # STEP 2 — Search for the record
        record = None
        for r in self.records:
            if r["flightID"] == searchedID:
                record = r
                break

        if record is None:
            print("\nRecord does not exist.\n")
            return

        # STEP 3 — Display matching record
        print("\nMatching flight found:")
        self.print_record_simple(record)

        # STEP 4 — Confirmation loop
        while True:
            answer = input("Is this the record you want to delete? (Y/N/0): ").strip().upper()

            if answer == "0":
                print("\nDeletion cancelled.\n")
                return

            if answer == "Y":
                # STEP 5 — Delete record
                self.records.remove(record)

                # STEP 6 — Auto-save after delete
                try:
                    with open("flybase.json", "w") as f:
                        json.dump(self.records, f, indent=4)
                    print("\nRecord deleted and saved to file.\n")
                except Exception as e:
                    print("\nRecord deleted in memory, but FAILED to save to file:")
                    print(e, "\n")

                return

            if answer == "N":
                print("\nDeletion cancelled.\n")
                return

            print("Please enter Y, N, or 0.\n")

    # ---------------------------
    # Strict Validation Functions
    # ---------------------------

    def _validate_mandatory_fields(self, rec):
        required = [
            "flightType", "pilotID", "airline",
            "departureDate", "departureLocation",
            "arrivalDate", "arrivalLocation",
            "aircraftID", "flightID", "aircraftModel"
        ]

        for field in required:
            if field not in rec or rec[field] == "":
                print(f"Error: Missing required field '{field}'. Skipping record.")
                return False
        return True


    def _validate_flightType(self, rec):
        valid_types = ["public", "private", "cargo", "military"]
        if rec["flightType"] not in valid_types:
            print(f"Error ({rec.get('flightID', 'UNKNOWN')}): Invalid flightType '{rec['flightType']}'.")
            return False
        return True


    def _validate_pilotID(self, rec):
        pattern = r"^[A-Za-z]{2}\d{4}$"
        if not re.match(pattern, rec["pilotID"]):
            print(f"Error ({rec.get('flightID')}): Invalid pilotID '{rec['pilotID']}'. Must be 2 letters + 4 digits.")
            return False
        return True

    def _validate_flightID(self, rec, ignore_rec=None):
        fid = rec["flightID"]

        # Basic format constraint
        if not fid.startswith("FLT") or len(fid) != 9 or not fid[3:].isdigit():
            print("Invalid flightID format (must be FLT followed by 6 digits).")
            return False

        # Duplicate detection
        for r in self.records:
            if r is ignore_rec:
                continue  # Skip comparing with itself
            if r["flightID"] == fid:
                print(f"Error: flightID '{fid}' already exists.")
                return False

        return True



    def _validate_aircraftID(self, rec):
        pattern = r"^[A-Za-z0-9]{6}$"
        if not re.match(pattern, rec["aircraftID"]):
            print(f"Error ({rec.get('flightID')}): Invalid aircraftID '{rec['aircraftID']}'. Must be 6 chars.")
            return False
        return True


    def _validate_datetime(self, rec):
        for field in ["departureDate", "arrivalDate"]:
            try:
                datetime.strptime(rec[field], "%H:%M %d/%m/%Y")
            except:
                print(f"Error ({rec.get('flightID')}): '{field}' must follow 'HH:MM DD/MM/YYYY'.")
                return False
        return True


    def _validate_conditional_fields(self, rec):
        ftype = rec["flightType"]

        has_passengers = "passengers" in rec
        has_cargo = "cargoWeight" in rec
        has_mission = "mission" in rec

        if ftype == "public":
            if not has_passengers:
                print(f"Error ({rec['flightID']}): Public flight missing passengers.")
                return False
            if has_cargo or has_mission:
                print(f"Error ({rec['flightID']}): Public flight must not include cargoWeight or mission.")
                return False

        elif ftype == "cargo":
            if not has_cargo:
                print(f"Error ({rec['flightID']}): Cargo flight missing cargoWeight.")
                return False
            if has_passengers or has_mission:
                print(f"Error ({rec['flightID']}): Cargo flight must not include passengers or mission.")
                return False

        elif ftype == "military":
            if not has_mission:
                print(f"Error ({rec['flightID']}): Military flight missing mission.")
                return False
            if has_passengers or has_cargo:
                print(f"Error ({rec['flightID']}): Military flight must not include passengers or cargoWeight.")
                return False

        elif ftype == "private":
            if has_passengers or has_cargo or has_mission:
                print(f"Error ({rec['flightID']}): Private flights must not contain passengers, cargoWeight, or mission.")
                return False

        return True

    def print_record_simple(self, rec):
        # Ordered keys
        keys = [
            "flightID",
            "flightType",
            "pilotID",
            "airline",
            "departureDate",
            "departureLocation",
            "arrivalDate",
            "arrivalLocation",
            "aircraftID",
            "aircraftModel"
        ]

        # Conditional key
        if rec["flightType"] == "public":
            keys.append("passengers")
        elif rec["flightType"] == "cargo":
            keys.append("cargoWeight")
        elif rec["flightType"] == "military":
            keys.append("mission")

        # Print field: value
        for k in keys:
            print(f"{k}: {rec[k]}")
        print()


    def updateRecord(self):
        print("\n=== Update Existing Flight Record ===")
        print("Type 0 at any time to return to menu.\n")

        # -------------------------
        # Ask for flightID
        # -------------------------
        while True:
            fid = input("Enter flightID to update (FLT######): ").strip()
            if fid == "0":
                return

            # Find record
            rec = None
            for r in self.records:
                if r["flightID"] == fid:
                    rec = r
                    break

            if rec is None:
                print("Flight ID not found. Try again.\n")
                continue

            # Print record in table form
            print("\nMatching flight found:")
            self.print_record_simple(rec)

            confirm = input("Is this the correct flight? (yes/no/0): ").strip().lower()
            if confirm == "0":
                return
            if confirm == "yes":
                break
            else:
                print("Okay, try again.\n")

        # -------------------------
        # Build ordered list of fields
        # -------------------------
        fields = [
            "flightID",
            "flightType",
            "pilotID",
            "airline",
            "departureDate",
            "departureLocation",
            "arrivalDate",
            "arrivalLocation",
            "aircraftID",
            "aircraftModel"
        ]

        # Conditional field
        if rec["flightType"] == "public":
            fields.append("passengers")
        elif rec["flightType"] == "cargo":
            fields.append("cargoWeight")
        elif rec["flightType"] == "military":
            fields.append("mission")

        # Print field list with numbers
        print("\nSelect fields to update:")
        for i, f in enumerate(fields, start=1):
            print(f"{i}: {f}")

        print("0: Return to menu")

        # -------------------------
        # Get field selections
        # -------------------------
        sel = input("\nEnter field numbers (comma separated): ").strip()
        if sel == "0":
            return

        try:
            selected = [int(x.strip()) for x in sel.split(",")]
        except:
            print("Invalid input.")
            return

        # Validate selection numbers
        for s in selected:
            if s < 1 or s > len(fields):
                print("Invalid field number:", s)
                return

        # -------------------------
        # Update each selected field
        # -------------------------
        for s in selected:
            field = fields[s - 1]
            current_value = rec[field] if field in rec else ""

            # Prompt
            new_val = input(f"Enter new value for {field} (current: {current_value}): ").strip()
            if new_val == "":
                print("Empty input not allowed.")
                return
            if new_val == "0":
                return

            # Handle field-specific formatting
            temp = rec.copy()
            temp[field] = new_val

            # Special handling for conditional logic when flightType changes
            if field == "flightType":
                new_ftype = new_val.lower()
                if new_ftype not in ["public", "private", "cargo", "military"]:
                    print("Invalid flightType.")
                    return

                # Remove old conditional fields
                for c in ["passengers", "cargoWeight", "mission"]:
                    if c in temp:
                        del temp[c]

                # Ask for new conditional field  
                if new_ftype == "public":
                    val = input("Enter passengers: ").strip()
                    if not val.isdigit():
                        print("Invalid passengers.")
                        return
                    temp["passengers"] = int(val)

                elif new_ftype == "cargo":
                    val = input("Enter cargoWeight (tonnes): ").strip()
                    try:
                        temp["cargoWeight"] = float(val)
                    except:
                        print("Invalid cargoWeight.")
                        return

                elif new_ftype == "military":
                    val = input("Enter mission: ").strip()
                    temp["mission"] = val

                # private → no conditional fields

            # Validation using all existing validators
            if (
                self._validate_mandatory_fields(temp)
                and self._validate_flightType(temp)
                and self._validate_pilotID(temp)
                and self._validate_flightID(temp, ignore_rec=rec)
                and self._validate_aircraftID(temp)
                and self._validate_datetime(temp)
                and self._validate_conditional_fields(temp)
            ):
                rec.clear()
                rec.update(temp)
                print(f"Updated {field} successfully.\n")
            else:
                print(f"Update for {field} failed validation.")
                return

        print("Record updated! (Remember to save.)\n")



    # ---------------------------
    # addRecord (Bulk Mode Only)
    # ---------------------------

    def addRecord(self, batch_list):
        """
        Accepts a list of record dictionaries.
        Validates each record strictly.
        Only inserts valid records.
        """

        if not isinstance(batch_list, list):
            print("Error: addRecord expects a LIST of records.")
            return

        for rec in batch_list:

            # 1. Mandatory fields
            if not self._validate_mandatory_fields(rec):
                continue

            # 2. Format validation
            if not self._validate_flightType(rec): continue
            if not self._validate_pilotID(rec): continue
            if not self._validate_flightID(rec): continue
            if not self._validate_aircraftID(rec): continue
            if not self._validate_datetime(rec): continue

            # 3. Conditional validation
            if not self._validate_conditional_fields(rec):
                continue

            # If all checks pass → insert record
            self.records.append(rec)

        # ---------------------------
    # Add Single Record (Interactive Mode)
    # ---------------------------

    def addSingleRecord(self):
        print("\n=== Add Single Flight Record ===")
        print("Type 0 at any time to cancel.\n")

        rec = {}

        # Helper function for field prompts
        def _prompt_field(prompt, validator):
            while True:
                value = input(prompt).strip()
                if value == "0":
                    print("Cancelled. Returning to menu.")
                    return None
                if value == "":
                    print("Input cannot be empty.")
                    continue
                if validator(value):
                    return value

        # -------------------------
        # 1. flightID FIRST
        # -------------------------
        def validate_fid(v):
            test = {"flightID": v}
            return self._validate_flightID(test)

        fid = _prompt_field("flightID (FLTxxxxxx): ", validate_fid)
        if fid is None: return
        rec["flightID"] = fid

        # -------------------------
        # 2. flightType
        # -------------------------
        def validate_ftype(v):
            if v in ["public", "private", "cargo", "military"]:
                return True
            print("Invalid flightType.")
            return False

        ftype = _prompt_field("flightType (public/private/cargo/military): ", validate_ftype)
        if ftype is None: return
        rec["flightType"] = ftype

        # -------------------------
        # 3. pilotID
        # -------------------------
        def validate_pilot(v):
            test = {"pilotID": v}
            return self._validate_pilotID(test)

        pilot = _prompt_field("pilotID (AA1234): ", validate_pilot)
        if pilot is None: return
        rec["pilotID"] = pilot

        # -------------------------
        # 4. airline
        # -------------------------
        airline = _prompt_field("airline: ", lambda v: True)
        if airline is None: return
        rec["airline"] = airline

        # -------------------------
        # 5. departureDate
        # -------------------------
        def validate_date(v):
            try:
                datetime.strptime(v, "%H:%M %d/%m/%Y")
                return True
            except:
                print("Invalid date format. Use HH:MM DD/MM/YYYY.")
                return False

        dep_date = _prompt_field("departureDate (HH:MM DD/MM/YYYY): ", validate_date)
        if dep_date is None: return
        rec["departureDate"] = dep_date

        # -------------------------
        # 6. departureLocation
        # -------------------------
        dep_loc = _prompt_field("departureLocation: ", lambda v: True)
        if dep_loc is None: return
        rec["departureLocation"] = dep_loc

        # -------------------------
        # 7. arrivalDate
        # -------------------------
        arr_date = _prompt_field("arrivalDate (HH:MM DD/MM/YYYY): ", validate_date)
        if arr_date is None: return
        rec["arrivalDate"] = arr_date

        # -------------------------
        # 8. arrivalLocation
        # -------------------------
        arr_loc = _prompt_field("arrivalLocation: ", lambda v: True)
        if arr_loc is None: return
        rec["arrivalLocation"] = arr_loc

        # -------------------------
        # 9. aircraftID
        # -------------------------
        def validate_aircraft(v):
            test = {"aircraftID": v}
            return self._validate_aircraftID(test)

        aircraft = _prompt_field("aircraftID (6 chars): ", validate_aircraft)
        if aircraft is None: return
        rec["aircraftID"] = aircraft

        # -------------------------
        # 10. aircraftModel
        # -------------------------
        model = _prompt_field("aircraftModel: ", lambda v: True)
        if model is None: return
        rec["aircraftModel"] = model

        # -------------------------
        # 11. Conditional Fields
        # -------------------------
        if ftype == "public":
            def validate_pass(v):
                if v.isdigit(): return True
                print("Passengers must be an integer.")
                return False

            passengers = _prompt_field("passengers: ", validate_pass)
            if passengers is None: return
            rec["passengers"] = int(passengers)

        elif ftype == "cargo":
            def validate_cargo(v):
                try:
                    float(v)
                    return True
                except:
                    print("cargoWeight must be a number.")
                    return False

            cargo = _prompt_field("cargoWeight (tonnes): ", validate_cargo)
            if cargo is None: return
            rec["cargoWeight"] = float(cargo)

        elif ftype == "military":
            mission = _prompt_field("mission: ", lambda v: True)
            if mission is None: return
            rec["mission"] = mission

        # private → no conditional fields

        # -------------------------
        # Final Validation
        # -------------------------
        print("\nValidating...")

        if (
            self._validate_mandatory_fields(rec)
            and self._validate_flightType(rec)
            and self._validate_pilotID(rec)
            and self._validate_flightID(rec)
            and self._validate_aircraftID(rec)
            and self._validate_datetime(rec)
            and self._validate_conditional_fields(rec)
        ):
            self.records.append(rec)
            print(f"\nRecord {rec['flightID']} added successfully.")
        else:
            print("\nRecord failed validation. Not added.")

    def airlineStats(self):
        print("\n=== Airline Statistics ===")
        print("Type 0 at any time to return.\n")

        # Step 1 — Ask for airline name
        airline_input = input("Enter airline name: ").strip()
        if airline_input == "0":
            return

        # Normalize for case-insensitive matching
        airline_normalized = airline_input.lower()

        # Gather all flights for this airline
        matching = [rec for rec in self.records
                    if rec["airline"].lower() == airline_normalized]

        if len(matching) == 0:
            print("That airline does not exist within the database.\n")
            return

        # Step 2 — Ask user for stats type
        while True:
            print("\nSelect statistic:")
            print("1. Total flights (all time)")
            print("2. Total flights in a given year")
            print("0. Return to Statistics Menu")

            choice = input("Choice: ").strip()

            if choice == "0":
                return

            # All-time total
            elif choice == "1":
                total = len(matching)
                print(f"\n{airline_input} – Total Flights (All Time): {total}\n")
                return

            # Year-specific total
            elif choice == "2":
                year = input("Enter year (YYYY): ").strip()
                if year == "0":
                    return

                # Validate year format
                if not (year.isdigit() and len(year) == 4):
                    print("Invalid year format. Try again.\n")
                    continue

                # Extract flights where departureDate ends with "/YYYY"
                year_matches = []
                for rec in matching:
                    date = rec["departureDate"]
                    # departureDate ends in DD/MM/YYYY → last 4 chars are the year
                    if date[-4:] == year:
                        year_matches.append(rec)

                print(f"\n{airline_input} – Flights in {year}: {len(year_matches)}\n")
                return

            else:
                print("Invalid choice, try again.\n")

    def generalStats(self):
        while True:
            print("\n=== General Statistics ===")
            print("0. Return to Statistics Menu")
            print("1. Total Flights in Database")
            print("2. Total Flights by Given Year")
            print("3. Total Flights by Flight Type")

            choice = input("Enter your choice: ").strip()

            # Return
            if choice == "0":
                return

            # Total flights (all time)
            elif choice == "1":
                total = len(self.records)
                print(f"\nTotal Flights in Database: {total}\n")

            # Total flights by year
            elif choice == "2":
                year = input("Enter year (YYYY): ").strip()
                if year == "0":
                    continue

                if not (year.isdigit() and len(year) == 4):
                    print("Invalid year format.\n")
                    continue

                matches = [rec for rec in self.records
                           if rec["departureDate"][-4:] == year]

                print(f"\nTotal Flights in {year}: {len(matches)}\n")

            # Total flights by flight type
            elif choice == "3":
                ftype = input("Enter flight type (public, private, cargo, military): ").strip().lower()
                if ftype == "0":
                    continue

                if ftype not in ("public", "private", "cargo", "military"):
                    print("Invalid flight type.\n")
                    continue

                matches = [rec for rec in self.records
                           if rec["flightType"].lower() == ftype]

                print(f"\nTotal {ftype} flights: {len(matches)}\n")

            else:
                print("Invalid choice, try again.\n")

    def modelStats(self):
        while True:
            print("\n=== Model Statistics ===")
            print("0. Return to Statistics Menu")
            print("1. Average Passengers by Aircraft Model")
            print("2. Average Cargo Weight by Aircraft Model")

            choice = input("Enter your choice: ").strip()

            if choice == "0":
                return

            # Average passengers
            elif choice == "1":
                model = input("Enter aircraft model: ").strip()
                if model == "0":
                    continue

                model_norm = model.lower()

                # Collect only public flights with passenger counts
                flights = [
                    rec for rec in self.records
                    if rec["aircraftModel"].lower() == model_norm
                    and rec["flightType"].lower() == "public"
                    and "passengers" in rec
                ]

                if len(flights) == 0:
                    print("No passenger data exists for that aircraft model.\n")
                    continue

                total = sum(rec["passengers"] for rec in flights)
                avg = total / len(flights)

                print(f"\nAverage Passengers for {model}: {avg:.2f}\n")

            # Average cargo weight
            elif choice == "2":
                model = input("Enter aircraft model: ").strip()
                if model == "0":
                    continue

                model_norm = model.lower()

                # Collect only cargo flights with cargoWeight
                flights = [
                    rec for rec in self.records
                    if rec["aircraftModel"].lower() == model_norm
                    and rec["flightType"].lower() == "cargo"
                    and "cargoWeight" in rec
                ]

                if len(flights) == 0:
                    print("No cargo weight data exists for that aircraft model.\n")
                    continue

                total = sum(rec["cargoWeight"] for rec in flights)
                avg = total / len(flights)

                print(f"\nAverage Cargo Weight for {model}: {avg:.2f} tonnes\n")

            else:
                print("Invalid choice, try again.\n")


    def statisticsMenu(self):
        while True:
            print("\n=== Statistics Menu ===")
            print("0. Return to Main Menu")
            print("1. Pilot Statistics")
            print("2. Airline Statistics")
            print("3. General Statistics")
            print("4. Model Statistics")

            choice = input("Enter your choice: ").strip()

            if choice == "0":
                return

            elif choice == "1":
                self.pilotStats()

            elif choice == "2":
                self.airlineStats()

            elif choice == "3":
                self.generalStats()

            elif choice == "4":
                self.modelStats()

            else:
                print("Invalid choice, try again.\n")

    # ---------------------------
    # Save / Load
    # ---------------------------

    def saveToFile(self, filename="flybase.json"):
        try:
            with open(filename, "w") as f:
                json.dump(self.records, f, indent=4)
            print(f"Saved {len(self.records)} records to {filename}.")
        except Exception as e:
            print("Error saving file:", e)


    def appendToFile(self, filename="flybase.json"):
        try:
            with open(filename, "r") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = []
        except FileNotFoundError:
            existing = []

        combined = existing + self.records

        # Deduplicate by flightID
        unique = {}
        for rec in combined:
            unique[rec["flightID"]] = rec

        with open(filename, "w") as f:
            json.dump(list(unique.values()), f, indent=4)

        print(f"Appended {len(self.records)} new records (total {len(unique)}) to {filename}.")



    def loadFromFile(self, filename="flybase.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("No existing database found. Starting with empty set.")
            return

        # Validate each loaded record before adding
        valid_count = 0
        for rec in data:
            if (
                self._validate_mandatory_fields(rec)
                and self._validate_flightType(rec)
                and self._validate_pilotID(rec)
                and self._validate_flightID(rec)
                and self._validate_aircraftID(rec)
                and self._validate_datetime(rec)
                and self._validate_conditional_fields(rec)
            ):
                self.records.append(rec)
                valid_count += 1
            else:
                print(f"Warning: Invalid record in JSON file skipped (flightID={rec.get('flightID')}).")

        print(f"Loaded {valid_count} valid records from {filename}.")

def main_menu():
    db = Database()


def main_menu():
    db = Database()

    while True:
        print("\n=== FlyBase Database Menu ===")
        print("0. Exit")
        print("1. Load from flybase.json")
        print("2. Add single flight record")
        print("3. Add records (bulk)")
        print("4. Save to flybase.json")
        print("5. Print loaded records (TEMP)")
        print("6. Update existing flight record")
        print("7. Delete a flight record")
        print("8. Statistics Menu")

        choice = input("Enter your choice: ").strip()

        # -------------------------
        # Exit
        # -------------------------
        if choice == "0":
            print("\nExiting program.")
            break

        # -------------------------
        # Load
        # -------------------------
        elif choice == "1":
            print("\nLoading data...")
            db.loadFromFile()

        elif choice == "2":
            print("\nSingle Add Mode Selected.")
            db.addSingleRecord()      # user enters the fields
            db.appendToFile()         # automatically append-save
            db.records = []           # optional: clear after saving


        elif choice == "3":
            print("\nBulk Add Mode Selected.")
            print("Enter flight records as a JSON list.")
            print("Type END when done.\n")

            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)

            try:
                batch = json.loads("\n".join(lines))
                if isinstance(batch, list):
                    print("\nAdding records...")
                    db.addRecord(batch)

                    # AUTOMATIC APPEND SAVE HERE 
                    db.appendToFile()

                    # Optional: clear added batch from memory after append
                    db.records = []
                else:
                    print("Error: Input must be a JSON LIST.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON formatting.")


        # -------------------------
        # Save
        # -------------------------
        elif choice == "4":
            print("\nSaving database...")
            db.saveToFile()

        # -------------------------
        # Print Records
        # -------------------------
        elif choice == "5":
            print_records(db)

        elif choice == "6":
           db.updateRecord()

        elif choice == "7":
           db.removeRecord()

        elif choice == "8":
            db.statisticsMenu()


        # -------------------------
        # Invalid Option
        # -------------------------
        else:
            print("Invalid choice, try again.")


def print_records(db):
    if not db.records:
        print("\nNo records in memory.")
        return
    
    print("\n=== CURRENT RECORDS IN MEMORY ===")
    for rec in db.records:
        print(json.dumps(rec, indent=4))
        print("----------------------------------")


if __name__ == "__main__":
    main_menu()
