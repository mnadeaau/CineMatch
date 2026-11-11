import streamlit as st
st.markdown("""
<style>
    /* Clean movie card styling on results */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-radius: 12px !important;
        background: rgba(36, 46, 70, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)
import common
import tmdb_client as tmdb

common.header()
st.header("Trending now")

window = st.radio("Show me", ["day", "week"], index=1, horizontal=True,
                  format_func=lambda w: "Today" if w == "day" else "This week")
try:
    with st.spinner("Loading…"):
        movies = tmdb.get_movies(tmdb.trending(window)[:12])
    if not movies:
        st.warning("Nothing to show right now. Please try again in a moment.")
    for m in movies:
        common.show_card(m)
except tmdb.TMDBError as e:
    st.error(f"⚠️ {e}")
