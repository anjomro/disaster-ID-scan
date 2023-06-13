# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2
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
    json_filename: str = "data_savepoint.json"

    def __init__(self):
        self.registrants = []

    def add(self, person: Person):
        self.registrants.append(person)

    def get_savepoint_path(self) -> Path:
        return self.save_path.joinpath(Registrants.json_filename)

    def set_path(self, path: Path):
        self.save_path = path
        # TODO: Check if json file exists, if so load it


    def save(self):
        with open(self.get_savepoint_path(), "w") as f:
            f.write(jsonpickle.encode(self))
