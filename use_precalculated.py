
from helpers import *

conn = establish_connection("student.sqlite")
count_default = 0


gpd = query(conn, "Select address_street_name, address_street_number, service_id, gal_per_day From WaterCustomers Where meter_status='normal' and service_type='Residential' Order by gal_per_day")
print_to_csv("gpd.csv", gpd, "Street Name,Street Address,Service ID,Gallons per Day\n", 4)