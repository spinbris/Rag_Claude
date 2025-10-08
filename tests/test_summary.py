"""Test script to load PDF and generate a summary."""

import os
from datetime import datetime
from ragsystem import RAGSystem

# Create outputs directory if it doesn't exist
os.makedirs('outputs', exist_ok=True)

# Initialize RAG system with ChromaDB storage in outputs folder
rag = RAGSystem(persist_directory="outputs/chroma_db")

# Load the PDF from data folder
print("Loading PDF...")
chunks_added = rag.load_pdf('data/CPG229.pdf')
print(f"Successfully loaded PDF: {chunks_added} chunks added\n")

# Ask for a very short summary
print("Generating summary...")
summary = rag.query(
    "Provide a very short summary (2-3 sentences) of what this document is about.",
    top_k=5,
    max_tokens=150
)

# Get stats
stats = rag.get_stats()

# Generate timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"outputs/summary_{timestamp}.txt"

# Save output to file
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DOCUMENT SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Source: data/CPG229.pdf\n")
    f.write(f"Chunks processed: {chunks_added}\n\n")
    f.write("--- SUMMARY ---\n")
    f.write(summary + "\n\n")
    f.write("--- STATS ---\n")
    for key, value in stats.items():
        f.write(f"{key}: {value}\n")
    f.write("=" * 80 + "\n")

# Print to console
print("\n--- SUMMARY ---")
print(summary)
print("\n--- STATS ---")
for key, value in stats.items():
    print(f"{key}: {value}")

print(f"\n✓ Output saved to: {output_file}")
