from enum import Enum
from datetime import date, datetime
from typing import Union

import easyocr
from mrz.base.errors import FieldError

from disaster_id_scan.store import Person


class DocumentType(Enum):
    ANY = 0
    TD1 = 1
    TD2 = 2
    TD3 = 3


def extract_mrz_from_image(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    pass


def parse_mrz(mrz: str) -> Union[Person, None]:
    '''Parse MRZ'''
    # Remove all whitespaces
    mrz = mrz.replace(" ", "")
    # Everything in MRZ is uppercase
    mrz = mrz.upper()
    # Check if Identity Card or Passport
    if mrz[0] == "P":
        # Passport
        pass  # -port :D
    elif mrz[0] == "I":
        # Identity Card
        return parse_td1(mrz)
    return None


def parse_td1(mrz: str) -> Union[Person, None]:
    # Parse Identity Card
    # https://en.wikipedia.org/wiki/Machine-readable_passport
    # Country code Issuer(3 letters)
    country_code_issuer = mrz[2:5].replace("<", "")
    # Name (Surname<<Given Names)
    name = mrz[60:90]
    names_splitted = name.split("<<")
    surname = names_splitted[0]
    given_names = names_splitted[1]
    given_names = given_names.replace("<", " ").rstrip()
    # Date of Birth (YYMMDD)
    birthdate_str: str = mrz[30:36]
    # Parse to date object
    birthdate = datetime.strptime(birthdate_str, "%y%m%d")
    nationality = mrz[45:48].replace("<", "")
    p = Person()
    p.first_name = given_names
    p.last_name = surname
    p.date_of_birth = birthdate
    p.residence = f"{country_code_issuer}"
    p.nationality = nationality
    print(p)
    return p
