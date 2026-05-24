from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import subprocess
import os
import uuid

app = FastAPI(
    title="PDF to Text Converter API",
    description="A simple API to convert PDF files to Text format.",
    version="1.0.0"
)

@app.post("/convert", response_class=PlainTextResponse, responses={
    200: {"description": "Successfully converted PDF to text"},
    400: {"description": "Bad Request - Invalid input or missing file"},
    500: {"description": "Internal Server Error - Conversion failed"}
})
async def convert_pdf_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    try:
        # Generate a unique identifier for the temporary file
        unique_id = uuid.uuid4().hex
        temp_pdf_path = f"/tmp/{unique_id}.pdf"
        temp_txt_path = f"/tmp/{unique_id}.txt"

        # Save the uploaded file to a temporary location
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            while content := await file.read(1024 * 1024):  # Read in chunks to handle large files
                temp_pdf_file.write(content)

        # Use pdftotext to convert the PDF to text
        subprocess.run(["pdftotext", temp_pdf_path, temp_txt_path], check=True)

        # Read the converted text
        with open(temp_txt_path, "r") as temp_txt_file:
            text_content = temp_txt_file.read()

        # Clean up temporary files
        os.remove(temp_pdf_path)
        os.remove(temp_txt_path)

        return text_content

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Conversion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)