import streamlit as st

from streamlit_option_menu import option_menu

import Home, slider, split_panel_map, Cartography, cog_app, filtrage, graphe_interactive, popup, texbox, Timelapse

st.set_page_config(
        page_title="Dashboard",
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
                options=['Home','Slider','Split Panel Map','Cartography', 'cog_app', 'filtrage', 'graphe_interactive', 'popup', 'texbox', 'Timelapse'],
                icons=['house-fill','person-circle','trophy-fill', 'house-fill','person-circle','trophy-fill','trophy-fill', 'house-fill','person-circle','trophy-fill'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
        )    

        if app== 'Home':
            Home.app()
            
        if app== 'Split Panel Map':
            split_panel_map.app()
            
        if app== 'Slider':
            slider.app()

        if app== 'Cartography':
            Cartography.app()

        if app== 'cog_app':
            cog_app.app()

        if app== 'filtrage':
            filtrage.app()

        if app== 'graphe_interactive':
            graphe_interactive.app()

        if app== 'popup':
            popup.app()

        if app== 'texbox':
            texbox.app()

        if app== 'Timelapse':
            Timelapse.app()
            
    run()