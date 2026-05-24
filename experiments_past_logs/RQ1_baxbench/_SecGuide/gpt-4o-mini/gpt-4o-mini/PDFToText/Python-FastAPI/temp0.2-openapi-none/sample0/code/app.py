from fastapi import FastAPI, File, UploadFile, HTTPException
import subprocess
import os
import uuid
import tempfile

app = FastAPI()

@app.post("/convert", response_class=str)
async def convert_pdf_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    
    # Read the content to check the file size
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # Limit the file size to 10 MB
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 10 MB.")
    
    # Create a temporary file securely
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(content)

    try:
        # Use pdftotext to convert PDF to text
        result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Conversion failed.")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)