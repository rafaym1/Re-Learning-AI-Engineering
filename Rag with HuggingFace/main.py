from rag.pipeline import RagPipeline


def main():
    pipeline = RagPipeline()
    pipeline.index("data/sample.txt")

    questions = [
        "How do black holes form?",
        "What causes rain?",
    ]
    for question in questions:
        answer = pipeline.query(question, top_k=2)
        print(f"Q: {question}\nA: {answer}\n")


if __name__ == "__main__":
    main()
