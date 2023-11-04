import streamlit as st
import requests
from geopy.distance import geodesic
import threading
import time

# Function to check for available vehicles
def check_vehicles(lat, lon, city_id, radius=1):
    while True:
        try:
            response = requests.get(f'https://www.reservauto.net/WCF/LSI/LSIBookingServiceV3.svc/GetAvailableVehicles?BranchID={city_id}&LanguageID=2')
            if response.status_code == 200:
                vehicles = response.json().get('d', {}).get('Vehicles', [])
                found_vehicle = False
                for vehicle in vehicles:
                    vehicle_coords = (vehicle['Latitude'], vehicle['Longitude'])
                    user_coords = (lat, lon)
                    if geodesic(vehicle_coords, user_coords).kilometers <= radius:
                        msg = f"CarID {vehicle['CarNo']}, {vehicle['CarPlate']}"
                        requests.post('https://ntfy.sh/communauto', data=msg)
                        st.write(msg)
                        found_vehicle = True
                        break  # Exit after the first found vehicle
                if not found_vehicle:
                    st.write("No vehicles available at the moment.")
            else:
                st.error("Failed to fetch vehicles from API.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        time.sleep(10)  # Sleep for 1 minute


def stop_checking():
    st.session_state['is_checking'] = False
    st.session_state['checker_thread'].join()
    st.session_state['checker_thread'] = None  # Reset the thread object
    st.success("Checking has been stopped.")

def main():
    st.title("Vehicle Availability Checker")
    city = {"calgary":10}
    with st.form("vehicle_checker_form"):
        lat_long_str = st.text_area("Enter Latitude and Longitude in the format (lat, long)","(51.0469234, -114.0863985)" )
        lat_long = lat_long_str.strip('()').split(',')
        latitude = float(lat_long[0])
        longitude = float(lat_long[1])
        city_id = st.number_input("Enter City ID", value=10, format="%d")
        radius = st.number_input("Enter Radius in km", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        submitted = st.form_submit_button("Start Checking")

    if submitted:
        check_vehicles(latitude, longitude, city_id, radius=radius)
        st.success("Started checking for available vehicles...")



main()
