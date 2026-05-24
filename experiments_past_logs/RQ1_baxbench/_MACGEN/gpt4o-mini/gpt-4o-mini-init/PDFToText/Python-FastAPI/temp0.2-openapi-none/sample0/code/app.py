from fastapi import FastAPI, UploadFile, File, HTTPException
import subprocess
import os
import uuid

app = FastAPI()

@app.post("/convert", response_class=str)
async def convert_pdf_to_text(file: UploadFile = File(...)):
    # Validate file content type
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    
    # Create a unique temporary file path
    temp_file_name = f"{uuid.uuid4()}.pdf"
    temp_file_path = os.path.join("/tmp", temp_file_name)
    
    # Save the uploaded file to a temporary location
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())
    
    try:
        # Use pdftotext to convert PDF to text
        result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Conversion failed.")
        
        return result.stdout.strip()
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)