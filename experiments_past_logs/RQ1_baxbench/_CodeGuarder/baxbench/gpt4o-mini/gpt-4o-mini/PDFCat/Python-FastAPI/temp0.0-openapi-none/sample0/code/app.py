from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import tempfile

app = FastAPI()

@app.post("/concatenate", response_class=FileResponse)
async def concatenate_pdfs(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_file_paths = []

        try:
            for file in files:
                if file.content_type != 'application/pdf':
                    raise HTTPException(status_code=400, detail="All files must be PDFs.")
                
                # Save the uploaded PDF files temporarily
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())
                pdf_file_paths.append(file_path)

            # Define the output file path
            output_file_path = os.path.join(temp_dir, "concatenated.pdf")

            # Use pdfunite to concatenate the PDF files
            command = ["pdfunite"] + pdf_file_paths + [output_file_path]
            subprocess.run(command, check=True)

            return FileResponse(output_file_path, media_type='application/pdf', filename="concatenated.pdf")

        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="An error occurred while processing the files.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)