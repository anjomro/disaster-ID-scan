from enum import Enum
from datetime import date, datetime
from typing import Union

import easyocr

from disaster_id_scan.store import Person


class DocumentType:
    mrz: str

    row_length: int
    row_count: int

    # Fields: (row, start_position, end_position)
    issuer_country_pos: (int, int, int)
    names_pos: (int, int, int)
    birthdate_pos: (int, int, int)
    birthdate_checkdigit_pos: (int, int, int)
    nationality_pos: (int, int, int)

    # Dict with country codes according to ISO 3166-1 alpha-3
    # With exceptions, e.g. "D" for Germany instead of "DEU"
    country_codes = {
        # Special codes:
        "BAH": "Bahamas",
        "D": "Deutschland",
        "EUE": "European Union",
        "GBD": "British Overseas Territories Citizen",
        "GBN": "British National (Overseas)",
        "GBO": "British Overseas Citizen",
        "GBP": "British Protected Person",
        "GBS": "British Subject",
        "UNA": "Specialized Agency of the United Nations",
        "UNK": "Kosovo under United Nations Interim Administration",
        "UNO": "United Nations Organization",
        "XBA": "African Development Bank",
        "XIM": "African Export Import Bank",
        "XCC": "Caribbean Community",
        "XCO": "Common Market for Eastern and Southern Africa",
        "XEC": "Economic Community of West African States",
        "XPO": "International Criminal Police Organization",
        "XOM": "Sovereign Military Order of Malta",
        "XXA": "Stateless",
        "XXB": "Refugee",
        "XXC": "Refugee",
        "XXX": "Unspecified Nationality",
        "ZIM": "Zimbabwe",
        # Main European countries:
        "AUT": "Austria",
        "BEL": "Belgium",
        "BGR": "Bulgaria",
        "CHE": "Switzerland",
        "CYP": "Cyprus",
        "CZE": "Czech Republic",
        "DEU": "Germany",
        "DNK": "Denmark",
        "ESP": "Spain",
        "EST": "Estonia",
        "FIN": "Finland",
        "FRA": "France",
        "GBR": "United Kingdom",
        "GRC": "Greece",
        "HRV": "Croatia",
        "HUN": "Hungary",
        "IRL": "Ireland",
        "ISL": "Iceland",
        "ITA": "Italy",
        "LIE": "Liechtenstein",
        "LTU": "Lithuania",
        "LUX": "Luxembourg",
        "LVA": "Latvia",
        "MCO": "Monaco",
        "MLT": "Malta",
        "NLD": "Netherlands",
        "NOR": "Norway",
        "POL": "Poland",
        "PRT": "Portugal",
        "ROU": "Romania",
        "SVK": "Slovakia",
        "SVN": "Slovenia",
        "SWE": "Sweden",
        "UKR": "Ukraine",
    }

    def __init__(self,
                 mrz: str,
                 row_length: int,
                 row_count: int,
                 issuer_country_pos: (int, int, int),
                 names_pos: (int, int, int),
                 birthdate_pos: (int, int, int),
                 birthdate_checkdigit_pos: (int, int, int),
                 nationality_pos: (int, int, int)):
        self.mrz = mrz
        self.row_length = row_length
        self.row_count = row_count
        self.issuer_country_pos = issuer_country_pos
        self.names_pos = names_pos
        self.birthdate_pos = birthdate_pos
        self.birthdate_checkdigit_pos = birthdate_checkdigit_pos
        self.nationality_pos = nationality_pos

    def country_code_to_name(self, code: str) -> str:
        code = code.upper().replace("<", "")
        if code in self.country_codes:
            return self.country_codes[code]
        else:
            return code

    def get_field(self, pos: (int, int, int)) -> str:
        # Position offset:
        # 1 is the first position in the first row
        pos_offset = (pos[0] - 1) * self.row_length
        return self.mrz[pos_offset + pos[1] - 1:pos_offset + pos[2]]

    def get_issuer_country(self) -> str:
        country = self.get_field(self.issuer_country_pos)
        return self.country_code_to_name(country)

    def get_first_name(self) -> str:
        names_splitted = self.get_field(self.names_pos).split("<<")
        if len(names_splitted) > 1:
            return names_splitted[1].replace("<", " ")
        else:
            return ""

    def get_last_name(self) -> str:
        return self.get_field(self.names_pos).split("<<")[0].replace("<", " ")

    def get_birthdate(self) -> date:
        # Get Birthdate, format YYMMDD
        try:
            birthdate = datetime.strptime(self.get_field(self.birthdate_pos), "%y%m%d").date()
        except ValueError:
            return date(1, 1, 1)
        return birthdate

    def get_birthdate_checkdigit(self) -> int:
        try:
            checkdigit = int(self.get_field(self.birthdate_checkdigit_pos))
        except ValueError:
            return -1
        return checkdigit

    def get_nationality(self) -> str:
        country = self.get_field(self.nationality_pos)
        return self.country_code_to_name(country)

    def get_person(self) -> Person:
        p = Person()
        p.first_name = self.get_first_name()
        p.last_name = self.get_last_name()
        p.date_of_birth = self.get_birthdate()
        p.nationality = self.get_nationality()
        p.residence = self.get_issuer_country()
        return p


class TD1(DocumentType):
    def __init__(self, mrz: str = ""):
        super(TD1, self).__init__(
            mrz=mrz,
            row_length=30,
            row_count=3,
            issuer_country_pos=(1, 3, 5),
            names_pos=(3, 1, 30),
            birthdate_pos=(2, 1, 6),
            birthdate_checkdigit_pos=(2, 7, 7),
            nationality_pos=(2, 16, 18),
        )


class TD2(DocumentType):
    def __init__(self, mrz: str = ""):
        super(TD2, self).__init__(
            mrz=mrz,
            row_length=36,
            row_count=2,
            issuer_country_pos=(1, 3, 5),
            names_pos=(1, 6, 36),
            birthdate_pos=(2, 14, 19),
            birthdate_checkdigit_pos=(2, 20, 20),
            nationality_pos=(2, 11, 13),
        )


class TD3(DocumentType):
    def __init__(self, mrz: str = ""):
        super(TD3, self).__init__(
            mrz=mrz,
            row_length=44,
            row_count=2,
            issuer_country_pos=(1, 3, 5),
            names_pos=(1, 6, 44),
            birthdate_pos=(2, 14, 19),
            birthdate_checkdigit_pos=(2, 20, 20),
            nationality_pos=(2, 11, 13),
        )


def extract_mrz_from_image(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    pass


def mrz_checksum(text: str, start_position: int = 0) -> int:
    # Assign values to characters 7, 3, 1, 7, 3, 1, ...
    # https://en.wikipedia.org/wiki/Machine-readable_passport
    values = [7, 3, 1]
    text = text.upper()
    # Reorder by start_position
    values = values[start_position:] + values[:start_position]
    # Calculate checksum
    checksum = 0
    for i, char in enumerate(text):
        # A-Z -> 10-35
        if char.isalpha():
            checksum += (ord(char) - 55) * values[i % len(values)]
        # 0-9 -> 0-9
        elif char.isdigit():
            checksum += int(char) * values[i % len(values)]
    return checksum % 10


def parse_mrz(mrz: str) -> Union[Person, None]:
    '''Parse MRZ'''
    # Remove all whitespaces
    mrz = mrz.replace(" ", "")
    # Everything in MRZ is uppercase
    mrz = mrz.upper()
    # Check if TD1, TD2 or TD3
    # TD3 is a Passport, must start with P
    if mrz[0] == "P":
        document = TD3(mrz)
    # If A for Aircrew or ~72char+-2, must be TD2
    elif mrz[0] == "A" or len(mrz) in range(70, 74):
        document = TD2(mrz)
    # If length is 90+-2 -> TD1
    elif len(mrz) in range(88, 92):
        document = TD1(mrz)
    else:
        return None
    return document.get_person()