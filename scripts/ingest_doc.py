import argparse
import os
import re
import sys
import tempfile
import urllib.request

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.skills.ingestion.pipeline import ingest_pdf_document


def download_arxiv_pdf(url: str) -> str:
    """Download an arXiv PDF from an abs or pdf URL to a temporary file."""
    # Convert abs URL to pdf URL if needed
    match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", url)
    if match:
        arxiv_id = match.group(1)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    else:
        pdf_url = url

    print(f"Downloading arXiv paper from: {pdf_url} ...")
    temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    req = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PersonalDeepAgent/1.0"},
    )
    with urllib.request.urlopen(req) as response, open(temp_path, "wb") as out_f:
        out_f.write(response.read())

    print(f"Saved temporary PDF to: {temp_path}")
    return temp_path


def main():
    parser = argparse.ArgumentParser(description="Ingest a PDF research paper into Personal DeepAgent")
    parser.add_argument("source", help="Local PDF file path or arXiv URL (e.g. https://arxiv.org/abs/2403.12345)")
    parser.add_argument("--threshold", type=float, default=0.8, help="Evaluation recall pass threshold (default: 0.8)")
    args = parser.parse_args()

    source = args.source.strip()
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        pdf_path = download_arxiv_pdf(source)
        canonical_url = source
        cleanup = True
    else:
        pdf_path = os.path.abspath(source)
        canonical_url = None
        cleanup = False

    try:
        print(f"\n==================================================")
        print(f"  AUTONOMOUS DOCUMENT INGESTION")
        print(f"==================================================")
        print(f"Source: {source}")
        print(f"Pass Threshold: {args.threshold * 100:.0f}%\n")

        report = ingest_pdf_document(pdf_path, source_url=canonical_url, threshold=args.threshold)

        print(f"--------------------------------------------------")
        print(f"Ingestion Status : {report.status}")
        print(f"Document Slug    : {report.document_metadata.document_name}")
        print(f"Title            : {report.document_metadata.title}")
        print(f"Author(s)        : {report.document_metadata.author}")
        print(f"Year             : {report.document_metadata.year}")
        print(f"Total Chunks     : {report.total_chunks}")
        print(f"Recall Score     : {report.final_recall_score * 100:.1f}%")
        print(f"Iterations Used  : {report.iterations_used}")
        if report.quarantine_reason:
            print(f"Quarantine Reason: {report.quarantine_reason}")
        print(f"--------------------------------------------------")

        if report.status == "SUCCESS":
            print("\nDocument successfully verified and added to knowledge base and catalog.csv!")
            sys.exit(0)
        else:
            print(f"\nDocument was quarantined ({report.status}). Check logs for details.")
            sys.exit(1)

    finally:
        if cleanup and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass


if __name__ == "__main__":
    main()

