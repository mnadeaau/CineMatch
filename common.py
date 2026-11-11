"""
common.py  --  SECTION 4a: SHARED USER INTERFACE COMPONENTS
Every page calls header() and show_card(), which guarantees consistent styling, the CineMatch
wordmark (branding) on every page, and identical, readable movie results everywhere.
"""
import streamlit as st

# Simple custom styling: a bold wordmark with a red accent, and rounded "pills" for movie facts.
CSS = """
<style>
.wordmark {font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin-bottom: 0;}
.wordmark span {color: #E50914;}
.tagline {color: #888; margin-top: -6px; margin-bottom: 10px;}
.pill {display:inline-block; padding:2px 10px; margin:2px 4px 2px 0; border-radius:12px;
       background:#262730; color:#fafafa; font-size:0.8rem;}
</style>
"""


def header():
    """Call this at the very top of every page.
    set_page_config must be the first Streamlit command on a page, so it lives here."""
    st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<p class="wordmark">🎬 CINE<span>MATCH</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Find your next movie by genre, mood and taste.</p>', unsafe_allow_html=True)
    # TMDB's terms require this attribution wherever its data is shown.
    st.sidebar.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")


def money(n):
    return f"${n:,.0f}" if n else "n/a"


def show_card(m, reason=None, scores=None):
    """Draw one movie: poster on the left, facts on the right."""
    left, right = st.columns([1, 4])
    with left:
        if m.get("poster"):
            st.image(m["poster"])
    with right:
        st.markdown(f"### {m['title']} ({m['year']})")
        pills = [f"⭐ {m['rating']:.1f} ({m['votes']:,} votes)", f"⏱ {m['runtime']} min",
                 f"🔞 {m['certification']}", f"🗣 {m['language'].upper()}"] + m["genres"]
        st.markdown("".join(f'<span class="pill">{p}</span>' for p in pills), unsafe_allow_html=True)
        st.write(m["overview"] or "No plot summary available.")
        st.caption(f"Director: {', '.join(m['director']) or 'n/a'}  |  "
                   f"Cast: {', '.join(m['cast'][:4]) or 'n/a'}  |  Box office: {money(m['box_office'])}")
        if scores:
            st.caption(scores)
        if reason:
            st.info(f"**Why this?** {reason}")
    st.divider()
