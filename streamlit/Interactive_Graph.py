import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from shapely.wkb import loads
import plotly.express as px
import plotly.io as pio



def wkb_to_geometry(wkb):
    try:
        return loads(wkb)
    except Exception as e:
        st.warning(f"Erreur lors de la conversion WKB vers geometry : {e}")
        return None

def on_map_click(event, df, st):
    lat, lon = event.latlng

    distances = [(index, abs(hotel["geometry"].y - lat) + abs(hotel["geometry"].x - lon)) for index, hotel in df.iterrows()]
    closest_hotel_index = min(distances, key=lambda x: x[1])[0]

    st.session_state.selected_hotel_index = closest_hotel_index

def app():
    st.title("Pop-up displaying attributes variation as interactive chart")
    st.markdown("From the popup, copy the name of the hotel and paste it in the down box ")

    df = pd.read_parquet(r'D:\iav\3ci\S5\web_mapping\streamlit\donnee\Hotels.parquet')

    df['geometry'] = df['geometry'].apply(wkb_to_geometry)

    carte = folium.Map(location=[33.379103, -6.430229], zoom_start=6)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            popup=folium.Popup(f" {row['Hotel name']}", max_width=1000),
        ).add_to(carte)

    folium_static(carte, width=1000, height=800)

    if 'selected_hotel_index' not in st.session_state:
        st.session_state.selected_hotel_index = None

    selected_hotel_index = st.session_state.selected_hotel_index

    selected_hotel_name = st.text_input("Selected hotel name ", value="" if selected_hotel_index is None else df.loc[selected_hotel_index, 'Hotel name'])

    fig = st.session_state.get('fig', None)  # Retrieve fig from session state

    if st.button("Validate selection"):
        selected_hotel_index = df[df['Hotel name'] == selected_hotel_name].index[0]
        st.session_state.selected_hotel_index = selected_hotel_index

        if selected_hotel_index is not None:
            selected_hotel = df.loc[selected_hotel_index, 'Hotel name']
            st.write(f"Selected Hotel: {selected_hotel}")

            hotel_data = df[df['Hotel name'] == selected_hotel].squeeze()

            visitors_data = [
                hotel_data['Visitors J-6'],
                hotel_data['Visitors J-5'],
                hotel_data['Visitors J-4'],
                hotel_data['Visitors J-3'],
                hotel_data['Visitors J-2'],
                hotel_data['Visitors yesterday (J-1)'],
                hotel_data['Visitors today (J)']
            ]

            moroccans_data = [
                hotel_data['Moroccans J-6'],
                hotel_data['Moroccans J-5'],
                hotel_data['Moroccans J-4'],
                hotel_data['Moroccans J-3'],
                hotel_data['Moroccans J-2'],
                hotel_data['Moroccans yesterday (J-1)'],
                hotel_data['Moroccans today (J)']
            ]

            foreigners_data = [
                hotel_data['Foreigners J-6'],
                hotel_data['Foreigners J-5'],
                hotel_data['Foreigners J-4'],
                hotel_data['Foreigners J-3'],
                hotel_data['Foreigners J-2'],
                hotel_data['Foreigners yesterday (J-1)'],
                hotel_data['Foreigners today (J)']
            ]

            reshaped_data = visitors_data + moroccans_data + foreigners_data

            fig = px.line(x=["J", "J-1", "J-2", "J-3", "J-4", "J-5", "J-6"] * 3,
                          y=reshaped_data,
                          color=['Visitors'] * 7 + ['Moroccans'] * 7 + ['Foreigners'] * 7,
                          labels={'x': 'Days', 'y': 'Number of visitors'},
                          title=f'Variation of visitors per day - {selected_hotel}',
                          line_shape='linear')

            st.plotly_chart(fig)

            # Save fig to session state for future reference
            st.session_state.fig = fig

    # Export to PDF button outside the 'if' condition
    if st.button("Export to PDF") and fig is not None:
        if selected_hotel_index is not None:
            selected_hotel = df.loc[selected_hotel_index, 'Hotel name']
            pdf_filename = f"{selected_hotel}_graph.pdf"
            pio.write_image(fig, pdf_filename)
            st.success(f"Graph exported to {pdf_filename}")


