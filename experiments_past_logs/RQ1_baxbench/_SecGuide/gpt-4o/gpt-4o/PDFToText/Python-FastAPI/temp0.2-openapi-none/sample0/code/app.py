from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import subprocess
import os
import tempfile
import shutil
import magic
import logging

app = FastAPI(
    title="PDF to Text Converter API",
    description="A simple API to convert PDF files to Text format.",
    version="1.0.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_pdf(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return file_type == 'application/pdf'

@app.post("/convert", response_class=PlainTextResponse, responses={
    200: {"description": "Successfully converted PDF to text"},
    400: {"description": "Bad Request - Invalid input or missing file"},
    500: {"description": "Internal Server Error - Conversion failed"}
})
async def convert_pdf_to_text(file: UploadFile = File(...)):
    try:
        # Read the file content to check the size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds the limit of 10 MB.")

        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            temp_pdf_file.write(file_content)
            temp_pdf_path = temp_pdf_file.name

        # Validate the PDF file
        if not is_valid_pdf(temp_pdf_path):
            os.remove(temp_pdf_path)
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")

        # Create a temporary file for the text output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_txt_file:
            temp_txt_path = temp_txt_file.name

        # Convert PDF to text
        subprocess.run(["pdftotext", temp_pdf_path, temp_txt_path], check=True)

        # Read the text content
        with open(temp_txt_path, "r") as temp_txt_file:
            text_content = temp_txt_file.read()

        return text_content

    except subprocess.CalledProcessError:
        logger.error("Conversion failed due to a subprocess error.")
        raise HTTPException(status_code=500, detail="Conversion failed")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Ensure temporary files are removed
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)