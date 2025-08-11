"""
Global Disaster Visualization Program
====================================
This program retrieves and visualizes global fire and earthquake data using Plotly.
It downloads fire data from a CSV file and earthquake data from the USGS API, then
creates interactive scattergeo plots to display the data on a world map. The program
is designed to be modular, user-friendly, and well-documented for maintainability.

Author: Orr, Aaron
Date: August 09, 2025
Ethical Note: Data is sourced from public repositories (NASA and USGS). Proper
attribution is maintained, and no proprietary data is used to avoid plagiarism or
copyright issues.
"""

import requests
import csv
import json
from plotly.graph_objs import Scattergeo, Layout
from plotly import offline

def fetch_fire_data():
    """
    Downloads global fire data from a CSV file and extracts latitude, longitude,
    and brightness values.
    
    Returns:
        tuple: Lists of latitudes, longitudes, and brightness values.
    """
    url = 'https://raw.githubusercontent.com/ehmatthes/pcc_2e/master/chapter_16/mapping_global_data_sets/data/world_fires_1_day.csv'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        with open('world_fires_1_day.csv', 'wb') as f:
            f.write(response.content)
        
        with open('world_fires_1_day.csv') as f:
            reader = csv.reader(f)
            header_row = next(reader)
            
            try:
                lat_index = header_row.index('latitude')
                lon_index = header_row.index('longitude')
                bright_index = header_row.index('brightness')
            except ValueError:
                print("Error: CSV file does not contain expected columns.")
                return [], [], []
            
            lats, lons, brightnesses = [], [], []
            for row in reader:
                try:
                    lat = float(row[lat_index])
                    lon = float(row[lon_index])
                    bright = float(row[bright_index])
                    lats.append(lat)
                    lons.append(lon)
                    brightnesses.append(bright)
                except ValueError:
                    continue
            return lats, lons, brightnesses
    except requests.RequestException as e:
        print(f"Error fetching fire data: {e}")
        return [], [], []

def fetch_earthquake_data():
    """
    Retrieves earthquake data from the USGS API and extracts magnitude, latitude,
    longitude, and titles.
    
    Returns:
        tuple: Lists of magnitudes, longitudes, latitudes, and hover texts.
    """
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'
    try:
        response = requests.get(url)
        response.raise_for_status()
        all_eq_data = response.json()
        
        mags, lons, lats, hover_texts = [], [], [], []
        for eq_dict in all_eq_data['features']:
            mag = eq_dict['properties']['mag']
            if mag is None:
                continue
            lon = eq_dict['geometry']['coordinates'][0]
            lat = eq_dict['geometry']['coordinates'][1]
            title = eq_dict['properties']['title']
            mags.append(mag)
            lons.append(lon)
            lats.append(lat)
            hover_texts.append(title)
        return mags, lons, lats, hover_texts
    except requests.RequestException as e:
        print(f"Error fetching earthquake data: {e}")
        return [], [], [], []

def plot_data(lons, lats, values, title, colorbar_title, colorscale, reverse_scale, text=None):
    """
    Creates a scattergeo plot using Plotly and saves it as an HTML file.
    
    Args:
        lons (list): Longitudes of data points.
        lats (list): Latitudes of data points.
        values (list): Values for marker size or color (e.g., brightness or magnitude).
        title (str): Title of the plot.
        colorbar_title (str): Title for the colorbar.
        colorscale (str): Plotly colorscale for markers.
        reverse_scale (bool): Whether to reverse the colorscale.
        text (list, optional): Hover text for data points.
    """
    data = [{
        'type': 'scattergeo',
        'lon': lons,
        'lat': lats,
        'text': text if text else [],
        'marker': {
            'size': [max(5 * val, 5) if colorbar_title == 'Magnitude' else 10 for val in values],
            'color': values,
            'colorscale': colorscale,
            'reversescale': reverse_scale,
            'colorbar': {'title': colorbar_title},
        },
    }]
    my_layout = Layout(title=title)
    fig = {'data': data, 'layout': my_layout}
    filename = f"{title.lower().replace(' ', '_')}.html"
    offline.plot(fig, filename=filename)
    print(f"Plot saved as {filename}")

def main():
    """
    Main function to interact with the user and execute the visualization program.
    """
    print("Global Doomsday Disaster Visualization Program")
    print("1. Dude thats a lot of Fire Activity")
    print("2. Dude thats a lot of Earthquakes (Past 24 Hours)")
    print("3. Exit")
    
    while True:
        choice = input("Enter your choice (1-3): ")
        if choice == '1':
            lats, lons, brightnesses = fetch_fire_data()
            if lats:
                plot_data(lons, lats, brightnesses, 'Global Fire Activity', 'Brightness', 'YlOrRd', False)
            else:
                print("No fire data available to plot.")
        elif choice == '2':
            mags, lons, lats, hover_texts = fetch_earthquake_data()
            if lats:
                plot_data(lons, lats, mags, 'Global Earthquakes (Past 24 Hours)', 'Magnitude', 'Viridis', True, hover_texts)
            else:
                print("No earthquake data available to plot.")
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == '__main__':
    main()
