"""Small document catalog shared by the SQL and graph examples."""

DOCUMENTS: list[tuple[int, str, str, int]] = [
    (1, "Python fundamentals", "python", 28),
    (2, "Text embeddings", "retrieval", 12),
    (3, "MCP tools", "integration", 8),
    (4, "Graph search", "retrieval", 16),
    (5, "NumPy arrays", "data", 20),
    (6, "Pandas tables", "data", 24),
]

AUTHORS: dict[int, str] = {
    1: "Alex", 2: "Sam", 3: "Alex", 4: "Sam", 5: "Lee", 6: "Lee",
}
