from fastapi import FastAPI, UploadFile, File, HTTPException
import zipfile
import os
from io import BytesIO

app = FastAPI()

@app.post("/convert", response_class=str)
async def convert_zip_to_text(file: UploadFile = File(...)):
    # Validate the file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: File must be a zip file.")

    # Read the zip file
    try:
        zip_file = zipfile.ZipFile(BytesIO(await file.read()))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: File is not a valid zip file.")

    # Initialize a list to hold the contents of the text files
    text_contents = []

    # Iterate through the files in the zip
    for zip_info in zip_file.infolist():
        # Sanitize the filename to prevent directory traversal
        if not zip_info.filename.startswith(('/', '')):  # Ensure it does not start with a directory traversal
            if zip_info.filename.endswith('.txt'):  # Only process text files
                with zip_file.open(zip_info) as text_file:
                    text_contents.append(text_file.read().decode('utf-8'))

    # Join all text contents into a single string
    result_text = "\n".join(text_contents)

    return result_text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)