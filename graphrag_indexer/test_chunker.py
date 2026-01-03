# test_chunker.py

from chunker import chunk_section

# Case 1: Raw document
doc1 = {
    "text": "This is a test document. " * 200
}

# Case 2: Structured blocks
doc2 = [
    {
        "text": "Transformer insulation failure occurs due to overheating.",
        "chapter": "Chapter 9",
        "section": "Condition Assessment",
        "subsection": "Insulation",
        "pages": [187]
    }
]

# Case 3: Mixed / missing metadata
doc3 = [
    {
        "text": "SF6 leakage can be mitigated by periodic maintenance."
    }
]

for i, doc in enumerate([doc1, doc2, doc3], start=1):
    print(f"\n=== TEST CASE {i} ===")
    chunks = chunk_section(doc)
    print(f"Chunks: {len(chunks)}")
    print(chunks[0])
