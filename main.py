from fastapi import FastAPI, HTTPException
import requests
import io
import pdfplumber

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "LCAP Retrieval API Running"}

@app.post("/retrieve-lcap")
def retrieve_lcap(data: dict):
    pdf_url = data.get("pdf_url")
    start_page = data.get("start_page", 0)
    end_page = data.get("end_page", None)

    if not pdf_url:
        raise HTTPException(status_code=400, detail="Missing pdf_url")

    try:
        response = requests.get(pdf_url, timeout=120)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

    pdf_file = io.BytesIO(response.content)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)

            if end_page is None or end_page > total_pages:
                end_page = total_pages

            if start_page < 0 or start_page >= total_pages:
                raise HTTPException(status_code=400, detail="Invalid start_page")

            full_text = ""

            for page_number in range(start_page, end_page):
                text = pdf.pages[page_number].extract_text()
                if text:
                    full_text += f"\n--- Page {page_number + 1} ---\n"
                    full_text += text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    return {
        "success": True,
        "total_pages": total_pages,
        "start_page": start_page,
        "end_page": end_page,
        "text_length": len(full_text),
        "text": full_text
    }
