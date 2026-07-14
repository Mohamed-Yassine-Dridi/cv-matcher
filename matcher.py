import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scraper import stream_opportunities

model = None

def get_model():
    global model
    if model is None:
        print("Loading AI model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def stream_match(cv_text, region="any", duration="any"):
    ai_model = get_model()

    if not cv_text.strip():
        yield f"data: {json.dumps([])}\n\n"
        yield "data: [DONE]\n\n"
        return

    cv_embedding = ai_model.encode([cv_text])[0]
    all_matches = []

    for opp_chunk in stream_opportunities(
        max_pages=10,
        region_choice=region,
        duration_choice=duration
    ):
        if not opp_chunk:
            continue

        texts = [o["text"] for o in opp_chunk]
        opp_embeddings = ai_model.encode(texts)

        scores = cosine_similarity([cv_embedding], opp_embeddings)[0]

        for i, score in enumerate(scores):
            match_score = round(float(score) * 100, 2)

            if match_score > 30:
                all_matches.append({
                    "title": opp_chunk[i]["title"],
                    "url": opp_chunk[i]["url"],
                    "score": match_score
                })

        all_matches.sort(key=lambda x: x["score"], reverse=True)

        yield f"data: {json.dumps(all_matches[:40])}\n\n"

    yield "data: [DONE]\n\n"