from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
import uvicorn
import tempfile
import shutil
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI(
    title="PDF Concatenation Service",
    description="A service that concatenates multiple PDF files into a single PDF.",
    version="1.0.0"
)

@app.post("/concatenate", response_class=FileResponse, responses={
    200: {
        "description": "Successfully concatenated the PDF files.",
        "content": {"application/pdf": {}}
    },
    400: {
        "description": "Bad Request - Invalid input or missing files.",
        "content": {"application/json": {"example": {"error": "Invalid input or missing files."}}}
    },
    500: {
        "description": "Internal Server Error - An error occurred while processing the files.",
        "content": {"application/json": {"example": {"error": "An error occurred while processing the files."}}}
    }
})
async def concatenate_pdfs(files: List[UploadFile] = File(...)):
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    temp_dir = tempfile.mkdtemp()

    try:
        pdf_writer = PdfWriter()

        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="All files must be PDFs.")
            
            # Save uploaded file to a secure temporary directory
            file_path = os.path.join(temp_dir, file.filename)

            with open(file_path, "wb") as f:
                f.write(await file.read())

            # Validate and read PDF content
            try:
                pdf_reader = PdfReader(file_path)
                for page in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page])
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid PDF file: {file.filename}")

        # Write the concatenated PDF to a file
        output_filename = os.path.join(temp_dir, "concatenated.pdf")
        with open(output_filename, "wb") as output_pdf:
            pdf_writer.write(output_pdf)

        return FileResponse(output_filename, media_type='application/pdf', filename="concatenated.pdf")

    except Exception as e:
        # Log the error details for debugging
        print(f"Error during PDF concatenation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the files.")
    finally:
        # Clean up temporary files and directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)