from enum import Enum

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


def get_mrz_data(possible_mrz: str, td_type: DocumentType = DocumentType.ANY):
    try:
        if td_type == DocumentType.ANY:
            for td in DocumentType:
                if td == DocumentType.ANY:
                    # We don't want endless recursion
                    pass
                data = get_mrz_data(possible_mrz, td)
                if data is not None:
                    return data
            else:
                print("No valid MRZ :(")
                return None
        elif td_type == DocumentType.TD1:
            return TD1CodeChecker(possible_mrz)
        elif td_type == DocumentType.TD2:
            return TD2CodeChecker(possible_mrz)
        elif td_type == DocumentType.TD3:
            return TD3CodeChecker(possible_mrz)
        else:
            print("Unknown DocumentType")
            return None
    except FieldError as fe:
        print(f"MRZ Error for {td_type}: {fe}")
        return None


def get_data_from_mrz(mrz: str):
    '''Parse MRZ, return data as dict'''
    mrz_data = get_mrz_data(mrz)

    if mrz_data is None:
        return None
    else:
        p = Person()
        p.first_name = td1.fields()['names']
        p.last_name = td1.fields()['surname']
        p.date_of_birth = td1.fields()['date_of_birth']
