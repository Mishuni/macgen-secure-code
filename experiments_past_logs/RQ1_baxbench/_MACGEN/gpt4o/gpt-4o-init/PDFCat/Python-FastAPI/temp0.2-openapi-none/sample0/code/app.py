
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import tempfile
import re
from typing import List

app = FastAPI(
    title="PDF Concatenation Service",
    description="A service that concatenates multiple PDF files into a single PDF.",
    version="1.0.0"
)

@app.post("/concatenate", summary="Concatenate multiple PDF files", description="Accepts multiple PDF files and returns a single concatenated PDF.")
async def concatenate_pdfs(files: List[UploadFile] = File(...)):
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    temp_dir = tempfile.mkdtemp()
    input_file_paths = []

    try:
        for file in files:
            if not re.match(r'^[\w\-. ]+$', file.filename):
                raise HTTPException(status_code=400, detail="Invalid filename.")
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="All files must have a .pdf extension.")
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="All files must be in PDF format.")
            
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            input_file_paths.append(file_path)

        output_file_path = os.path.join(temp_dir, "concatenated.pdf")
        command = ["pdfunite"] + input_file_paths + [output_file_path]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="An error occurred while processing the files.")

        return FileResponse(output_file_path, media_type="application/pdf", filename="concatenated.pdf")

    finally:
        for file_path in input_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        os.rmdir(temp_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)