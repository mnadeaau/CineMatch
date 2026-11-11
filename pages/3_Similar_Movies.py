import streamlit as st
import common
import tmdb_client as tmdb
from recommender import rank_similar

common.header()
st.header("Movies like…")

title = st.text_input("Type a movie you love", placeholder="Inception")

try:
    if title.strip():
        hits = tmdb.search_movies(title.strip())
        if not hits:
            st.warning("I couldn't find a movie with that title. Check the spelling.")
        else:
            choice = st.selectbox("Did you mean…", hits,
                                  format_func=lambda h: f"{h['title']} ({h['year']})")
            st.caption("How much should each ingredient matter?")
            c1, c2, c3 = st.columns(3)
            w_content = c1.slider("Story, genre, cast", 0.0, 1.0, 0.6)
            w_mood = c2.slider("Similar mood", 0.0, 1.0, 0.2)
            w_quality = c3.slider("Audience rating", 0.0, 1.0, 0.2)

            if st.button("Find similar movies", type="primary"):
                if w_content + w_mood + w_quality == 0:
                    st.warning("Please give at least one ingredient some weight.")
                else:
                    with st.spinner("Reading plots and comparing movies…"):
                        seed = tmdb.get_movie(choice["id"])
                        pool = tmdb.get_movies(tmdb.related_ids(choice["id"])[:30])
                        ranked = rank_similar(seed, pool, w_content, w_mood, w_quality)
                    if not ranked:
                        st.warning("Not enough related movies were found for that title.")
                    else:
                        st.subheader(f"Because you liked {seed['title']}")
                        for m in ranked[:8]:
                            scores = (f"Match score {m['score']:.2f}  (content {m['content']:.2f} · "
                                      f"mood {m['mood']:.2f} · quality {m['quality']:.2f})")
                            common.show_card(m, reason=m["why"], scores=scores)
except tmdb.TMDBError as e:
    st.error(f"⚠️ {e}")
