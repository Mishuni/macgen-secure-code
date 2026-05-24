from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import os
import subprocess
import tempfile

app = FastAPI(
    title="PDF to Text Converter API",
    description="A simple API to convert PDF files to Text format.",
    version="1.0.0"
)

@app.post("/convert", response_class=PlainTextResponse)
async def convert_pdf_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name
        
        temp_txt_path = temp_pdf_path.replace('.pdf', '.txt')
        
        try:
            subprocess.run(["pdftotext", temp_pdf_path, temp_txt_path], check=True, shell=False)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Failed to convert PDF to text.")
        
        with open(temp_txt_path, 'r') as txt_file:
            text_content = txt_file.read()
        
        return text_content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during file processing.")
    
    finally:
        try:
            os.remove(temp_pdf_path)
            os.remove(temp_txt_path)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)