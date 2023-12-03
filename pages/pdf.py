import os
import leafmap.foliumap as leafmap
import streamlit as st
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

# Function to get all image files in a folder
def get_image_files(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.tif', '.tiff'))]
    return image_files

# Function to display split map
def display_split_map(left_layer, right_layer):
    m = leafmap.Map()
    m.split_map(left_layer=left_layer, right_layer=right_layer)
    with st.container():
        m.to_streamlit(height=700)

    return m

# Function to convert PNG to PDF
def convert_png_to_pdf(png_path, pdf_path):
    image = Image.open(png_path)
    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer, pagesize=image.size)
    pdf.drawInlineImage(png_path, 0, 0, width=image.width, height=image.height)

    pdf.save()

    pdf_buffer.seek(0)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

# Streamlit app
st.title("Choose Images to Display")

# Select folder
selected_folder = st.sidebar.selectbox("Select Folder", ["visitors", "moroccans", "foreigners"])

# Get image files from selected folder
folder_images = get_image_files(os.path.join('donnee', selected_folder))

# Select two images from the selected folder
selected_images = st.sidebar.multiselect(f"Select 2 Images in {selected_folder}", folder_images, key="selected_images", default=[])

# Display split map with the selected images
if len(selected_images) == 2:
    split_map = display_split_map(os.path.join('donnee', selected_folder, selected_images[0]),
                                  os.path.join('donnee', selected_folder, selected_images[1]))

    # Export button in the sidebar
    export_button = st.sidebar.button("Export PDF")

    if export_button:
        screenshot_path = os.path.join('output', 'output.png')
        pdf_path = os.path.join('output', 'output.pdf')

        # Save the split map as PNG using the screenshot method
        split_map.screenshot(screenshot_path)

        # Convert PNG to PDF
        convert_png_to_pdf(screenshot_path, pdf_path)

        st.success('Conversion terminée! Téléchargez le PDF ci-dessous:')

        # Use st.download_button to provide the download link
        with open(pdf_path, 'rb') as f:
            st.download_button('Télécharger le PDF', f, key='pdf_download_button',
                               help="Cliquez pour télécharger le PDF", file_name='output.pdf', mime='application/pdf')

else:
    st.warning("Please select exactly 2 images.")
