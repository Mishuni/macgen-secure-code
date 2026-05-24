import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import subprocess
import uvicorn

app = FastAPI(
    title="PDF Concatenation Service",
    description="A service that concatenates multiple PDF files into a single PDF.",
    version="1.0.0"
)

class ErrorResponse(BaseModel):
    error: str

@app.post("/concatenate", response_class=FileResponse, responses={
    200: {
        "description": "Successfully concatenated the PDF files.",
        "content": {"application/pdf": {}}
    },
    400: {
        "description": "Bad Request - Invalid input or missing files.",
        "model": ErrorResponse
    },
    500: {
        "description": "Internal Server Error - An error occurred while processing the files.",
        "model": ErrorResponse
    }
})
async def concatenate_pdfs(files: List[UploadFile] = File(...)):
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_paths = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="All files must be PDFs.")
            
            # Sanitize the filename
            filename = os.path.basename(file.filename)
            if '..' in filename:
                raise HTTPException(status_code=400, detail="Invalid file name.")
            
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            pdf_paths.append(file_path)

        output_pdf_path = os.path.join(temp_dir, "concatenated.pdf")
        try:
            subprocess.run(['pdfunite'] + pdf_paths + [output_pdf_path], check=True)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="An error occurred while processing the files.")

        return FileResponse(output_pdf_path, media_type='application/pdf', filename="concatenated.pdf")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)