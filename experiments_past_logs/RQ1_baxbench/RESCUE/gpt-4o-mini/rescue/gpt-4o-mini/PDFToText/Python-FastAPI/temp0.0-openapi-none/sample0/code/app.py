from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
import subprocess

app = FastAPI()

@app.post("/convert", response_class=str)
async def convert_pdf_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    # Create a temporary file to save the uploaded PDF
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    try:
        # Write the uploaded PDF file to the temporary file
        with os.fdopen(fd, 'wb') as temp_pdf_file:
            content = await file.read()
            temp_pdf_file.write(content)

        # Create a temporary file for the output text
        fd, text_path = tempfile.mkstemp(suffix=".txt")
        try:
            # Use pdftotext to convert the PDF to text
            subprocess.run(['pdftotext', pdf_path, text_path], check=True)

            # Read the converted text
            with open(text_path, 'r', encoding='utf-8') as text_file:
                text_content = text_file.read()

            return text_content
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Conversion failed.")
        finally:
            os.remove(text_path)  # Clean up the temporary text file
    finally:
        os.remove(pdf_path)  # Clean up the temporary PDF file