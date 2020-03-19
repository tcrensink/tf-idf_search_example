"""
Records are constructed and then iterated over to find counts. This is done for clarity over performance.

data errors:
- state "C" -> "DC"
- BENTONVILLE, AR  72712 -> BENTONVILLE

record descr: https://nces.ed.gov/ccd/data/txt/sl051blay.txt
"""
import csv
from itertools import groupby
DATA_PATH = "school_data.csv"

# easier to remember these:
STATE_FIELD = "LSTATE05"
METRO_FIELD = "MLOCALE"
CITY_FIELD = "LCITY05"
SCHOOL_ID_FIELD = "NCESSCH"


def return_records(data_path=DATA_PATH):
    with open(data_path, newline="") as fp:
        reader = csv.DictReader(fp)
        records = [rec for rec in reader]
    return records


def field_val_fun(field):
    """Return function to pass to groupby, sort key."""
    def field_function(record, field=field):
        value = record[field]
        return value
    return field_function


def max_value_key(value_dict):
    """Return key(s) with max value from value_dict.from

    This function implicitly assumes there is a unique key with the max value.
    """
    max_value = max(value_dict.values())
    max_key = [key for key, val in value_dict.items() if val == max_value][0]
    return max_key


def dict_to_str(dictionary):
    """Return string of dict formatted for print."""
    str_list = [f"{key}: {val}" for key, val in dictionary.items()]
    print_string = "\n".join(str_list)
    return print_string


def print_counts(records):
    """Generate data and print it, formatted."""

    # get num unique school ids (safer than len(records))
    school_count = len(set(record[SCHOOL_ID_FIELD] for record in records))

    # create a dict of form field_val: counts(field_val) for each below
    state_func = field_val_fun(STATE_FIELD)
    state_groups = groupby(sorted(records, key=state_func), key=state_func)
    state_count_dict = {key: len(list(val)) for key, val in state_groups}

    metro_func = field_val_fun(METRO_FIELD)
    metro_groups = groupby(sorted(records, key=metro_func), key=metro_func)
    metro_count_dict = {key: len(list(val)) for key, val in metro_groups}

    city_func = field_val_fun(CITY_FIELD)
    city_groups = groupby(sorted(records, key=city_func), key=city_func)
    city_count_dict = {key: len(list(val)) for key, val in city_groups}
    city_max_schools = max_value_key(city_count_dict)
    max_school_count = city_count_dict[city_max_schools]
    num_cities_with_schools = len(city_count_dict)

    print(f"Total Schools: {school_count}")
    print("Schools by State:")
    print(dict_to_str(state_count_dict))

    print("Schools by Metro-centric locale:")
    print(dict_to_str(metro_count_dict))

    print("City with most schools:", city_max_schools, f"({max_school_count} schools)")
    print(f"Unique cities with at least one school: {num_cities_with_schools}")


if __name__ == "__main__":

    records = return_records()
    print_counts(records)
