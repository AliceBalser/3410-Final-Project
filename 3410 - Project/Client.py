# ECED3410 - Group 3 Project
# Alice Balser - B00954620
# Connor McDonald - B00938421

from getpass import getpass
from Repository import Repository
from Server import Server
from datetime import datetime
import shutil

class Client:

    def __init__(self):
        """
        Initialize the Client UI, create Repository and Server objects, and set the default user type.

        Returns:
            None
        """

        self.userType = "General"
        self.repo = Repository()
        self.server = Server(self.repo)

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------

    def login(self):
        """
        Prompt the user for an airline password and switch between General and Airline user modes.

        Returns:
            None
        """

        pwd = getpass("Enter Airline Password (or press ENTER for General): ")

        if pwd == "admin123":

            self.userType = "Airline"

            print("\nLogged in as Airline User.\n")

        else:

            self.userType = "General"

            print("\nLogged in as General User.\n")

    # ---------------------------------------------------------
    # MAIN MENU
    # ---------------------------------------------------------

    def mainMenu(self):
        """
        Display the main menu loop, handle top-level navigation, and dispatch user actions.
        
        Returns:
            None
        """

        self.login()

        while True:

            print("\n=== Main Menu ===")
            print("0. Exit")
            print("1. Load Database")
            print("2. Records Menu")
            print("3. Statistics Menu")

            if self.userType == "General":

                print("9. Sign in as Airline User")

            if self.userType == "Airline":

                print("4. Add Single Record")
                print("5. Save to File")
                print("6. Update Record")
                print("7. Delete Record")

            choice = input("Choose: ")

            # -----------------------------------------------------
            # BASIC OPTIONS
            # -----------------------------------------------------

            if choice == "0":

                return

            elif choice == "1":  

                count = self.repo.loadFromFile()

                print(f"Loaded {count} records.")

            elif choice == "2":

                self.recordsMenu()

            elif choice == "3":

                self.statisticsMenu()

            # ------------------------------------------------------------
            # AIRLINE USER OPTIONS (Options only visible to Airline Users)
            # ------------------------------------------------------------

            elif choice == "4" and self.userType == "Airline":
                self.addSingle()

            elif choice == "5" and self.userType == "Airline":

                self.repo.saveToFile()

                print("Saved.")

            elif choice == "6" and self.userType == "Airline":

                self.updateRecord()

            elif choice == "7" and self.userType == "Airline":

                self.deleteRecord()


            # -----------------------------------------------------
            # LOGIN FOR GENERAL USER
            # -----------------------------------------------------

            elif choice == "9" and self.userType == "General":

                self.login()

            # If the user is already an Airline User, they do not need to log in again
            else:

                print("Invalid choice.")

    def updateRecord(self):
        """
        UI end of updating an existing flight record.
        Prompts the user for a flightID, displays the current record, 
        collects updated field values, and diverts validation and storage 
        to the Repository and Server layers.

        Returns:
            None
        """

        if self.userType == "General":

            print("\nThis action is restricted to Airline Users.\n")

            return

        print("\n=== Update Existing Flight Record ===")
        print("Type 0 at any time to cancel.\n")

        # STEP 1 — FIND RECORD
        while True:

            fid = input("Enter flightID to update (FLT######): ").strip()

            if fid == "0":

                return

            rec = self.repo.getByFlightID(fid)

            if rec is None:

                print("Flight ID not found. Try again.\n")

                continue

            # Format the record being shown
            print("\nCurrent Record:")
            print(self.server.formatRecord(rec, isAirlineUser=(self.userType == "Airline")))

            confirm = input("\nIs this the correct flight? (y/n/0): ").strip().lower()

            if confirm == "0":

                return

            if confirm == "y":

                break

            print("Retrying...\n")

        # STEP 2 — SELECT FIELDS TO UPDATE
        fields = [
            "flightID", "flightType", "pilotID", "airline",
            "departureDate", "departureLocation",
            "arrivalDate", "arrivalLocation",
            "aircraftID", "aircraftModel"
        ]

        # Handle flightType logic
        if rec["flightType"] == "public":

            fields.append("passengers")

        elif rec["flightType"] == "cargo":

            fields.append("cargoWeight")

        elif rec["flightType"] == "military":

            fields.append("mission")

        print("\nSelect fields to update:")

        for i, f in enumerate(fields, start=1):

            print(f"{i}. {f}")

        print("0. Cancel")

        sel = input("Enter field numbers (comma separated): ").strip()

        if sel == "0":

            return

        try:

            selected = [int(s.strip()) for s in sel.split(",")]

        except:

            print("Invalid input.")

            return

        for s in selected:

            if s < 1 or s > len(fields):

                print(f"Invalid field number: {s}")

                return

        # STEP 3 — EDIT FIELDS
        new_rec = rec.copy()

        for s in selected:

            field = fields[s - 1]

            current = new_rec.get(field, "")

            new_val = input(f"Enter new value for {field} (current: {current}): ").strip()

            if new_val == "0":

                return
            if new_val == "":

                print("Empty value not allowed.")

                return

            new_rec[field] = new_val

            # SPECIAL HANDLING for flightType changes
            if field == "flightType":

                ft = new_val.lower()

                # Wipe old conditional fields
                for c in ["passengers", "cargoWeight", "mission"]:

                    new_rec.pop(c, None)

                # Add appropriate new one
                if ft == "public":

                    p = input("Passengers: ").strip()

                    if not p.isdigit():

                        print("Invalid passengers.")

                        return

                    new_rec["passengers"] = int(p)


                elif ft == "cargo":

                    w = input("Cargo Weight (tonnes): ").strip()

                    try:

                        new_rec["cargoWeight"] = float(w)

                    except:

                        print("Invalid cargoWeight.")

                        return

                elif ft == "military":

                    m = input("Mission: ").strip()
                    new_rec["mission"] = m

        # STEP 4 — VALIDATE & APPLY UPDATE
        success = self.repo.update(rec, new_rec)

        if success:

            print("\nRecord updated successfully!\n")
            self.repo.saveToFile()
        else:

            print("\nUpdate failed, invalid data.\n")

    # ---------------------------------------------------------
    # UI HELPERS
    # ---------------------------------------------------------

    def wrap_cell(self, text, width):
        """
        Wraps a single cell into a list of lines, each line cannot be more than the give width
        
        Parameters:
            text (str): The text content to wrap
            width (int): The maximum width for each wrapped line

        Returns:
            list[str]: A list of wrapped text lines
        """

        text = str(text)

        return [text[i:i+width] for i in range(0, len(text), width)]

    def print_flights_table(self, flights):
        """
        Build and display a formatted table of flight records.
        Automatically hides restricted columns for General users,
        determines column widths, and selects between wide or stacked view depending on terminal size.
        
        Parameters:
            flights (list[dict]): List of flight record dictionaries to display

        Returns:
            None
        """

        # Outline which Headers are associated with sensitive data
        sensitive_columns = {
            "Passenger Count",
            "Mission",
            "Cargo Weight"
        }

        # Headers
        display_headers = [

            "Flight ID",
            "Flight Type",
            "Pilot ID",
            "Airline",
            "Departure Date",
            "Departure Location",
            "Arrival Date",
            "Arrival Location",
            "Aircraft ID",
            "Aircraft Model",
            "Passenger Count",
            "Mission",
            "Cargo Weight"

        ]

        # Mapping of the headers to their field
        key_map = {

            "Flight ID": "flightID",
            "Flight Type": "flightType",
            "Pilot ID": "pilotID",
            "Airline": "airline",
            "Departure Date": "departureDate",
            "Departure Location": "departureLocation",
            "Arrival Date": "arrivalDate",
            "Arrival Location": "arrivalLocation",
            "Aircraft ID": "aircraftID",
            "Aircraft Model": "aircraftModel",
            "Passenger Count": "passengers",
            "Mission": "mission",
            "Cargo Weight": "cargoWeight",

        }

        # if the user is a general user, remove all sensitive data
        if self.userType == "General":

            display_headers = [

                h for h in display_headers 
                if h not in sensitive_columns

            ]

        # Build rows in header order using the dictionary keys
        rows = []

        for rec in flights:

            row = [rec.get(key_map[h], "N/A") for h in display_headers]

            rows.append(row)

       
        # Sizing columns based on Header spacing
        col_widths = [len(h) for h in display_headers]

        # Total width of table with " | " separators (3 chars each)
        sep_width = 3 * (len(display_headers) - 1)
        total_width = sum(col_widths) + sep_width

        terminal_width = shutil.get_terminal_size((100, 20)).columns

        if total_width <= terminal_width:

            # If the table fits within the terminal, show the table
            self.display_table(display_headers, rows, col_widths)

        else:

            # If the table is too wide, prompt the user to choose if they want a stacked format for the records
            print(f"\nThe table is {total_width} characters wide,")
            print(f"but your terminal is only {terminal_width} characters wide.\n")

            print("1. Show normal table anyway (May cause issues)")
            print("2. Use readable stacked format (recommended)")

            ch = input("Choose display format: ").strip()

            match ch:
           
                case "1":

                   self.display_table(display_headers, rows, col_widths)

                case "2":

                   self.display_narrow_table(display_headers, rows)

    def display_table(self, headers, rows, col_widths):
        """
        Render a full-width formatted table using aligned columns.
        Wraps long cell contents by column width and prints row separators.
        
        Parameters:
            headers (list[str]): Column headers
            rows (list[list]): Table rows containing cell values
            col_widths (list[int]): Width allocated for each column

        Returns:
            None
        """

        # Print header
        header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))

        print(header_line)
        print("-" * len(header_line))

        # Print each row
        for row in rows:

            wrapped = [

                self.wrap_cell(row[i], col_widths[i])
                for i in range(len(row))

            ]

            max_height = max(len(w) for w in wrapped)

            for line_index in range(max_height):

                line = []

                for col_index, cell_lines in enumerate(wrapped):

                    text = cell_lines[line_index] if line_index < len(cell_lines) else ""

                    line.append(text.ljust(col_widths[col_index]))

                print(" | ".join(line))

            print("-" * len(header_line))

    def display_narrow_table(self, headers, rows):
        """
        Render records in a stacked vertical layout for narrow terminals 
        Can be used when a full-width table would not fit inside terminal.
        Each record is displayed as key–value pairs.
        
        Parameters:
            headers (list[str]): Column labels
            rows (list[list]): Record values corresponding to each header

        Returns:
            None
        """

        import shutil
        terminal_width = shutil.get_terminal_size((100, 20)).columns

        # Width for the "Header: " label part
        label_width = max(len(h) for h in headers) + 2

        # Width for values
        value_width = max(10, terminal_width - label_width - 1)

        print("\n[Table too wide for this terminal, showing stacked view]\n")

        for row in rows:

            for h, cell in zip(headers, row):

                cell_text = str(cell)

                lines = self.wrap_cell(cell_text, value_width)

                # First line: header + first part of value
                print(f"{h.ljust(label_width)}{lines[0]}")

                # Continuation lines: indent under value column
                for cont in lines[1:]:

                    print(" " * label_width + cont)

            print("-" * terminal_width)

    def printAllRecords(self):
        """
        Display all records from the Repository using the table/stacked format chosen by print_flights_table. 
        Prints a message if the database is empty.
        
        Returns:
            None
        """

        if not self.repo.records:

            print("No records.")

            return

        self.print_flights_table(self.repo.records)
        

    # ---------------------------------------------------------
    # CRUD UI WRAPPERS
    # ---------------------------------------------------------

    def addSingle(self):
        """
        UI for creating and inserting a new flight record.
        Prompts the user for each field, performs basic input validation,
        and delegates full validation and insertion to the Repository.
        
        Returns:
            None
        """

        print("\n=== Add Single Flight Record ===")

        print("Type 0 at any time to cancel.\n")

        rec = {}

        def _prompt(label, validator=lambda x: True):

            while True:

                val = input(f"{label}: ").strip()

                if val == "0":

                    print("Cancelled.")

                    return None

                if val == "":

                    print("Input cannot be empty.")

                    continue

                if validator(val):

                    return val

                print("Invalid input.")

        # 1. flightID
        def val_fid(v):

            test = {"flightID": v}

            return self.repo._validate_flightID(test)

        v = _prompt("flightID (FLTxxxxxx)", val_fid)

        if v is None: return

        rec["flightID"] = v

        # 2. flightType
        v = _prompt("flightType (public/private/cargo/military)",
                    lambda x: x in ["public", "private", "cargo", "military"])
        
        if v is None: return

        rec["flightType"] = v

        # 3. pilotID
        v = _prompt("pilotID (AA1234)",
                    lambda x: self.repo._validate_pilotID({"pilotID": x}))
        
        if v is None: return

        rec["pilotID"] = v

        # 4. airline
        v = _prompt("airline")

        if v is None: return

        rec["airline"] = v

        # 5. departureDate
        def val_date(x):

            try:

                datetime.strptime(x, "%H:%M %d/%m/%Y")

                return True

            except:

                return False

        v = _prompt("departureDate (HH:MM DD/MM/YYYY)", val_date)

        if v is None: return

        rec["departureDate"] = v

        # 6. departureLocation
        v = _prompt("departureLocation")

        if v is None: return

        rec["departureLocation"] = v

        # 7. arrivalDate
        v = _prompt("arrivalDate (HH:MM DD/MM/YYYY)", val_date)

        if v is None: return

        rec["arrivalDate"] = v

        # 8. arrivalLocation
        v = _prompt("arrivalLocation")

        if v is None: return

        rec["arrivalLocation"] = v

        # 9. aircraftID
        v = _prompt("aircraftID (6 chars)",
                    lambda x: self.repo._validate_aircraftID({"aircraftID": x}))
        
        if v is None: return

        rec["aircraftID"] = v

        # 10. aircraftModel
        v = _prompt("aircraftModel")

        if v is None: return

        rec["aircraftModel"] = v

        # Conditional fields based on flightType
        ft = rec["flightType"]

        if ft == "public":

            v = _prompt("passengers", lambda x: x.isdigit())

            if v is None: return

            rec["passengers"] = int(v)

        elif ft == "cargo":

            v = _prompt("cargoWeight (tonnes)", lambda x: all(c in "0123456789." for c in x))

            if v is None: return

            rec["cargoWeight"] = float(v)

        elif ft == "military":

            v = _prompt("mission")

            if v is None: return

            rec["mission"] = v

        # Final validation through repository
        if self.repo.insert(rec):

            self.repo.appendToFile()

            print(f"\nFlight {rec['flightID']} added successfully.\n")

        else:

            print("Record failed validation. Not added.")

    def deleteRecord(self):
        """
        UI for deleting an existing record by flightID.
        Locates the record via Repository, removes it, and saves changes to file.
        
        Returns:
            None
        """

        fid = input("Enter flightID: ")

        rec = next((r for r in self.repo.records if r["flightID"] == fid), None)

        if not rec:

            print("Not found.")

            return

        self.repo.delete(rec)

        self.repo.saveToFile()

        print("Deleted.")

    # ---------------------------------------------------------
    # RECORDS UI
    # ---------------------------------------------------------
    def recordsMenu(self):
        """
        Display the records submenu
        Allows the user to print all records
        Allows the user to print a specific record
        Allows the user to print records based on a given filter
        
        Returns:
            None
        """

        while True:
           print("\n=== Records ===")
           print("0. Back")
           print("1. Print All")
           print("2. Print Specific")
           print("3. Print Ordered (by filter)")
           
           ch = input("Choose: ").strip()

           match ch:

               case "0":
                   return

               case "1":
                   self.printAllRecords()

               case "2":

                   flightID = input("\nEnter flightID of the specific flight (FLT######):  ")

                   rec = self.repo.getByFlightID(flightID)

                   if rec is None:

                       print("Flight ID not found. Try again.\n")

                   else:

                       self.specificRecord(rec)

                       return

               case "3":
                   self.filteredRecords() 

               case _:
                   print("Invalid option.\n")


    def specificRecord(self, record):
        """
        Displays a formatted view of a single flight record.
        Parameters:
            record (dict): The flight record to display
        Returns:
            None
        """

        print("\nMatching Record:")
        print(self.server.formatRecord(record, isAirlineUser=(self.userType == "Airline")))

            
    def filteredRecords(self):
        """
        Print records ordered by a single chosen field.
        UI matches the style of the Update Record field selection.
        
        Returns:
            None
        """

        # Determine fields exactly like UpdateRecord
        fields = [
            "flightID", "flightType", "pilotID", "airline",
            "departureDate", "departureLocation",
            "arrivalDate", "arrivalLocation",
            "aircraftID", "aircraftModel"
        ]

        # Add conditional fields (we check all records — if ANY record has the field, include it)
        if any("passengers" in r for r in self.repo.records):
            fields.append("passengers")
        if any("cargoWeight" in r for r in self.repo.records):
            fields.append("cargoWeight")
        if any("mission" in r for r in self.repo.records):
            fields.append("mission")

        print("\n=== Sort Records ===")
        print("Select ONE field to sort by:\n")

        # Display numerical menu
        for i, f in enumerate(fields, start=1):
            print(f"{i}. {f}")

        print("0. Cancel")

        choice = input("\nEnter field number: ").strip()

        if choice == "0":
            return

        try:
            idx = int(choice)
        except:
            print("Invalid selection.")
            return

        if not 1 <= idx <= len(fields):
            print("Invalid field number.")
            return

        field = fields[idx - 1]

        # ---- SORTING LOGIC ----

        # Date fields need datetime sorting
        if field in ("departureDate", "arrivalDate"):
            try:
                sorted_records = sorted(
                    self.repo.records,
                    key=lambda r: datetime.strptime(r[field], "%H:%M %d/%m/%Y")
                )
            except:
                print("Error: One or more dates are invalid format.")
                return

        else:
            # Non-date fields sorted alphabetically / numerically
            sorted_records = sorted(
                self.repo.records,
                key=lambda r: str(r.get(field, "")).lower()
            )

        # Print results in your table format
        print(f"\n=== Sorted by {field} ===\n")
        self.print_flights_table(sorted_records)



    # ---------------------------------------------------------
    # STATS UI
    # ---------------------------------------------------------

    def statisticsMenu(self):
         """
        Displays the Statistics submenu and provides pilot, airline, general, and model-based statistical summaries.
        
        Returns:
            None
        """

         while True:
            print("\n=== Statistics ===")
            print("0. Back")
            print("1. Pilot Statistics")
            print("2. Airline Statistics")

            if self.userType == "Airline":
                print("3. General Statistics")
                print("4. Model Statistics")

            ch = input("Choose: ").strip()

            if ch == "0":
                return

            # -----------------------------------------------------
            # 1. PILOT STATISTICS
            # -----------------------------------------------------
            if ch == "1":
                pid = input("Enter pilotID: ").strip()
                self.server.pilotStats(pid)

            # -----------------------------------------------------
            # 2. AIRLINE STATISTICS
            # -----------------------------------------------------
            elif ch == "2":
                al = input("Enter Airline: ").strip()
                print("\nChoose range:")
                print("1. All-Time")
                print("2. Specific Year")

                sub = input("Choice: ").strip()

                if sub == "1":
                    total = self.server.airlineTotal(al)
                    print(f"\nTotal flights for {al}: {total}\n")

                elif sub == "2":
                    year = input("Enter Year (YYYY): ").strip()
                    total = self.server.airlineYear(al, year)
                    print(f"\nFlights for {al} in {year}: {total}\n")

                else:
                    print("Invalid option.\n")

            # -----------------------------------------------------
            # 3. GENERAL STATISTICS (Airline User Only)
            # -----------------------------------------------------
            elif ch == "3" and self.userType == "Airline":
                print("\nGeneral Statistics:")
                print("1. Total Flights in Database")
                print("2. Total Flights by Given Year")
                print("3. Total Flights by Flight Type")

                sub = input("Choose: ")

                if sub == "1":
                    print(f"\nTotal Flights: {self.server.totalFlights()}\n")

                elif sub == "2":
                    year = input("Enter Year (YYYY): ")
                    print(f"\nFlights in {year}: {len(self.server.flightsByYear(year))}\n")

                elif sub == "3":
                    ft = input("Enter Flight Type: ")
                    print(f"\nTotal {ft} flights: {len(self.server.flightsByType(ft))}\n")

                else:
                    print("Invalid option.\n")

            # -----------------------------------------------------
            # 4. MODEL STATISTICS (Airline User Only)
            # -----------------------------------------------------
            elif ch == "4" and self.userType == "Airline":
                print("\nModel Statistics:")
                print("1. Average Passengers by Model")
                print("2. Average Cargo Weight by Model")

                sub = input("Choose: ")

                if sub == "1":
                    model = input("Model: ")
                    avg = self.server.avgPassengers(model)
                    if avg is None:
                        print("No passenger data.\n")
                    else:
                        print(f"\nAverage Passengers for {model}: {avg:.2f}\n")

                elif sub == "2":
                    model = input("Model: ")
                    avg = self.server.avgCargo(model)
                    if avg is None:
                        print("No cargo data.\n")
                    else:
                        print(f"\nAverage Cargo Weight for {model}: {avg:.2f} tonnes\n")

                else:
                    print("Invalid option.\n")

            else:
                print("Invalid choice.\n")

