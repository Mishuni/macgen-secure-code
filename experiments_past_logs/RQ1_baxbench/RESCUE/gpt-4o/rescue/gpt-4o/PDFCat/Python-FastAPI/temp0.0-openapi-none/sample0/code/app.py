from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import subprocess
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="PDF Concatenation Service",
    description="A service that concatenates multiple PDF files into a single PDF.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store temporary files
TEMP_DIR = "/tmp/pdf_concat_service"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/concatenate", summary="Concatenate multiple PDF files", description="Accepts multiple PDF files and returns a single concatenated PDF.")
async def concatenate_pdfs(files: List[UploadFile] = File(...)):
    # Validate input
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="At least two PDF files are required for concatenation.")

    temp_files = []
    try:
        # Save uploaded files to temporary directory
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Only PDF files are allowed.")
            
            # Generate a secure temporary file path
            temp_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.pdf")
            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)
            temp_files.append(temp_file_path)

        # Generate a secure output file path
        output_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_concatenated.pdf")

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(
                ["pdfunite", *temp_files, output_file_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail="An error occurred while concatenating the PDF files.")

        # Return the concatenated PDF file
        return FileResponse(
            path=output_file_path,
            media_type="application/pdf",
            filename="concatenated.pdf"
        )
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)