import os
import leafmap.foliumap as leafmap
import streamlit as st
from branca.colormap import linear

# Function to get all image files in a folder
def get_image_files(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.tif', '.tiff'))]
    return image_files

# Function to display split map
def display_split_map(left_layer, right_layer, c):
    m = leafmap.Map()
    m.split_map(left_layer=left_layer, right_layer=right_layer)
        
    m.add_child(c)    

    with st.container():
        m.to_streamlit(height=700)

# Streamlit app
st.title("Split panel map ")

# Select folder
selected_folder = st.selectbox("Select attribute", ["visitors", "moroccans", "foreigners"])

# Get image files from selected folder
folder_images = get_image_files(os.path.join('donnee', selected_folder))

# Select two images from the selected folder
selected_images = st.multiselect(f"Select 2 Images in {selected_folder}", folder_images, key="selected_images", default=[])

# Display split map with the selected images
if len(selected_images) == 2:
    if selected_folder == 'visitors':
# Add a Choropleth legend
        c = linear.viridis.scale(0, 70)
        c.caption = 'Visitors'
        
    elif selected_folder == 'moroccans':
        # Add a Choropleth legend
        c = linear.viridis.scale(0, 50)
        c.caption = 'Moroccans'

    elif selected_folder == 'foreigners':
        # Add a Choropleth legend
        c = linear.viridis.scale(0, 20)
        c.caption = 'Foreigners'

    display_split_map(os.path.join('donnee', selected_folder, selected_images[0]),
                      os.path.join('donnee', selected_folder, selected_images[1]),
                      c)
else:
    st.warning("Please select exactly 2 images.")
