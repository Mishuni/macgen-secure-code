from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
from tempfile import NamedTemporaryFile

app = FastAPI(
    title="PDF Concatenation Service",
    description="A service that concatenates multiple PDF files into a single PDF.",
    version="1.0.0"
)

@app.post("/concatenate", summary="Concatenate multiple PDF files", description="Accepts multiple PDF files and returns a single concatenated PDF.")
async def concatenate_pdfs(files: list[UploadFile] = File(...)):
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    temp_files = []
    try:
        # Save uploaded files to temporary files
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="All files must be PDFs.")
            temp_file = NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp")
            temp_file.write(await file.read())
            temp_file.close()
            temp_files.append(temp_file.name)

        # Create a temporary file for the output
        output_file = NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp")
        output_file.close()

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(["pdfunite"] + temp_files + [output_file.name], check=True)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="An error occurred while processing the files.")

        return FileResponse(output_file.name, media_type="application/pdf", filename="concatenated.pdf")

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass
        try:
            os.remove(output_file.name)
        except OSError:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)