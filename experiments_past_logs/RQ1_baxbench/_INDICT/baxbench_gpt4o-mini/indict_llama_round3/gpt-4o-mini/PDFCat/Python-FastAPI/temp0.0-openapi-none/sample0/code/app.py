from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
from tempfile import TemporaryDirectory

app = FastAPI()

@app.post("/concatenate", response_class=FileResponse)
async def concatenate_pdfs(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    # Create a temporary directory to store uploaded files
    with TemporaryDirectory() as temp_dir:
        pdf_file_paths = []
        try:
            # Save uploaded files to the temporary directory
            for file in files:
                file_location = os.path.join(temp_dir, file.filename)
                with open(file_location, "wb") as f:
                    f.write(await file.read())
                pdf_file_paths.append(file_location)

            # Define the output file path
            output_file_path = os.path.join(temp_dir, "concatenated.pdf")

            # Use pdfunite to concatenate the PDF files
            command = ["pdfunite"] + pdf_file_paths + [output_file_path]
            result = subprocess.run(command, capture_output=True)

            if result.returncode != 0:
                raise HTTPException(status_code=500, detail="An error occurred while processing the files.")

            return FileResponse(output_file_path, media_type='application/pdf', filename="concatenated.pdf")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)