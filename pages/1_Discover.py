from datetime import date

import streamlit as st
import common
import tmdb_client as tmdb

common.header()
st.header("Discover")


@st.cache_data(ttl=86400)           # remember the genre list for a day
def get_genres():
    return tmdb.genre_map()


LANGUAGES = {"Any": None, "English": "en", "French": "fr", "Spanish": "es", "Korean": "ko",
             "Japanese": "ja", "Hindi": "hi", "German": "de", "Italian": "it", "Chinese": "zh"}
SORTS = {"Most popular": "popularity.desc", "Highest rated": "vote_average.desc",
         "Newest": "primary_release_date.desc"}

try:
    genres = get_genres()
    name_to_id = {name: gid for gid, name in genres.items()}

    # A form means nothing runs until the user presses the button
    with st.form("filters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("When & quality")
            years = st.slider("Release years", 1920, date.today().year, (1990, date.today().year))
            min_rating = st.slider("Minimum rating", 0.0, 10.0, 6.5, 0.5)
            min_votes = st.number_input("Minimum number of votes", 0, 100000, 500, 100)
        with col2:
            st.subheader("Content & people")
            runtime = st.slider("Runtime (minutes)", 40, 240, (60, 200))
            cert = st.selectbox("Maximum age rating (US)", ["Any", "G", "PG", "PG-13", "R", "NC-17"])
            language = st.selectbox("Original language", list(LANGUAGES))
            director = st.text_input("Director", placeholder="e.g. Ron Howard")
            actor = st.text_input("Actor", placeholder="e.g. Tom Hanks")
        with col3:
            st.subheader("Genres")
            include = st.multiselect("Include genres", list(name_to_id))
            mode = st.radio("Combine them with", ["ALL of them (AND)", "ANY of them (OR)"])
            exclude = st.multiselect("Exclude genres (NOT)", list(name_to_id))
            sort = st.selectbox("Sort by", list(SORTS))
        submitted = st.form_submit_button("🔍 Find movies", type="primary")

    if submitted:
        if set(include) & set(exclude):
            st.error("A genre can't be both included and excluded. Please fix one of them.")
        else:
            f = {"primary_release_date.gte": f"{years[0]}-01-01",
                 "primary_release_date.lte": f"{years[1]}-12-31",
                 "vote_average.gte": min_rating,
                 "vote_count.gte": int(min_votes),
                 "with_runtime.gte": runtime[0],
                 "with_runtime.lte": runtime[1],
                 "sort_by": SORTS[sort]}
            if cert != "Any":
                f["certification_country"] = "US"
                f["certification.lte"] = cert
            if LANGUAGES[language]:
                f["with_original_language"] = LANGUAGES[language]
            if include:
                joiner = "," if mode.startswith("ALL") else "|"
                f["with_genres"] = joiner.join(str(name_to_id[g]) for g in include)
            if exclude:
                f["without_genres"] = ",".join(str(name_to_id[g]) for g in exclude)

            # People: look up their ID first (and warn if we can't find them)
            for label, name, is_director, key in [("director", director, True, "with_crew"),
                                                  ("actor", actor, False, "with_cast")]:
                if name.strip():
                    found = tmdb.search_person(name.strip(), is_director)
                    if found:
                        f[key] = found[0]
                        st.caption(f"Matched {label}: **{found[1]}**")
                    else:
                        st.warning(f"Couldn't find a {label} called '{name}'. Check the spelling.")

            with st.spinner("Searching…"):
                results, total = tmdb.discover(f)
                movies = tmdb.get_movies([m["id"] for m in results])

            if not movies:
                st.warning("No movies matched all of those filters. Try loosening one "
                           "(for example, lower the minimum rating or votes).")
            else:
                st.success(f"{total:,} movies match. Showing the first {len(movies)}.")
                for m in movies:
                    common.show_card(m)
except tmdb.TMDBError as e:
    st.error(f"⚠️ {e}")
