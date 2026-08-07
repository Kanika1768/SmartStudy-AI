import os
import pymupdf


def load_pdf(pdf_path, document_name=None):
    """
    Load a PDF page by page.

    Args:
        pdf_path (str):
            Path to the PDF file.

        document_name (str, optional):
            Original uploaded filename.
            If not provided, the filename is extracted from pdf_path.

    Returns:
        list[dict]

        Example:
        [
            {
                "text": "...",
                "page": 1,
                "document": "Operating Systems.pdf"
            }
        ]
    """

    document = pymupdf.open(pdf_path)

    # Preserve original uploaded filename if available
    if document_name:
        filename = document_name
    else:
        filename = os.path.basename(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        # Skip empty pages
        if not text:
            continue

        pages.append(
            {
                "text": text,
                "page": page_number,
                "document": filename
            }
        )

    document.close()

    return pages