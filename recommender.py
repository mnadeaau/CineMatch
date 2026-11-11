"""
recommender.py  --  SECTION 3: RECOMMENDATION ALGORITHMS
This file implements three approaches (the assignment requires at least two):
  A. Content-based filtering  (the "content" score)
  B. Sentiment-based matching (the "mood" score)
  C. Hybrid                   (the weighted "score" that blends A, B and quality)

Ranks movies using three ingredients.
   content  = how alike the plot/genres/themes/people are   (TF-IDF + cosine similarity)
   mood     = how close the plot tone is                     (VADER sentiment)
   quality  = weighted audience rating                       (stops 3-vote movies winning)
   score    = a weighted blend of the three (the "hybrid")
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_utils import build_soup, sentiment_score


# EXPLAINABILITY: builds the "Why this?" text by listing what the recommendation shares with the
# movie the user picked. This is the "similarity explanation" enhanced feature.
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
    # Dividing by the total weight keeps the final score between 0 and 1 even if the user
    # moves the sliders so the weights no longer add up to 1. "or 1" avoids dividing by zero.
    total = (w_content + w_mood + w_quality) or 1

    # APPROACH A, content-based: seed movie is row 0, candidates follow. TF-IDF gives rare, meaningful
    # words (e.g. "heist") a high value and everyday words a low value. Cosine similarity then measures
    # how alike the seed is to each candidate (0 = nothing alike, 1 = identical).
    soups = [build_soup(m) for m in [seed] + candidates]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(soups)
    content = cosine_similarity(matrix[0], matrix[1:]).ravel()

    # APPROACH B, sentiment-based: mood = 1 minus the gap between the two plot sentiments (scaled
    # because the biggest possible gap is 2). Same tone gives ~1, opposite tone gives ~0.
    #
    # QUALITY: the weighted rating (same idea as the IMDb Top 250). A movie with few votes is pulled
    # towards the average, so 3 votes at 10/10 cannot beat a classic with 20,000 votes at 8.4.
    # APPROACH C, hybrid: final score = weighted blend. Defaults of 0.6 / 0.2 / 0.2 were chosen
    # because content is the strongest signal of taste, while mood is noisy (see nlp_utils.py).
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
