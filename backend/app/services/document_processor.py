import pymupdf


def extract_text_from_pdf(file_path: str) -> list[dict]:
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text("text").strip()

        if text:
            pages.append(
                {
                    "page_number": page_number + 1,
                    "text": text,
                }
            )

    document.close()

    return pages


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        start = 0
        chunk_order = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "page_number": page_number,
                        "chunk_order": chunk_order,
                        "start_offset": start,
                        "end_offset": end,
                        "text": chunk_text,
                    }
                )

                chunk_order += 1

            if end >= len(text):
                break

            start = end - overlap

    return chunks