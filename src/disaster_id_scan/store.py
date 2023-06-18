# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2
from csv import DictWriter
from datetime import date, datetime
from pathlib import Path

import jsonpickle


class Person:
    '''
    Class to hold a person's data.
    It has to be assumed that the data is not complete.
    '''
    first_name: str
    last_name: str
    date_of_birth: date
    nationality: str
    residence: str
    place_of_catastrophe: str
    place_of_shelter: str
    date_of_catastrope: date
    time_of_registration: datetime

    def __init__(self):
        # Set all values to None
        self.first_name = None
        self.last_name = None
        self.date_of_birth = None
        self.nationality = None
        self.residence = None
        self.place_of_catastrophe = None
        self.place_of_shelter = None
        self.date_of_catastrope = None
        # Set time of registration to now
        self.time_of_registration = datetime.now()

    def __str__(self):
        return f"""-- Person --
Name: {self.last_name}
First Name: {self.first_name}
Date of Birth: {self.date_of_birth}"""


class Registrants:
    '''
    Class to hold a list of registrants.
    '''
    registrants: list[Person]

    save_path: Path
    json_filename: str = "disaster-id-scan_autosave.json"

    export_filename: str = "disaster-id-scan_export.csv"

    def __init__(self):
        self.registrants = []

    def add(self, person: Person) -> int:
        '''
        Add a person to the list of registrants, return the id of the person.
        '''
        self.registrants.append(person)
        return len(self.registrants) - 1

    def get_savepoint_path(self) -> Path:
        return self.save_path.joinpath(Registrants.json_filename)

    def get_export_path(self) -> Path:
        return self.save_path.joinpath(Registrants.export_filename)

    def get_name_list(self) -> list[str]:
        return [f"{person.last_name}, {person.first_name} #{id}" for id, person in enumerate(self.registrants)]

    def get_person_by_list_entry(self, list_entry: str) -> (int, Person):
        person_id = int(list_entry.split("#")[1])
        return person_id, self.registrants[person_id]

    def get_person_by_id(self, person_id: int) -> Person:
        return self.registrants[person_id]

    def update(self, person_id: int, person: Person):
        self.registrants[person_id] = person
        self.save()

    def delete(self, person_id: int):
        self.registrants.pop(person_id)
        self.save()

    def set_path(self, path: Path):
        self.save_path = path
        # Check if json file exists, if so load it
        if self.get_savepoint_path().exists():
            with open(self.get_savepoint_path(), "r") as f:
                self.registrants = jsonpickle.decode(f.read())
        # Save immediately, to keep export file up to date
        self.save()

    def save(self):
        with open(self.get_savepoint_path(), "w") as f:
            f.write(jsonpickle.encode(self.registrants))
        # Export to csv (Xenios-Format? Whatever...)
        # Name, Vorname, geb, Alter(ca.), Nationalitaet, Staat, Unterkunft,

        with open(self.get_export_path(), "w") as f:
            writer = DictWriter(f, fieldnames=["Name", "Vorname", "geb", "Alter(ca.)", "Nationalitaet", "Staat",
                                               "Unterkunft", "Katastrophenort", "Katastrophentag", "Registrierungszeit"])
            writer.writeheader()
            for person in self.registrants:
                # Calculate approximate age
                if person.date_of_birth is not None:
                    age = datetime.now().year - person.date_of_birth.year
                else:
                    age = None
                writer.writerow({
                    "Name": person.last_name,
                    "Vorname": person.first_name,
                    "geb": person.date_of_birth.strftime("%d.%m.%Y") if person.date_of_birth is not None else None,
                    "Alter(ca.)": age,
                    "Nationalitaet": person.nationality,
                    "Staat": person.residence,
                    "Unterkunft": person.place_of_shelter,
                    "Katastrophenort": person.place_of_catastrophe,
                    "Katastrophentag": person.date_of_catastrope.strftime("%d.%m.%Y") if person.date_of_catastrope is not None else None,
                    "Registrierungszeit": person.time_of_registration.strftime("%d.%m.%Y %H:%M:%S") if person.time_of_registration is not None else None
                })
