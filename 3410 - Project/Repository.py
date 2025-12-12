# ECED3410 - Group 3 Project
# Alice Balser - B00954620
# Connor McDonald - B00938421

import json
import re
from datetime import datetime


class Repository:

    def __init__(self):
        """
        Initializes the Repository with an empty in-memory list of records.

        Returns:
            None
        """

        self.records = []

    # ---------------------------------------------------------
    # VALIDATION MODULES
    # ---------------------------------------------------------

    def _validate_mandatory_fields(self, rec):
        """
        Validates that all required fields exist and are non-empty in a record.

        Parameters:
            rec (dict): The record to validate

        Returns:
            bool: True if all mandatory fields are valid, otherwise False
        """

        required = [

            "flightType", "pilotID", "airline",
            "departureDate", "departureLocation",
            "arrivalDate", "arrivalLocation",
            "aircraftID", "flightID", "aircraftModel"

        ]

        for field in required:

            if field not in rec or str(rec[field]).strip() == "":

                print(f"Error: Missing required field '{field}'")

                return False

        return True

    def _validate_flightType(self, rec):
        """
        Validates that the flightType field is one of the allowed categories.

        Parameters:
            rec (dict): The record containing the flightType field

        Returns:
            bool: True if valid, False otherwise
        """

        valid_types = ["public", "private", "cargo", "military"]

        ft = rec.get("flightType", "").lower()

        if ft not in valid_types:

            print(f"Error ({rec.get('flightID')}): invalid flightType '{ft}'")

            return False

        return True

    def _validate_pilotID(self, rec):
        """
        Validates the pilotID format (two letters followed by four digits).

        Parameters:
            rec (dict): The record containing the pilotID field

        Returns:
            bool: True if valid, False otherwise
        """

        pid = rec.get("pilotID", "")

        if not re.match(r"^[A-Za-z]{2}\d{4}$", pid):

            print(f"Error ({rec.get('flightID')}): invalid pilotID '{pid}'")

            return False

        return True

    def _validate_flightID(self, rec, ignore_rec=None):
        """
        Validates a flightID for correct formatting and uniqueness in the Repository.

        Parameters:
            rec (dict): The record containing the flightID
            ignore_rec (dict or None): A record to exclude during uniqueness checks when updating

        Returns:
            bool: True if valid, False otherwise
        """

        fid = rec.get("flightID", "")

        if not (fid.startswith("FLT") and len(fid) == 9 and fid[3:].isdigit()):

            print(f"Invalid flightID format '{fid}'")

            return False

        for r in self.records:

            if r is ignore_rec:

                continue

            if r["flightID"] == fid:

                print(f"Error: flightID '{fid}' already exists.")

                return False

        return True

    def _validate_aircraftID(self, rec):
        """
        Validates the aircraftID format (six alphanumeric characters).

        Parameters:
            rec (dict): The record containing the aircraftID field

        Returns:
            bool: True if valid, False otherwise
        """

        aid = rec.get("aircraftID", "")

        if not re.match(r"^[A-Za-z0-9]{6}$", aid):

            print(f"Error ({rec.get('flightID')}): invalid aircraftID '{aid}'")

            return False

        return True

    def _validate_datetime(self, rec):
        """
        Validates that the departure and arrival date fields match the expected datetime format.

        Parameters:
            rec (dict): The record containing date fields to validate

        Returns:
            bool: True if all dates are valid, False otherwise
        """

        for field in ["departureDate", "arrivalDate"]:

            try:

                datetime.strptime(rec[field], "%H:%M %d/%m/%Y")

            except:

                print(f"Error ({rec.get('flightID')}): invalid date in '{field}'")

                return False

        return True

    def _validate_conditional_fields(self, rec):
        """
        Ensures the correct conditional fields exist based on the flightType (e.g., passengers for public, cargoWeight for cargo).
        
        Parameters:
            rec (dict): The record to validate
        
        Returns:
            bool: True if conditional fields are correct, False otherwise
        """

        ft = rec["flightType"].lower()

        has_pass = "passengers" in rec
        has_cargo = "cargoWeight" in rec
        has_mission = "mission" in rec

        if ft == "public":

            return has_pass and not has_cargo and not has_mission

        if ft == "cargo":

            return has_cargo and not has_pass and not has_mission

        if ft == "military":

            return has_mission and not has_pass and not has_cargo

        if ft == "private":

            return not has_pass and not has_cargo and not has_mission

        return True

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------

    def insert(self, rec):
        """
        Inserts a new flight record into the Repository after full validation.
        
        Parameters:
            rec (dict): The record to insert
        
        Returns:
            bool: True if insertion succeeds, False if validation fails
        """

        # Normalize passenger and cargoWeight so they will not cause errors while calculating statistics
        self._normalize_types(rec)

        if not (

            self._validate_flightID(rec)

            and self._validate_flightType(rec)

            and self._validate_pilotID(rec)

            and self._validate_mandatory_fields(rec)

            and self._validate_aircraftID(rec)

            and self._validate_datetime(rec)

            and self._validate_conditional_fields(rec)


        ):

            return False

        self.records.append(rec)

        return True

    def update(self, old_rec, new_rec):
        """
        Validates and applies a full update to an existing flight record.

        Parameters:
            old_rec (dict): The original record before modification
            new_rec (dict): The updated record containing new field values

        Returns:
            bool: True if the update succeeds, False otherwise
        """

        # Normalize passenger and cargoWeight so they will not cause errors while calculating statistics
        self._normalize_types(new_rec)

        if not (

            self._validate_mandatory_fields(new_rec)

            and self._validate_flightType(new_rec)

            and self._validate_pilotID(new_rec)

            and self._validate_flightID(new_rec, ignore_rec=old_rec)

            and self._validate_aircraftID(new_rec)

            and self._validate_datetime(new_rec)

            and self._validate_conditional_fields(new_rec)

        ):

            return False

        old_rec.clear()
        old_rec.update(new_rec)

        return True

    def _normalize_types(self, rec):
        """
        Converts passengers and cargoWeight fields to the correct types.
        (if the mentioned fields are in the record).

        Parameters:
            rec (dict): The record whose fields will be normalized

        Returns:
            None
        """
    
        # Passengers should be of type int
        if "passengers" in rec and rec["passengers"] is not None:

            try:

                rec["passengers"] = int(rec["passengers"])

            except (ValueError, TypeError):

                raise ValueError("Invalid passengers value (must be an integer).")

        # Cargo weight should be of type float
        if "cargoWeight" in rec and rec["cargoWeight"] is not None:

            try:

                rec["cargoWeight"] = float(rec["cargoWeight"])

            except (ValueError, TypeError):

                raise ValueError("Invalid cargoWeight value (must be a number).")


    def delete(self, rec):
        """
        Removes a record from the Repository.

        Parameters:
            rec (dict): The record to remove

        Returns:
            None
        """

        self.records.remove(rec)

    def getByFlightID(self, fid):
        """
        Retrieves a record matching the given flightID.

        Parameters:
            fid (str): The flightID to search for

        Returns:
            dict or None: The matching record, or None if not found
        """

        for rec in self.records:

            if rec.get("flightID") == fid:

                return rec

        return None



    # ---------------------------------------------------------
    # JSON I/O
    # ---------------------------------------------------------

    def loadFromFile(self, filename="flybase.json"):
        """
        Loads flight records from a JSON file and inserts valid entries into the Repository.

        Parameters:
            filename (str): The path to the JSON file to load

        Returns:
            int: The number of successfully inserted records
        """

        try:

            with open(filename, "r") as f:

                data = json.load(f)

        except FileNotFoundError:

            print("No existing database. Starting empty.")

            return 0

        count = 0

        for rec in data:

            if self.insert(rec):

                count += 1

        return count

    def saveToFile(self, filename="flybase.json"):
        """
        Saves all current flight records to a JSON file, overwriting existing data.

        Parameters:
            filename (str): The path to the JSON file to write

        Returns:
            None
        """

        with open(filename, "w") as f:

            json.dump(self.records, f, indent=4)

    def appendToFile(self, filename="flybase.json"):
        """
        Appends or updates flight records in an existing JSON file without deleting earlier entries.

        Parameters:
            filename (str): The path to the JSON file to update

        Returns:
            None
        """

        try:

            with open(filename, "r") as f:

                existing = json.load(f)

        except:

            existing = []

        combined = {rec["flightID"]: rec for rec in existing}

        for r in self.records:

            combined[r["flightID"]] = r

        with open(filename, "w") as f:

            json.dump(list(combined.values()), f, indent=4)
