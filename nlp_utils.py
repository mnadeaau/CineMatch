"""
nlp_utils.py  --  the "language" file: mood from plots, text for similarity, plain-English search.
"""
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def sentiment_score(text):
    """-1 = very negative plot, +1 = very positive plot."""
    return _analyzer.polarity_scores(text)["compound"] if text else 0.0


def _token(prefix, name):
    # "Christopher Nolan" -> "dir_christophernolan" so the whole name counts as ONE word
    return prefix + re.sub(r"[^a-z0-9]", "", name.lower())


def build_soup(m):
    """Glue everything we know about a movie into one text. Genres, themes and directors are
    repeated so they count for more than ordinary plot words."""
    parts = [m["overview"], m["tagline"]]
    parts += [_token("genre_", g) for g in m["genres"]] * 2
    parts += [k.replace(" ", "_") for k in m["keywords"]] * 2
    parts += [_token("dir_", d) for d in m["director"]] * 2
    parts += [_token("cast_", c) for c in m["cast"][:5]]
    return " ".join(p for p in parts if p)


# word -> (TMDB genre id, nice name)
GENRES = {"comedy": (35, "Comedy"), "funny": (35, "Comedy"), "horror": (27, "Horror"),
          "action": (28, "Action"), "drama": (18, "Drama"), "romance": (10749, "Romance"),
          "romantic": (10749, "Romance"), "sci-fi": (878, "Sci-Fi"), "thriller": (53, "Thriller"),
          "animation": (16, "Animation"), "animated": (16, "Animation"), "family": (10751, "Family")}


def parse_query(text):
    """Turn a sentence into TMDB filters. Returns (filters, list_of_things_we_understood)."""
    t = text.lower()
    f, understood = {}, []

    # Rule 1: decades such as "90s" or "1990s"
    m = re.search(r"\b(19|20)?(\d0)s\b", t)
    if m:
        n = int(m.group(2))
        year = 1900 + n if n >= 30 else 2000 + n
        f["primary_release_date.gte"] = f"{year}-01-01"
        f["primary_release_date.lte"] = f"{year + 9}-12-31"
        understood.append(f"{year}s")

    # Rule 2: "under 2 hours" / "under 90 minutes"
    m = re.search(r"under (\d+(?:\.\d+)?) ?(hours?|hrs?|minutes?|mins?)", t)
    if m:
        amount = float(m.group(1))
        minutes = int(amount * 60) if m.group(2).startswith("h") else int(amount)
        f["with_runtime.lte"] = minutes
        understood.append(f"under {minutes} minutes")

    # Rule 3: "rated 7" / "rating above 7.5"
    m = re.search(r"(?:rated|rating) (?:above |over |at least )?(\d(?:\.\d)?)", t)
    if m:
        f["vote_average.gte"] = float(m.group(1))
        understood.append(f"rating at least {m.group(1)}")

    # Rule 4: genres, including "not horror"
    excluded_words = re.findall(r"(?:not|no|without) ([a-z-]+)", t)
    include, exclude = {}, {}
    for word, (gid, name) in GENRES.items():
        if word in t:
            (exclude if word in excluded_words else include)[gid] = name
    if include:
        f["with_genres"] = ",".join(str(g) for g in include)
        understood.append("genres: " + ", ".join(include.values()))
    if exclude:
        f["without_genres"] = ",".join(str(g) for g in exclude)
        understood.append("not: " + ", ".join(exclude.values()))

    # Rule 5: family friendly means PG or lower
    if "family" in t or "kids" in t:
        f["certification_country"] = "US"
        f["certification.lte"] = "PG"
        understood.append("PG or lower")

    return f, understood
