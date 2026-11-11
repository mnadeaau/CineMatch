import streamlit as st
import common

common.header()

st.write("### Welcome!")
st.write("CineMatch helps you decide what to watch. Use the menu on the **left** to:")
st.markdown("""
- **Discover**: filter movies by year, rating, length, age rating, language, people and genres
- **Smart Search**: just type what you want, like *funny 90s movies under 2 hours, not horror*
- **Similar Movies**: pick a movie you love and see matches, with the reasons why
- **Trending**: see what everyone is watching right now
""")
st.caption("Data comes from The Movie Database (TMDB).")
