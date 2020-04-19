
from helpers import *

import statistics


def print_to_csv(file_loc, data):
    # this function assumes that data a list with items in the format of: (tuple, int)
    f = open(file_loc, "w")
    # data[0] should be a tuple
    is_houses = len(data[0][0]) >= 2 # it's a household (it has a street address number), otherwise, it's a street
    f.write("Street,Street Address,Service_ID,Meter Number,Average Gallons Per Day\n" if is_houses else "Street,Average Gallons Per Day\n")
    for i in range(len(data)):
        f.write("{},{},{},{},".format(data[i][0][0], data[i][0][1], data[i][0][2], data[i][0][3]) if is_houses else "{},".format(data[i][0][0]))

        # print average gallons per day
        f.write("{}\n".format(data[i][1]))
    f.close()


households = query_database("Select Distinct address_street_name, address_street_number, service_id, meter_number "
                            "From Water Where service_type='Residential' And meter_number!=''")
streets = query_database("Select Distinct address_street_name From Water")

# print households[0]
# last_adjust = get_last_adjustment(households[0])
# request = ("Select current_reading, prior_reading From Water " + match_residential_house + before_date + " And (transaction_type='Charge' or transaction_type='AC') "\
#           + sort_by_date).format(households[0][0], households[0][1], households[0][2], households[0][3], last_adjust, last_adjust)
# print request
# print query_database(request)
# exit(0)

households = [x for x in households if (len(x[3]) == 0 or not x[3][len(x[3]) - 1] == 'X')]

no_water_houses = []
per_household = []
for house in households:

    last_adjustment = get_last_adjustment(house)

    result = query_database(("Select current_reading, prior_reading From Water " + match_residential_house + before_date + \
                        "And (transaction_type='Charge' or transaction_type='AC')"
                  + sort_by_date).format(house[0], house[1], house[2], house[3], house[3], last_adjustment, last_adjustment))
    # And (prior_reading!=current_reading or prior_reading is Null or current_reading is Null) \
    #                          And (prior_date!=Water.current_date or prior_date is Null or Water.current_date is Null)
    # Note: those conditions in the query do not seem to do anything as values will typically be '' and not Null

    # prior_reading = query_database("Select prior_reading From Water Where address_street_name='{}' \
    #                      And address_street_number='{}' And service_id='{}' And Not(prior_reading==current_reading And current_reading Is Not Null And prior_reading Is Not Null) \
    #                      And Not(prior_date==Water.current_date And Water.current_date Is Not Null And prior_date Is Not Null) And transaction_type='Charge' \
    #                      Order By prior_date, Water.current_date Asc;".format(house[0], house[1], house[2]))

    # TODO properly debug this section, it likely doesn't process the readings correctly
    total = 0
    if len(result) == 0:
        per_household.append(0)
        no_water_houses.append(house)
        continue
    prev = int(result[0][0])
    for i in range(len(result)):
        if result[i][0] == result[i][1]:
            continue
        if result[i][0] == '':
            print 'empty'
        if result[i][0] is not None and result[i][1] is int:
            prev = int(result[i][1])
            print("used prior")
        if int(result[i][0]) - prev < 0:
            # meter was (likely) reset
            prev = 0
        total += int(result[i][0]) - prev
        prev = int(result[i][0])

    total *= cubic_ft_to_gallons
    per_household.append(total)

average_per_house = calc_average_for_houses(households, per_household)

consumption_per_street = []
for street in streets:
    total = 0
    houses = query_database("Select Distinct address_street_name, address_street_number, service_id, meter_number From Water \
                         Where address_street_name='{}' And meter_number!='';".format(street[0]))
    for house in houses:
        try:
            total += average_per_house[households.index(house)]
        except:
            pass
    # print street  # acts as a progress bar of sorts (because names should be in alphabetical order)
    consumption_per_street.append(total)


household_data = []
for i in range(len(households)):
    household_data.append((households[i], average_per_house[i]))

# merge streets and average_per_house_per_street
street_data = []
for i in range(len(streets)):
    street_data.append((streets[i], consumption_per_street[i]))

count_300 = 0
count_500 = 0
count_1000 = 0
for i in range(len(households)):
    if average_per_house[i] > 300:
        count_300 += 1
    if average_per_house[i] > 500:
        count_500 += 1
    if average_per_house[i] > 1000:
        count_1000 += 1

print("Number of houses using >300 Gallons per day: " + str(count_300))
print("Number of houses using >500 Gallons per day: " + str(count_500))
print("Number of houses using >1000 Gallons per day: " + str(count_1000))
print("Number of incomplete sets of dates: " + str(count_default))
print("Average gallons per day per household " + str(statistics.mean(average_per_house)))
print(no_water_houses)

print_to_csv("HouseAverageGPD.csv", household_data)
print_to_csv("StreetAverageGPD.csv", street_data)



