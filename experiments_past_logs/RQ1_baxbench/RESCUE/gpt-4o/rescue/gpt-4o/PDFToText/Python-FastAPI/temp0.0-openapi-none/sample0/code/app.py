import os
import tempfile
import subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI(
    title="PDF to Text Converter API",
    description="A simple API to convert PDF files to Text format.",
    version="1.0.0",
)

@app.post("/convert", response_class=PlainTextResponse, summary="Convert a PDF file to Text", description="Upload a PDF file to convert it into Text format.")
async def convert_pdf_to_text(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    # Create a secure temporary file to store the uploaded PDF
    try:
        fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        try:
            # Write the uploaded file content to the temporary file
            with os.fdopen(fd, "wb") as temp_pdf_file:
                temp_pdf_file.write(await file.read())

            # Create another secure temporary file for the output text
            fd_out, temp_txt_path = tempfile.mkstemp(suffix=".txt")
            os.close(fd_out)  # Close the file descriptor as we only need the path

            try:
                # Use the `pdftotext` utility to extract text from the PDF
                result = subprocess.run(
                    ["pdftotext", temp_pdf_path, temp_txt_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Read the extracted text from the temporary text file
                with open(temp_txt_path, "r", encoding="utf-8") as temp_txt_file:
                    extracted_text = temp_txt_file.read()

                return extracted_text

            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail="Failed to convert PDF to text.") from e

            finally:
                # Ensure the temporary text file is securely deleted
                if os.path.exists(temp_txt_path):
                    os.remove(temp_txt_path)

        finally:
            # Ensure the temporary PDF file is securely deleted
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from e

# Run the application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)