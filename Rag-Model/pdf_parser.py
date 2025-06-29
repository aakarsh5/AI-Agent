# Add to pdf_parser.py

def parse_pdf_and_return_docs(pdf_path: str) -> List[Document]:
    import fitz
    total_pages = len(fitz.open(pdf_path))

    result = compiled.invoke({
        "question": "",  # Placeholder, we don't use it here
        "query_type": "visual",
        "query": {},
        "answer": None,
        "pdf_path": pdf_path,
        "current_page": 1,
        "total_pages": total_pages,
        "page_docs": [],
        "docs": [],
        "page_image": None
    })
    return result["docs"]
