import json
import matplotlib.pyplot as plt
import numpy as np

# Load the metrics data
with open('metrics.json') as f:
    metrics = json.load(f)

# Define metrics to visualize
metric_names = ['google_bleu', 'bleu', 'meteor', 'rouge']
metric_titles = ['Google BLEU', 'BLEU', 'METEOR', 'ROUGE-L']

# Extract translators and sort by google_bleu score (descending)
translators = list(metrics.keys())
translators.sort(key=lambda x: metrics[x]['google_bleu'], reverse=True)

# Set up the figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
axs = axs.flatten()

# Color map
colors = plt.cm.viridis(np.linspace(0, 0.8, len(translators)))

# Create bar charts for each metric
for i, (metric, title) in enumerate(zip(metric_names, metric_titles)):
    values = [metrics[translator][metric] for translator in translators]
    
    # Create the bar chart
    bars = axs[i].bar(range(len(translators)), values, color=colors)
    
    # Add labels and styling
    axs[i].set_title(title, fontsize=14)
    axs[i].set_ylabel('Score', fontsize=12)
    axs[i].set_xticks(range(len(translators)))
    axs[i].set_xticklabels(translators, rotation=45, ha='right', fontsize=10)
    axs[i].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axs[i].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.2f}', ha='center', fontsize=9)

# Add a common title
fig.suptitle('Translation Metrics Comparison Across Models', fontsize=16)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9)

# Save the figure
plt.savefig('translation_metrics_comparison.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 'translation_metrics_comparison.png'")

# Show the figure
plt.show()

# Create a single chart with all metrics together for easy comparison
plt.figure(figsize=(14, 8))

bar_width = 0.2
index = np.arange(len(translators))

for i, (metric, title) in enumerate(zip(metric_names, metric_titles)):
    values = [metrics[translator][metric] for translator in translators]
    plt.bar(index + i * bar_width, values, bar_width, label=title, alpha=0.8, color=plt.cm.viridis(i/4))

plt.xlabel('Translator', fontsize=12)
plt.ylabel('Score', fontsize=12)
plt.title('All Metrics Comparison', fontsize=16)
plt.xticks(index + bar_width * 1.5, translators, rotation=45, ha='right')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('all_metrics_comparison.png', dpi=300, bbox_inches='tight')
print("Combined visualization saved as 'all_metrics_comparison.png'")

plt.show()