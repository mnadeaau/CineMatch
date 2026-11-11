"""
tmdb_client.py  --  SECTION 1: API INTERACTION, DATA RETRIEVAL AND DATA PROCESSING
All communication with the TMDB API lives in this one file, so the rest of the app never
needs to know how the API works. If TMDB ever changes, only this file needs fixing.

Key decisions:
  * Caching (lru_cache): the same request is only sent once. This avoids TMDB rate limits
    and makes repeat searches instant.
  * Parallel fetching (ThreadPoolExecutor): details for ~20 movies load at the same time
    instead of one by one.
  * Friendly errors (TMDBError): any API problem becomes a plain-English message for the user.
"""
import os
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w342"


class TMDBError(Exception):
    """A problem talking to TMDB. The message is safe to show to the user."""


def _key():
    # SECURITY: the API key is never written in the code. On Streamlit Cloud it is stored in
    # "Secrets"; locally it can be an environment variable. This keeps the key out of GitHub.
    try:
        return st.secrets["TMDB_API_KEY"]
    except Exception:
        return os.environ.get("TMDB_API_KEY", "")


@lru_cache(maxsize=4096)   # CACHE: the same question is only ever sent to TMDB once
def _get(path, params=()):
    key = _key()
    if not key:
        raise TMDBError("No TMDB API key found. Add TMDB_API_KEY to the app's Secrets.")
    query = dict(params)
    query["api_key"] = key
    last_error = None
    # RELIABILITY: retry up to 3 times so a brief network hiccup does not crash the app
    for attempt in range(3):               # try up to 3 times if TMDB is busy
        try:
            r = requests.get(f"{BASE}{path}", params=query, timeout=10)
            if r.status_code == 401:
                raise TMDBError("TMDB rejected the API key. Use the short 'API Key', not the long token.")
            if r.status_code == 429:       # "too many requests" -> wait, then retry
                time.sleep(1 + attempt)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_error = e
            time.sleep(0.5)
    raise TMDBError(f"Could not reach TMDB right now ({last_error}). Please try again.")


# Helper: converts a normal dictionary of parameters into a sorted tuple. Dictionaries cannot be
# cached, but tuples can, so this is what makes the caching above work.
def _call(path, **params):
    # Turns {"a": 1} into a hashable form so the cache can remember it
    return _get(path, tuple(sorted((k, str(v)) for k, v in params.items())))


def genre_map():
    """{35: 'Comedy', 27: 'Horror', ...}"""
    return {g["id"]: g["name"] for g in _call("/genre/movie/list", language="en-US")["genres"]}


# Personnel filter support: TMDB filters by person ID, not name, so we look the ID up first.
# For directors we prefer people TMDB lists as "Directing" to avoid matching an actor with the same name.
def search_person(name, directing=False):
    """Find a person's ID. Returns (id, name) or None if nobody matches."""
    results = _call("/search/person", query=name).get("results", [])
    if directing:   # prefer people known for directing
        results = [p for p in results if p.get("known_for_department") == "Directing"] or results
    return (results[0]["id"], results[0]["name"]) if results else None


def search_movies(query, limit=8):
    results = _call("/search/movie", query=query, include_adult="false").get("results", [])
    return [{"id": m["id"], "title": m["title"], "year": (m.get("release_date") or "")[:4]}
            for m in results[:limit]]


def trending(window="week"):
    return [m["id"] for m in _call(f"/trending/movie/{window}").get("results", [])]


# Candidate pool for recommendations: instead of ranking every movie on TMDB (impossible),
# we only rank movies TMDB already considers related. This keeps results relevant and fast.
def related_ids(movie_id):
    """Movies TMDB itself thinks are related. We use these as candidates to rank."""
    ids = []
    for kind in ("recommendations", "similar"):
        ids += [m["id"] for m in _call(f"/movie/{movie_id}/{kind}").get("results", [])]
    return list(dict.fromkeys(ids))   # remove duplicates, keep order


def discover(filters, pages=1):
    """Filtered search. `filters` uses TMDB's own parameter names (same as in Colab)."""
    # Defaults: hide adult titles, and require at least 100 votes so obscure movies with a
    # handful of ratings do not dominate the results. Any filter passed in overrides these.
    params = {"include_adult": "false", "language": "en-US",
              "sort_by": "popularity.desc", "vote_count.gte": 100}
    params.update(filters)
    movies, total = [], 0
    for page in range(1, pages + 1):
        data = _call("/discover/movie", page=page, **params)
        movies += data.get("results", [])
        total = data.get("total_results", 0)
    return movies, total


# DATA PROCESSING: TMDB returns a large, deeply nested reply. This function flattens it into one
# tidy dictionary per movie containing only the fields the app uses (basic info, content details,
# performance metrics). Missing values are replaced with safe defaults so the app never crashes.
def _clean(d):
    """Turn TMDB's big messy reply into one tidy dictionary (your clean_movie from Step 3)."""
    # Certification (age rating) is stored per country. We use the US rating; "NR" = not rated.
    cert = "NR"
    for country in d.get("release_dates", {}).get("results", []):
        if country["iso_3166_1"] == "US":
            for r in country["release_dates"]:
                if r.get("certification"):
                    cert = r["certification"]
                    break
    credits = d.get("credits", {})
    return {
        "id": d["id"],
        "title": d.get("title", ""),
        "year": (d.get("release_date") or "")[:4],
        "runtime": d.get("runtime") or 0,
        "certification": cert,
        "genres": [g["name"] for g in d.get("genres", [])],
        "overview": d.get("overview") or "",
        "tagline": d.get("tagline") or "",
        "keywords": [k["name"] for k in d.get("keywords", {}).get("keywords", [])],
        "cast": [p["name"] for p in credits.get("cast", [])[:8]],
        "director": [p["name"] for p in credits.get("crew", []) if p.get("job") == "Director"],
        "rating": d.get("vote_average") or 0.0,
        "votes": d.get("vote_count") or 0,
        "box_office": d.get("revenue") or 0,
        "budget": d.get("budget") or 0,
        "language": d.get("original_language", ""),
        "poster": f"{IMG}{d['poster_path']}" if d.get("poster_path") else None,
    }


# One request returns everything: append_to_response bundles cast/crew, keywords and release
# dates into the same reply, instead of making three separate requests per movie.
def get_movie(movie_id):
    return _clean(_call(f"/movie/{movie_id}", language="en-US",
                        append_to_response="credits,keywords,release_dates"))


def get_movies(ids):
    """Get full details for many movies at once (8 at a time, so it's fast)."""
    def safe(i):
        try:
            return get_movie(i)
        except TMDBError:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        return [m for m in pool.map(safe, ids) if m]
