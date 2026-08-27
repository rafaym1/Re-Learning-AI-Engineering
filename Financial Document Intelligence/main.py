from fdi.ingestion import ingest_vdr


def main():
    documents, skipped = ingest_vdr("data/dev_vdr")

    print(f"Ingested {len(documents)} documents:")
    for doc in documents:
        print(f"  [{doc.category}] {doc.source_path} — {len(doc.text)} chars, {len(doc.tables)} tables")

    if skipped:
        print(f"\nSkipped {len(skipped)} unsupported files:")
        for path in skipped:
            print(f"  {path}")


if __name__ == "__main__":
    main()
