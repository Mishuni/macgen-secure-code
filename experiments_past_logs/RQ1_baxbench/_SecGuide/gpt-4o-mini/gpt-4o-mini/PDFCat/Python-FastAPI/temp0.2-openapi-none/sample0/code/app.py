from fastapi import FastAPI, UploadFile, File, HTTPException
import subprocess
import os
from tempfile import NamedTemporaryFile
import mimetypes

app = FastAPI()

def is_valid_pdf(file_path: str) -> bool:
    """Check if the file is a valid PDF by inspecting its magic number."""
    with open(file_path, 'rb') as f:
        header = f.read(4)
    return header == b'%PDF'

@app.post("/concatenate", response_class=bytes)
async def concatenate_pdfs(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    # Create temporary files to store uploaded PDFs
    temp_files = []
    try:
        for file in files:
            # Validate file type
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
            
            # Create a temporary file for the uploaded PDF
            with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()  # Ensure the file is written to disk
                temp_file_name = temp_file.name
                
                # Validate the PDF file
                if not is_valid_pdf(temp_file_name):
                    raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")
                
                temp_files.append(temp_file_name)

        # Create a temporary file for the concatenated PDF
        with NamedTemporaryFile(delete=True, suffix=".pdf") as output_file:
            # Use pdfunite to concatenate the PDFs
            command = ["pdfunite"] + temp_files + [output_file.name]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                raise HTTPException(status_code=500, detail="An error occurred while processing the files.")

            # Read the concatenated PDF and return it
            output_file.seek(0)
            concatenated_pdf = output_file.read()

        return concatenated_pdf

    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal error occurred.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)