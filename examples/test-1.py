
import ragsystem

rag = ragsystem 
# Walks data/ and loads supported files. For a summary use verbose=True:
summary = rag.load_file('data/', verbose=True)
print(f"Added {summary['added_chunks']} chunks from data/")
if summary['skipped_files']:
	print("Skipped files:", summary['skipped_files'])

# Save index
rag.save('rag_index.pkl')