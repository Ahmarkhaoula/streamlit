import streamlit as st
def app():
    st.title("GeoAnalytic Dashboard")

    st.markdown(
        "Welcome to our interactive multipage experience! Explore a variety of maps catering to different needs:")
    st.markdown( "🏨Hotel Distribution Map : Visualize the distribution of hotels in Morocco & Click on markers to view details about each hotel.🌐 ")
    st.markdown( "📆Day Slider :  Navigate through different days with a dynamic slider & Observe visitor trends using raster interpolation. 📊 ")
    st.markdown( "⬅️➡️Split Panel Map : Compare data across days seamlessly &  Drag the slider to witness changes over time. 🔁")
    st.markdown(  "🎥Timelapse GIF : Experience daily variations through an animated GIF.🔄 ")
    st.markdown("🔍Filtering Page : Refine data based on attributes or spatial queries. 🔢")
    st.markdown( "🏨Interactive Hotel Selection : Select a hotel to explore an interactive graph of daily visitors.📊 ")
    st.markdown( "📍Hotel Search by Coordinates : Enter coordinates to find the two closest hotels.🗺️")

    st.info("Click on the left sidebar menu to navigate to the different apps.")

    st.subheader("🗺️ Examples of Interactive Maps ")

    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        
         st.image("https://khaoulanas.s3.ca-central-1.amazonaws.com/cog/gif.gif")
         st.image(r'donnee\carto.png',width=320) 
  

    with row1_col2:
      
        st.image(r"donnee\graph .png",width=300)
        st.image(r'donnee\slider .png',width=300)
        

