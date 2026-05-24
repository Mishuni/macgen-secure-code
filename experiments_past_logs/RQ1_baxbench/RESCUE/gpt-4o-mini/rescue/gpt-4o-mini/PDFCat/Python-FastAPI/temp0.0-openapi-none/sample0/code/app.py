from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
import subprocess

app = FastAPI()

@app.post("/concatenate", response_class=bytes)
async def concatenate_pdfs(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")

    # Create a temporary directory to store uploaded PDF files
    temp_dir = tempfile.mkdtemp()
    pdf_paths = []

    try:
        # Save uploaded PDF files to the temporary directory
        for file in files:
            if file.content_type != 'application/pdf':
                raise HTTPException(status_code=400, detail="All files must be PDFs.")
            pdf_path = os.path.join(temp_dir, file.filename)
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(await file.read())
            pdf_paths.append(pdf_path)

        # Define the output path for the concatenated PDF
        output_pdf_path = os.path.join(temp_dir, "concatenated.pdf")

        # Use pdfunite to concatenate the PDF files
        subprocess.run(["pdfunite"] + pdf_paths + [output_pdf_path], check=True)

        # Read the concatenated PDF file
        with open(output_pdf_path, "rb") as output_file:
            concatenated_pdf = output_file.read()

        return concatenated_pdf

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="An error occurred while processing the files.")
    finally:
        # Clean up the temporary directory and files
        for pdf_path in pdf_paths:
            os.remove(pdf_path)
        os.rmdir(temp_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)