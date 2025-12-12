# ECED3410 - Group 3 Project
# Alice Balser - B00954620
# Connor McDonald - B00938421

from datetime import datetime


class Server:

    def __init__(self, repo):
        """
        Initializes the Server with a reference to the Repository class.

        Parameters:
            repo (Repository): The Repository instance used for accessing stored records

        Returns:
            None
        """

        self.repo = repo

    def formatRecord(self, rec, isAirlineUser):
        """
        Generates a formatted string representation of a flight record, while hiding sensitive fields for General users.
        
        Parameters:
            rec (dict): The record to format
            isAirlineUser (bool): Whether the requester is an Airline user allowed to see sensitive data
        
        Returns:
            str: A formatted multi-line string representing the record
        """

        sensitive_keys = {"passengers", "mission", "cargoWeight"}

        lines = []

        for k, v in rec.items():

            # Hide sensitive information for general users
            if not isAirlineUser and k in sensitive_keys:
                continue

            lines.append(f"{k}: {v}")

        return "\n".join(lines)

    # ---------------------------------------------------------
    # PILOT STATS
    # ---------------------------------------------------------
    def pilotStats(self, pilotID):
        """
        Displays statistics for a given pilot, including total flights, career length, and airlines flown for.
        
        Parameters:
            pilotID (str): The pilot ID to search for
        
        Returns:
            None
        """

        print("\n=== Pilot Statistics ===")

        if pilotID == "0" or pilotID.strip() == "":

            print("No data.\n")

            return

        # Find flights for that pilot
        flights = [r for r in self.repo.records if r["pilotID"].lower() == pilotID.lower()]

        if not flights:

            print("\nNo flights found for that pilot.\n")

            return

        # Sort by date
        def parse_date(d):

            return datetime.strptime(d, "%H:%M %d/%m/%Y")

        flights_sorted = sorted(flights, key=lambda r: parse_date(r["departureDate"]))

        first = flights_sorted[0]["departureDate"]
        last  = flights_sorted[-1]["departureDate"]

        career_days = (parse_date(last) - parse_date(first)).days
        airlines = sorted({r["airline"] for r in flights})

        # Nicely formatted output
        print(f"\nPilot: {pilotID}")
        print("--------------------------------------")
        print(f"Total Flights: {len(flights)}")
        print(f"Career Length: {career_days} days")
        print(f"First Flight: {first}")
        print(f"Last Flight:  {last}")
        print("\nAirlines flown for:")
         
        for al in airlines:

            print(f"- {al}")



    # ---------------------------------------------------------
    # AIRLINE STATS
    # ---------------------------------------------------------

    def airlineTotal(self, airline):
         """
        Counts all flights associated with a specific airline.

        Parameters:
            airline (str): The airline name to search for

        Returns:
            int: The number of matching flights
        """

         airline = airline.lower()

         flights = [r for r in self.repo.records if r["airline"].lower() == airline]

         return len(flights)

    def airlineYear(self, airline, year):
        """
        Counts all flights for a given airline within a specified year.

        Parameters:
            airline (str): The airline name to search for
            year (str): The target year in YYYY format

        Returns:
            int: The number of flights for that airline in the given year
        """

        airline = airline.lower()

        flights = [

            r for r in self.repo.records

            if r["airline"].lower() == airline

            and r["departureDate"][-4:] == year
        
        ]

        return len(flights)

    # ---------------------------------------------------------
    # GENERAL STATS
    # ---------------------------------------------------------

    def totalFlights(self):
        """
        Retrieves the total number of flights in the Repository.

        Returns:
            int: Total number of stored flight records
        """

        return len(self.repo.records)

    def flightsByYear(self, year):
        """
        Retrieves all flights occurring within a given year.

        Parameters:
            year (str): The year to filter by, in YYYY format

        Returns:
            list[dict]: A list of matching flight records
        """

        return [

            r for r in self.repo.records

            if r["departureDate"][-4:] == year

        ]

    def flightsByType(self, ft):
        """
        Retrieves all flights of a specified flight type.

        Parameters:
            ft (str): The flight type to search for (e.g., 'public', 'cargo')

        Returns:
            list[dict]: A list of matching records
        """

        return [

            r for r in self.repo.records

            if r["flightType"].lower() == ft.lower()

        ]

    # ---------------------------------------------------------
    # MODEL STATS
    # ---------------------------------------------------------

    def avgPassengers(self, model):
        """
        Computes the average passenger count for public flights of a given aircraft model.

        Parameters:
            model (str): The aircraft model name to analyze

        Returns:
            float or None: The average passenger count, or None if no valid data exists
        """

        model = model.lower()

        flights = [

            r for r in self.repo.records

            if r["aircraftModel"].lower() == model

            and r["flightType"].lower() == "public"

            and "passengers" in r

        ]

        if not flights:

            return None

        return sum(r["passengers"] for r in flights) / len(flights)

    def avgCargo(self, model):
        """
        Computes the average cargo weight for cargo flights of a given aircraft model.

        Parameters:
            model (str): The aircraft model name to analyze

        Returns:
            float or None: The average cargo weight in tonnes, or None if no valid data exists
        """

        model = model.lower()

        flights = [

            r for r in self.repo.records

            if r["aircraftModel"].lower() == model

            and r["flightType"].lower() == "cargo"

            and "cargoWeight" in r

        ]

        if not flights:

            return None

        return sum(r["cargoWeight"] for r in flights) / len(flights)
