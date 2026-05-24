from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import tempfile
import re

app = FastAPI()

@app.post("/concatenate", response_class=FileResponse)
async def concatenate(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Invalid input or missing files.")
    
    temp_files = []
    try:
        # Validate and save uploaded files
        for file in files:
            if file.content_type != 'application/pdf':
                raise HTTPException(status_code=400, detail="All files must be PDF.")
            if not re.match(r'^[\w\-. ]+$', file.filename):
                raise HTTPException(status_code=400, detail="Invalid filename.")
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=".pdf")
            temp_file.write(await file.read())
            temp_file.close()
            temp_files.append(temp_file.name)

        # Define output file path
        output_file = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=".pdf").name

        # Concatenate PDFs using pdfunite
        subprocess.run(["pdfunite"] + temp_files + [output_file], check=True)

        return FileResponse(output_file, media_type='application/pdf', filename="concatenated.pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the files.")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            os.remove(temp_file)
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)