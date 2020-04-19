
from sqlquery import *
from datetime import datetime

cubic_ft_to_gallons = float(float(1728) / float(231))
conn = establish_connection("student.sqlite")

count_default = 0

match_house = "Where address_street_name='{}' And address_street_number='{}' And service_id='{}' " \
              "And (meter_number='{}' Or meter_number='{}X') And meter_number!=''"
match_residential_house = match_house + "And service_type='Residential' "
before_date = "And (Water.current_date>'{}' Or prior_date>'{}') "
sort_by_date = "Order by prior_date, Water.current_date Asc;"  # NOTE: This should be only added at the end of the query


def query_database(request):
    return query(conn, request)


def print_to_csv(file_name, list, header, size):
    file = open(file_name, "w")
    file.write(header)
    for data in list:
        for i in range(size - 1):
            file.write(str(data[i]) + ",")
        file.write(str(data[size - 1]) + "\n")
    file.close()


def address_from_resident_id(id):
    address = query_database("Select residential_address_street_name, residential_address_street_number From Census Where resident_id='{}';".format(id))[0]
    return address


# This function is used to determine a cutoff for when we should start counting water meter readings.
def get_last_adjustment(house_address):
    adjustments = query_database(("Select prior_date, Water.current_date From Water " + match_residential_house +
                                  "And transaction_type='Adjustment'" + sort_by_date)
                                 .format(house_address[0], house_address[1], house_address[2], house_address[3], house_address[3]))

    if len(adjustments) == 0:
        last_adjustment = "0000-00-00 00:00:00"  # the beginning of time will be before everything
    else:
        last_adjustment = adjustments[len(adjustments) - 1][1]
        if last_adjustment is None:
            last_adjustment = adjustments[len(adjustments) - 1][0]
    return last_adjustment


def date_diff(first_date, last_date):
    date_format = "%Y-%m-%d %H:%M:%S"
    first = datetime.strptime(first_date, date_format)
    last = datetime.strptime(last_date, date_format)
    total_days = (last - first).days
    return total_days


def try_combinations(first, last):
    if first[0] is not None:
        if last[1] is not None:
            try:
                return date_diff(first[0], last[1])
            except:
                pass
        if last[0] is not None:
            try:
                return date_diff(first[0], last[0])
            except:
                pass
    if first[1] is not None:
        if last[1] is not None:
            try:
                return date_diff(first[1], last[1])
            except:
                pass
        if last[0] is not None:
            try:
                return date_diff(first[1], last[0])
            except:
                pass

    return None


def get_days(house_address):
    last_adjustment = get_last_adjustment(house_address)

    dates = query_database(("Select prior_date, Water.current_date From Water " + match_residential_house + before_date +
                       "And (transaction_type='Charge' or transaction_type='AC') " + sort_by_date)
                  .format(house_address[0], house_address[1], house_address[2], house_address[3], house_address[3],
                          last_adjustment, last_adjustment))

    try:
        first_prior_date = dates[0][0]
    except:
        first_prior_date = None
    try:
        first_current_date = dates[0][1]
    except:
        first_current_date = None
    try:
        last_prior_date = dates[len(dates) - 1][0]
    except:
        last_prior_date = None
    try:
        last_current_date = dates[len(dates) - 1][1]
    except:
        last_current_date = None

    total_days = try_combinations((first_prior_date, first_current_date), (last_prior_date, last_current_date))
    if total_days is None:
        global count_default
        total_days = len(dates) * 90
        count_default += len(dates)
    return total_days


def calc_average_for_houses(houses, per_household):
    averages = []
    for index in range(len(houses)):
        days = get_days(houses[index])
        if days == 0:
            print(houses[index]) # TODO remove debugging prints
        averages.append(per_household[index] / (-1 if days == 0 else days))
    return averages
