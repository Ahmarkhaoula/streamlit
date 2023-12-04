import leafmap 
import streamlit 

def app():
    m = leafmap.Map()
    url = 'https://khaoulanas.s3.ca-central-1.amazonaws.com/cog/output.cog.tif'
    m.add_cog_layer(url, name="Fire (pre-event)")
    m.to_streamlit()