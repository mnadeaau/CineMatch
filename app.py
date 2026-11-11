import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="CineMatch | Discover Your Next Favorite Film",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Cinema CSS Theme (Midnight Crimson & Glassmorphism)
st.markdown("""
<style>
    /* Global dark aesthetic */
    .stApp {
        background: radial-gradient(circle at top right, #1a1f2c 0%, #0d1117 60%, #080b10 100%);
        color: #f0f3f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Top Brand Header */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }
    .brand-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
    }
    .brand-highlight {
        color: #E50914; /* Cinema Crimson */
        text-shadow: 0 0 20px rgba(229, 9, 20, 0.4);
    }
    .brand-tagline {
        color: #8b949e;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 24px;
    }

    /* Hero Spotlight Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(229, 9, 20, 0.15) 0%, rgba(26, 31, 44, 0.8) 50%, rgba(13, 17, 23, 0.95) 100%),
                    url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1600&q=80') center/cover;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 36px 32px;
        margin-bottom: 32px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        position: relative;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(229, 9, 20, 0.25);
        color: #ff4d58;
        border: 1px solid rgba(229, 9, 20, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    .hero-desc {
        color: #c9d1d9;
        font-size: 1.05rem;
        max-width: 650px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* Feature Grid Cards */
    .feature-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(229, 9, 20, 0.5);
        box-shadow: 0 10px 25px rgba(229, 9, 20, 0.15);
        background: rgba(26, 32, 44, 0.85);
    }
    .card-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .card-desc {
        font-size: 0.92rem;
        color: #8b949e;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    .card-chip {
        font-size: 0.75rem;
        color: #ff6b74;
        background: rgba(229, 9, 20, 0.12);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        align-self: flex-start;
    }

    /* How It Works Steps */
    .step-box {
        background: rgba(22, 27, 34, 0.5);
        border-radius: 12px;
        border-left: 3px solid #E50914;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .step-number {
        font-weight: 800;
        color: #E50914;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-text {
        color: #e6edf3;
        font-size: 0.92rem;
        margin-top: 2px;
    }

    /* Footer styling */
    .tmdb-footer {
        margin-top: 48px;
        padding-top: 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #6e7681;
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Brand Header
st.markdown("""
<div class="brand-container">
    <span style="font-size: 2.2rem;">🎬</span>
    <h1 class="brand-title">CINE<span class="brand-highlight">MATCH</span></h1>
</div>
<div class="brand-tagline">Find your next movie by genre, mood, and algorithmic taste.</div>
""", unsafe_allow_html=True)

# 4. Cinematic Hero Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">AI-Powered Discovery Engine</div>
    <div class="hero-title">Personalized Cinema at Your Fingertips</div>
    <div class="hero-desc">
        End the scrolling fatigue. CineMatch combines deep metadata filtering, natural language processing, 
        and plot sentiment analysis to match you with stories you'll genuinely love.
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Interactive Navigation Cards (Replaces the plain bullet points)
st.markdown("### 🍿 Explore CineMatch Features")
st.caption("Select an engine from the left menu or browse what each module does:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div>
            <div class="card-icon">🔍</div>
            <div class="card-title">Discover Studio</div>
            <div class="card-desc">
                Precision filtering across release decades, minimum rating quality, runtime brackets, 
                MPAA certifications (PG-13, R), original language, and boolean genre operators (AND / OR).
            </div>
        </div>
        <div class="card-chip">Temporal & Quality Filters</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div>
            <div class="card-icon">💬</div>
            <div class="card-title">Smart Natural Search</div>
            <div class="card-desc">
                Speak in human language. Search queries like <i>"funny 90s comedy under 2 hours, not horror"</i> 
                are parsed using NLP text analysis to detect sentiment, era, and themes.
            </div>
        </div>
        <div class="card-chip">Conversational NLP</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div>
            <div class="card-icon">🎭</div>
            <div class="card-title">Similar Movies & Explanations</div>
            <div class="card-desc">
                Select any film you adore. Our hybrid recommendation engine analyzes TF-IDF keywords, 
                director DNA, and emotional valence—explaining exactly <b>why</b> each match was chosen.
            </div>
        </div>
        <div class="card-chip">Explainable AI (XAI)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div>
            <div class="card-icon">🔥</div>
            <div class="card-title">Trending & Real-Time Pulse</div>
            <div class="card-desc">
                Live weekly and daily top-performing films directly from The Movie Database (TMDB). 
                Track commercial velocity, global box office trends, and crowd favorites.
            </div>
        </div>
        <div class="card-chip">Live TMDB API Feed</div>
    </div>
    """, unsafe_allow_html=True)

# 6. "How It Works" Visual 3-Step Section
st.write("")
st.markdown("### ⚡ How CineMatch Works Under the Hood")

step_col1, step_col2, step_col3 = st.columns(3)

with step_col1:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">Step 01 • Ingestion</div>
        <div class="step-text"><b>Live TMDB Data:</b> Queries real-time metadata, cast, director, budget, revenue, and plot overviews.</div>
    </div>
    """, unsafe_allow_html=True)

with step_col2:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">Step 02 • NLP & Sentiment</div>
        <div class="step-text"><b>Text Analysis:</b> VADER sentiment models and TF-IDF vectors extract emotional tone and plot themes.</div>
    </div>
    """, unsafe_allow_html=True)

with step_col3:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">Step 03 • Recommendation</div>
        <div class="step-text"><b>Hybrid Scoring:</b> Weights cosine content similarity (60%), sentiment tone (25%), and rating quality (15%).</div>
    </div>
    """, unsafe_allow_html=True)

# 7. Sidebar Styling & TMDB Attribution
with st.sidebar:
    st.markdown("### 🎬 CineMatch")
    st.caption("AI-Powered Film Discovery")
    st.markdown("---")
    st.info("💡 **Tip:** Use the navigation links above to switch between Discover, Smart Search, Similar Movies, and Trending.")

# 8. Footer (TMDB Required Attribution)
st.markdown("""
<div class="tmdb-footer">
    <div>
        <b>Data Source:</b> Powered by <a href="https://www.themoviedb.org/" style="color:#E50914; text-decoration:none;" target="_blank">The Movie Database (TMDB)</a>.
    </div>
    <div>
        <i>This product uses the TMDB API but is not endorsed or certified by TMDB.</i>
    </div>
</div>
""", unsafe_allow_html=True)
