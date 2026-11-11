"""
recommender.py  --  the "brain": ranks movies using three ingredients.
   content  = how alike the plot/genres/themes/people are   (TF-IDF + cosine similarity)
   mood     = how close the plot tone is                     (VADER sentiment)
   quality  = weighted audience rating                       (stops 3-vote movies winning)
   score    = a weighted blend of the three (the "hybrid")
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_utils import build_soup, sentiment_score


def explain(seed, cand, mood):
    """Plain-English reasons why `cand` is like `seed`."""
    reasons = []
    genres = set(seed["genres"]) & set(cand["genres"])
    if genres: reasons.append("shared genres: " + ", ".join(sorted(genres)))
    themes = set(seed["keywords"]) & set(cand["keywords"])
    if themes: reasons.append("shared themes: " + ", ".join(sorted(themes)[:4]))
    directors = set(seed["director"]) & set(cand["director"])
    if directors: reasons.append("same director: " + ", ".join(directors))
    cast = set(seed["cast"]) & set(cand["cast"])
    if cast: reasons.append("shared cast: " + ", ".join(sorted(cast)[:3]))
    if mood > 0.9: reasons.append("very similar plot tone")
    reasons.append(f"rated {cand['rating']:.1f}/10 by {cand['votes']:,} people")
    return "; ".join(reasons)


def rank_similar(seed, candidates, w_content=0.6, w_mood=0.2, w_quality=0.2):
    """Return the candidates as a list, best match first, each with its scores and a 'why'."""
    candidates = [c for c in candidates if c["id"] != seed["id"]]
    if not candidates:
        return []
    total = (w_content + w_mood + w_quality) or 1     # so the score always stays between 0 and 1

    # 1) content similarity
    soups = [build_soup(m) for m in [seed] + candidates]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(soups)
    content = cosine_similarity(matrix[0], matrix[1:]).ravel()

    # 2) mood + 3) quality, then the blend
    seed_mood = sentiment_score(seed["overview"])
    average = np.mean([c["rating"] for c in candidates])
    cutoff = max(np.median([c["votes"] for c in candidates]), 1)

    ranked = []
    for c, content_score in zip(candidates, content):
        mood = 1 - abs(sentiment_score(c["overview"]) - seed_mood) / 2
        v, R = c["votes"], c["rating"]
        quality = ((v / (v + cutoff)) * R + (cutoff / (v + cutoff)) * average) / 10
        score = (w_content * content_score + w_mood * mood + w_quality * quality) / total
        item = dict(c)
        item.update(score=score, content=content_score, mood=mood, quality=quality,
                    why=explain(seed, c, mood))
        ranked.append(item)
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
