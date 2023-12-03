import streamlit as st
import folium
from streamlit_folium import folium_static
from urllib.error import URLError
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
from geopy.distance import geodesic
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import tempfile
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

def find_two_nearest_hotels(gdf, entered_coords):
    gdf['distance'] = gdf.apply(lambda row: geodesic(entered_coords, (row['geometry'].y, row['geometry'].x)).km, axis=1)
    sorted_gdf = gdf.sort_values(by='distance')
    nearest_hotels = sorted_gdf.iloc[:2]
    return nearest_hotels

def capture_folium_map_as_png(map_obj, output_path):
    temp_html = tempfile.NamedTemporaryFile(delete=False)
    map_obj.save(temp_html.name)

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    driver.get(f'file://{temp_html.name}')

    time.sleep(5)

    driver.save_screenshot(output_path)

    driver.quit()

    temp_html.close()

def convert_png_to_pdf(png_path, pdf_path, entered_coords, nearest_hotels, folium_map):
    image = Image.open(png_path)
    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer, pagesize=image.size)
    pdf.drawInlineImage(png_path, 0, 0, width=image.width, height=image.height)

    # Add entered coordinates to the PDF
    pdf.drawString(10, 10, f"Entered Coordinates: {entered_coords}")

    # Capture information from Folium popups before adding markers
    popup_info = []
    for layer in folium_map._children:
        if isinstance(layer, folium.Marker):
            latitude, longitude = layer.location[0], layer.location[1]
            popup_text = layer.options.get('popup', '').replace("<br>", "\n")  # Convert HTML line breaks to newlines
            popup_info.append((latitude, longitude, popup_text))

    # Add information from Folium popups to the PDF
    pdf.drawString(10, 20, "Information from Popups:")
    for info in popup_info:
        latitude, longitude, popup_text = info
        pdf.drawString(20, 30, f"Marker at Coordinates: ({latitude}, {longitude})")
        pdf.drawString(30, 40, f"Popup Information: {popup_text}")

    # Add nearest hotels to the PDF
    pdf.drawString(10, 100, "Nearest Hotels:")
    for index, row in nearest_hotels.iterrows():
        pdf.drawString(20, 110 + (index * 10), f"Hotel: {row['Hotel name']} (Distance: {row['distance']:.2f} km)")

        # Add hotel coordinates as a separate line
        pdf.drawString(30, 120 + (index * 10), f"Coordinates: ({row['geometry'].y}, {row['geometry'].x})")

    pdf.save()

    pdf_buffer.seek(0)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

def main():
    st.title("Search by coordinates")

    carte = folium.Map(location=[33.379103, -6.430229], zoom_start=6)

    coords_input = st.text_input("Enter coordinates (format : latitude, longitude):")

    if st.button("Search"):
        try:
            for layer in carte._children:
                if isinstance(layer, folium.Marker):
                    layer.add_to(carte)

            if coords_input:
                entered_latitude, entered_longitude = map(float, coords_input.split(','))
                df = pd.read_parquet("donnee/Hotels.parquet", engine='fastparquet')  # Assuming the file is in the same directory
                df['geometry'] = df['geometry'].apply(lambda x: loads(x))
                gdf = gpd.GeoDataFrame(df, geometry='geometry')

                hotel_found = False
                for index, row in gdf.iterrows():
                    latitude, longitude = row['geometry'].y, row['geometry'].x

                    if latitude == entered_latitude and longitude == entered_longitude:
                        hotel_found = True
                        folium.Marker(
                            location=[latitude, longitude],
                            popup=f"Hotel: {row['Hotel name']}",
                            icon=folium.Icon(color='red')
                        ).add_to(carte)

                if not hotel_found:
                    st.warning("Entered coordinates doesn't correspond to a hotel, Here is the entered position (yellow) with the two nearest hotels(green).")
                    folium.Marker(
                        location=[entered_latitude, entered_longitude],
                        popup=folium.Popup(f"Entered coordinates: {entered_latitude}, {entered_longitude}",max_width=1000),
                        icon=folium.Icon(color='orange')
                    ).add_to(carte)

                    reference_coords = (entered_latitude, entered_longitude)
                    nearest_hotels = find_two_nearest_hotels(gdf, reference_coords)

                    for index, row in nearest_hotels.iterrows():
                        latitude, longitude = row['geometry'].y, row['geometry'].x

                        folium.Marker(
                            location=[latitude, longitude],
                            popup=folium.Popup(f"Hotel: {row['Hotel name']} (Distance: {row['distance']:.2f} km)", max_width=1000),
                            icon=folium.Icon(color='green')
                        ).add_to(carte)


                for index, row in gdf.iterrows():
                    try:
                        latitude, longitude = row['geometry'].y, row['geometry'].x

                        folium.CircleMarker(
                            location=[latitude, longitude],
                            radius=5,
                            color='blue',
                            fill=True,
                            popup=folium.Popup(f"Hotel: {row['Hotel name']}", max_width=1000),
                            fill_color='blue',
                            
                        ).add_to(carte)
                    except Exception as e:
                        st.warning(f"Erreur lors de l'extraction des coordonnées pour l'hôtel {row['Hotel name']} : {e}")

            else:
                st.warning("No entered coordinates!")
                
                for index, row in nearest_hotels.iterrows():
                    latitude, longitude = row['geometry'].y, row['geometry'].x

                    folium.Marker(
                        location=[latitude, longitude],
                        popup=folium.Popup(f"Hotel: {row['Hotel name']} (Distance: {row['distance']:.2f} km)", max_width=1000 ),
                        icon=folium.Icon(color='green')
                    ).add_to(carte)

                for index, row in gdf.iterrows():
                    try:
                        latitude, longitude = row['geometry'].y, row['geometry'].x

                        folium.CircleMarker(
                            location=[latitude, longitude],
                            radius=5,
                            color='blue',
                            fill=True,
                            fill_color='blue',
                            popup=f"Hotel: {row['Hotel name']}"
                        ).add_to(carte)
                    except Exception as e:
                        st.warning(f"Erreur lors de l'extraction des coordonnées pour l'hôtel {row['Hotel name']} : {e}")

            # Display the Folium map
            folium_static(carte)

            # Save map as PNG and convert to PDF
            screenshot_path = 'output.png'
            pdf_path = 'output.pdf'

            capture_folium_map_as_png(carte, screenshot_path)
            convert_png_to_pdf(screenshot_path, pdf_path, coords_input, nearest_hotels, carte)

            st.success('PDF done ✅')
            
            # Utiliser st.file_download pour télécharger le fichier PDF
            with open(pdf_path, 'rb') as f:
                st.download_button("click here to download PDF", f, key='pdf_download_button', help="click here to download PDF", file_name='output.pdf', mime='application/pdf')

        except URLError as e:
            st.error(f"Erreur d'URL : {e}")

        except Exception as e:
            st.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()
