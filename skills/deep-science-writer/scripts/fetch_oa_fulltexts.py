import os
import sys
import json
import time
import requests
import argparse

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed. Please run: py -m pip install PyMuPDF requests")
    sys.exit(1)

EMAIL = "your.email@example.com" # Update with valid email

def get_oa_pdf_url(doi):
    """Query Unpaywall API to find an Open Access PDF URL for a given DOI."""
    try:
        url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('is_oa') and data.get('best_oa_location'):
                return data['best_oa_location'].get('url_for_pdf') or data['best_oa_location'].get('url')
        return None
    except Exception as e:
        print(f"[-] Error fetching Unpaywall for {doi}: {e}")
        return None

def download_pdf(url, dest):
    """Download the PDF file from the given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code == 200 and b'%PDF' in res.content[:10]:
            with open(dest, 'wb') as f:
                f.write(res.content)
            return True
        return False
    except Exception as e:
        print(f"[-] Error downloading PDF from {url}: {e}")
        return False

def extract_text(pdf_path):
    """Extract text from the downloaded PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        return f"Extraction Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Fetch Open Access PDFs via Unpaywall and extract text.")
    parser.add_argument("dois", nargs="+", help="List of DOIs to fetch.")
    parser.add_argument("--out", default="fulltexts_extracted.md", help="Output markdown file.")
    parser.add_argument("--email", default="your.email@example.com", help="Email for Unpaywall API.")
    parser.add_argument("--dir", default="fulltext", help="Folder that keeps each PDF and its extracted text.")
    args = parser.parse_args()

    global EMAIL
    EMAIL = args.email
    os.makedirs(args.dir, exist_ok=True)
    manifest = []   # rag_ingest.py reads this file as is

    with open(args.out, "w", encoding="utf-8") as out:
        out.write("# Full-Text Extraction Results\n\n")
        
        for doi in args.dois:
            print(f"[*] Processing {doi}...")
            pdf_url = get_oa_pdf_url(doi)
            if not pdf_url:
                print(f"  -> No OA PDF found.")
                out.write(f"## {doi}\nNo Open Access PDF found via Unpaywall.\n\n")
                continue
                
            print(f"  -> Found OA URL: {pdf_url}")
            stem = os.path.join(args.dir, doi.replace('/', '_'))
            pdf_path = stem + ".pdf"

            if download_pdf(pdf_url, pdf_path):
                print(f"  -> Downloaded PDF. Extracting text...")
                text = extract_text(pdf_path)
                out.write(f"## {doi}\n")
                # The whole text: Discussion and Limitations hold the gap quotes. The PDF is kept
                # for page-image QA and for checking extracted numbers against the page.
                out.write(text + "\n\n")
                with open(stem + ".txt", "w", encoding="utf-8") as t:
                    t.write(text)
                manifest.append({"doi": doi, "text_path": stem + ".txt", "pdf_path": pdf_path,
                                 "source": "Unpaywall open-access PDF via PyMuPDF",
                                 "content_check": "ok" if not text.startswith("Extraction Error") else text[:200]})
            else:
                print(f"  -> Failed to download PDF.")
                out.write(f"## {doi}\nFailed to download PDF from {pdf_url}.\n\n")
                
            time.sleep(1) # Be polite to the API

    with open(os.path.join(args.dir, "manifest.json"), "w", encoding="utf-8") as m:
        json.dump(manifest, m, ensure_ascii=False, indent=1)
    print(f"\n[+] Extraction complete. Saved to {args.out}; per-paper files and manifest.json in {args.dir}")

if __name__ == "__main__":
    main()