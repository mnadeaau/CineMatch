"""
2_Smart_Search.py  --  SECTION 4d: NATURAL LANGUAGE QUERY INTERFACE (enhanced feature)
The user types a sentence; parse_query() (nlp_utils.py) converts it into filters.
The page repeats back what it understood so the user can spot and correct mistakes.
"""
import streamlit as st
import common
import tmdb_client as tmdb
from nlp_utils import parse_query

common.header()
st.header("Smart Search")
st.write("Describe what you want in plain English. For example: "
         "*funny 90s movies under 2 hours, not horror* or *family animation from the 2000s rated 7*.")

query = st.text_input("What are you in the mood for?")

if st.button("Search", type="primary"):
    if not query.strip():
        st.warning("Please type something first.")
    else:
        filters, understood = parse_query(query)
        # EDGE CASE: nothing recognised (e.g. "asdfgh"). Give hints rather than showing random movies.
        if not understood:
            st.warning("I couldn't find any filters in that. Try mentioning a genre, a decade, "
                       "a length (like 'under 2 hours') or a rating (like 'rated 7').")
        else:
            st.markdown("**I understood:** " + " · ".join(understood))
            # Plain-English searches default to movies with 300+ votes so results are well-known titles.
            # setdefault only applies this if the user did not already specify something else.
            filters.setdefault("vote_count.gte", 300)
            try:
                with st.spinner("Searching…"):
                    results, total = tmdb.discover(filters)
                    movies = tmdb.get_movies([m["id"] for m in results])
                if not movies:
                    st.warning("Nothing matched. Try fewer or looser requirements.")
                else:
                    st.success(f"{total:,} movies match. Showing the first {len(movies)}.")
                    for m in movies:
                        common.show_card(m)
            except tmdb.TMDBError as e:
                st.error(f"⚠️ {e}")
