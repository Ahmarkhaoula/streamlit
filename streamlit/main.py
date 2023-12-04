import streamlit as st

from streamlit_option_menu import option_menu

import Home,  Day_Slider, Split_Panel_Map, Cartography, Filtering, Interactive_Graph, popup, Search_by_coordinates, Timelapse

st.set_page_config(
        page_title="Dashboard",
        layout= 'wide'
)

class MultiApp:

    def _init_(self):
        self.apps = []
    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })    

    def run():

        with st.sidebar:
            app = option_menu(
                menu_title='Dashboard',
                options=['Home','Day Slider','Split Panel Map','Cartography', 'Filtering', 'Interactive Graph', 'popup', 'Search by coordinates', 'Timelapse'],
                icons=['house-fill','sliders','layout-split', 'pin-map','filter','graph-up', 'pin','cursor-fill','fast-forward-circle'],
                menu_icon='globe-americas',
                default_index=0,
                styles={
                    "container": {"padding": "5!important","background-color":'#047c91'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#60a7b5"},
        "nav-link-selected": {"background-color": "#044d5c"},}
                
        )    

        if app== 'Home':
            Home.app()
            
        if app== 'Split Panel Map':
            Split_Panel_Map.app()
            
        if app== 'Day Slider':
           Day_Slider.app()

        if app== 'Cartography':
            Cartography.app()

        if app== 'Filtering':
            Filtering.app()

        if app== 'Interactive Graph':
            Interactive_Graph.app()

        if app== 'popup':
            popup.app()

        if app== 'Search by coordinates':
            Search_by_coordinates.app()

        if app== 'Timelapse':
            Timelapse.app()
            
    run()