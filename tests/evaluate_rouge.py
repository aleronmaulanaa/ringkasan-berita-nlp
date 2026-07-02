import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rouge_score import rouge_scorer
from src.summarizer import summarize_text


def evaluate(articles_path: str = "data/sample_articles.json"):
    with open(articles_path, encoding="utf-8") as f:
        articles = json.load(f)

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    all_scores = {"rouge1": [], "rouge2": [], "rougeL": []}

    for article in articles:
        result = summarize_text(article["text"], lang=article.get("lang"))
        scores = scorer.score(article["reference_summary"], result["summary"])
        print(f"\n--- {article['title']} ---")
        for metric, score in scores.items():
            print(f"  {metric}: P={score.precision:.4f} R={score.recall:.4f} F={score.fmeasure:.4f}")
            all_scores[metric].append(score)

    if len(articles) > 1:
        print(f"\n{'='*60}")
        print(f"RATA-RATA ({len(articles)} artikel)")
        print(f"{'='*60}")
        for metric, scores_list in all_scores.items():
            avg_p = sum(s.precision for s in scores_list) / len(scores_list)
            avg_r = sum(s.recall for s in scores_list) / len(scores_list)
            avg_f = sum(s.fmeasure for s in scores_list) / len(scores_list)
            print(f"  {metric}: P={avg_p:.4f} R={avg_r:.4f} F={avg_f:.4f}")


if __name__ == "__main__":
    evaluate()
