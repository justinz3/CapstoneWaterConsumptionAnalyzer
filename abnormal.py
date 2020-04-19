
from helpers import *

from datetime import datetime
import statistics
import csv

# conn = establish_connection("student.sqlite")
# count_default = 0
#
# abnormal_addresses = query(conn, "Select address_street_number, address_street_name From WaterCustomers  \
#                   Where meter_status='anomaly' and service_type='Residential'")
# print(abnormal_addresses)
#
# readings = []
#
# for address in abnormal_addresses:
#     q = query(conn, "Select * from Water Where address_street_number == '{}' and address_street_name == '{}'".format(address[0], address[1]))
#     for reading in q:
#         readings.append(reading)
#
# print(readings)

# print_to_csv("abnormal_readings.csv", readings, "id,service_id,address_street_number,address_street_name,service_type,"
#                                                 "description,service,current_date,prior_date,current_reading,prior_reading,"
#                                                 "account_number,meter_number,transaction_date,transaction_type,units\n", 16)

# Verify that the .csv file can be read
with open('abnormal_readings.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        print(', '.join(row))
# households = query(conn, "Select Distinct address_street_name, address_street_number, service_id From Water")
# # streets = query(conn, "Select Distinct address_street_name From Water")
# no_water_houses = []
# per_household = []
# for house in households:
#
#     last_adjustment = analysis.get_last_adjustment(house)
#
#     result = query(conn, "Select current_reading, prior_reading From Water Where address_street_name='{}' \
#                          And address_street_number='{}' And service_id='{}' And (prior_reading!=current_reading or prior_reading is Null or current_reading is Null) \
#                          And (prior_date!=Water.current_date or prior_date is Null or Water.current_date is Null) And (Water.current_date>'{}' Or prior_date>'{}') And transaction_type='Charge'\
#                          Order By prior_date, Water.current_date Asc;".format(house[0], house[1], house[2], last_adjustment, last_adjustment))
#     # TODO properly debug this section, it likely doesn't process the readings correctly
#     total = 0
#     if len(result) == 0:
#         per_household.append(0)
#         no_water_houses.append(house)
#         continue
#     prev = int(result[0][0])
#     for i in range(len(result)):
#         if result[i][0] is not None and result[i][1] is int:
#             prev = int(result[i][1])
#             print("used prior")
#         if int(result[i][0]) - prev < 0:
#             # meter was (likely) reset
#             prev = 0
#         total += int(result[i][0]) - prev
#         prev = int(result[i][0])
#
#     total *= cubic_ft_to_gallons
#
#     per_household.append(total)