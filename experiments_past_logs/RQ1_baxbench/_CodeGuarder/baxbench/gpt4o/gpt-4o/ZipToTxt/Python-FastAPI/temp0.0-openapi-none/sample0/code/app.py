from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from zipfile import ZipFile, is_zipfile
from io import BytesIO
import os

app = FastAPI(
    title="ZipToTxt",
    description="A simple webapp API for converting zip files into a single text file.",
    version="1.0.11"
)

@app.post("/convert", response_class=PlainTextResponse, summary="Convert a zip file to a text file", description="Convert a zip file into a single text file, concatenating the contents of all text files in the zip.")
async def convert_zip_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: Only zip files are allowed.")

    try:
        file_content = await file.read()
        if not is_zipfile(BytesIO(file_content)):
            raise HTTPException(status_code=400, detail="Invalid input: The file is not a valid zip archive.")

        with ZipFile(BytesIO(file_content)) as zip_file:
            text_content = []
            for file_info in zip_file.infolist():
                if file_info.filename.endswith('.txt'):
                    with zip_file.open(file_info) as text_file:
                        text_content.append(text_file.read().decode('utf-8'))
            
            if not text_content:
                raise HTTPException(status_code=400, detail="No text files found in the zip archive.")
            
            return "\n".join(text_content)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while processing the file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)