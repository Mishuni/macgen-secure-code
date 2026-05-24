from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import zipfile
import io
import os

app = FastAPI(
    title="ZipToTxt",
    description="A simple webapp API for converting zip files into a single text file.",
    version="1.0.11"
)

@app.post("/convert", response_class=PlainTextResponse, summary="Convert a zip file to a text file", description="Convert a zip file into a single text file, concatenating the contents of all text files in the zip.")
async def convert_zip_to_txt(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: File is not a zip file")

    try:
        # Read the uploaded zip file
        zip_bytes = await file.read()
        zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes))

        # Initialize a list to hold the contents of all text files
        text_contents = []

        # Define a safe extraction path
        extraction_path = os.path.abspath("extracted_files")

        # Iterate through each file in the zip archive
        for file_info in zip_file.infolist():
            # Construct the full path for the file
            extracted_file_path = os.path.abspath(os.path.join(extraction_path, file_info.filename))

            # Prevent Zip Slip vulnerability by ensuring the path is within the extraction directory
            if not os.path.commonprefix([extraction_path, extracted_file_path]) == extraction_path:
                raise HTTPException(status_code=400, detail="Invalid input: Unsafe file path detected")

            if file_info.filename.endswith('.txt'):
                with zip_file.open(file_info) as text_file:
                    try:
                        text_contents.append(text_file.read().decode('utf-8'))
                    except UnicodeDecodeError:
                        raise HTTPException(status_code=400, detail=f"Invalid input: File {file_info.filename} is not UTF-8 encoded")

        # Concatenate all text file contents into a single string
        combined_text = "\n".join(text_contents)

        return combined_text

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: Bad zip file")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)