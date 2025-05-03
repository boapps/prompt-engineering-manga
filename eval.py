import json
import evaluate

def compute_metrics(predictions, references):
    """Compute multiple metrics for the translations."""
    metrics = {
        "google_bleu": evaluate.load("google_bleu"),
        "bleu": evaluate.load("bleu"),
        "meteor": evaluate.load("meteor"),
        "rouge": evaluate.load("rouge")
    }
    
    results = {}
    for name, metric in metrics.items():
        try:
            result = metric.compute(predictions=predictions, references=references)
            # Normalize scores to percentage (0-100 scale)
            if name == "google_bleu":
                results[name] = result["google_bleu"] * 100
            elif name == "bleu":
                results[name] = result["bleu"] * 100
            elif name == "meteor":
                results[name] = result["meteor"] * 100
            elif name == "rouge":
                results[name] = result["rougeL"] * 100
        except Exception as e:
            print(f"Error calculating {name}: {e}")
            results[name] = 0
    
    return results

with open("translated_books.json") as f:
    translated_books = json.load(f)

book_scores = {}
for book_title, pages in translated_books.items():
    print(f"Book Title: {book_title}")
    per_page_scores = {translator: [] for translator in pages[0].keys() if translator not in ["ja_text", "en_text", "image"]}
    for page in pages:
        predictions = {}
        ja_text = page.pop("ja_text")
        en_text = page.pop("en_text")
        image = page.pop("image")
        references = [t.lower() for t in en_text.split("\n")]
        for name, translation in page.items():
            predictions[name] = [t.lower() for t in translation.split("\n")]
            if len(predictions[name]) == len(references):
                metrics_results = compute_metrics(predictions=predictions[name], references=references)
                per_page_scores[name].append({"metrics": metrics_results, "image": image})
            else:
                print(f"Length mismatch for {name} on page {image}. Skipping metrics calculation.")
                per_page_scores[name].append({"metrics": {metric: 0 for metric in ["google_bleu", "bleu", "meteor", "rouge"]}, "image": image})

    for name, pagescores in per_page_scores.items():
        # Calculate average scores for each metric
        metrics_sums = {}
        for page in pagescores:
            for metric, score in page["metrics"].items():
                metrics_sums[metric] = metrics_sums.get(metric, 0) + score
                
        avg_metrics = {metric: sum_score/len(pagescores) for metric, sum_score in metrics_sums.items()}
        
        # Print results for this translator
        print(f"{name}:", end=" ")
        metric_strings = [f"{metric}: {score:.2f}" for metric, score in avg_metrics.items()]
        print(", ".join(metric_strings))
        
        # Store in book_scores
        book_scores[book_title] = book_scores.get(book_title, {})
        book_scores[book_title][name] = avg_metrics

    print("===")
    print()

print(json.dumps(book_scores, indent=4, ensure_ascii=False))

# Calculate averages across all books
average_scores = {}
for book_title in book_scores:
    for name in book_scores[book_title]:
        if name not in average_scores:
            average_scores[name] = {metric: 0 for metric in book_scores[book_title][name]}
        
        for metric, score in book_scores[book_title][name].items():
            average_scores[name][metric] = average_scores[name].get(metric, 0) + score

# Divide by number of books
for name in average_scores:
    for metric in average_scores[name]:
        average_scores[name][metric] /= len(book_scores)

print("Average scores across all books:")
print(json.dumps(average_scores, indent=4, ensure_ascii=False))
