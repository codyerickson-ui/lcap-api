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

    if not pdf_url:
        raise HTTPException(status_code=400, detail="Missing pdf_url")

    try:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

    pdf_file = io.BytesIO(response.content)

    full_text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    return {
        "success": True,
        "text_length": len(full_text),
        "text": full_text
    }
