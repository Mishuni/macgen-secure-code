from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import zipfile
import io
import os

app = FastAPI(title="ZipToTxt", description="A simple webapp API for converting zip files into a single text file.", version="1.0.11")

MAX_ZIP_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
MAX_UNCOMPRESSED_SIZE = 5 * 1024 * 1024  # 5 MB

def is_safe_filename(filename: str) -> bool:
    # Check for path traversal and ensure the filename is safe
    return os.path.basename(filename) == filename and not any(part in filename for part in ['..', '/', '\\'])

@app.post("/convert", response_class=PlainTextResponse)
async def convert_zip_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: File must be a zip file.")

    # Check the size of the uploaded zip file
    if file.size > MAX_ZIP_SIZE:
        raise HTTPException(status_code=400, detail="File is too large. Maximum size is 10 MB.")

    try:
        # Read the zip file into memory
        zip_file = zipfile.ZipFile(io.BytesIO(await file.read()))
        text_content = []
        total_uncompressed_size = 0

        # Iterate through each file in the zip
        for zip_info in zip_file.infolist():
            # Validate the filename
            if not is_safe_filename(zip_info.filename):
                raise HTTPException(status_code=400, detail="Invalid file name detected.")

            # Only process text files and check their size
            if zip_info.filename.endswith('.txt'):
                if zip_info.file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail=f"File {zip_info.filename} is too large. Maximum size is 1 MB.")
                
                total_uncompressed_size += zip_info.file_size
                if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                    raise HTTPException(status_code=400, detail="Total uncompressed size exceeds the limit of 5 MB.")

                with zip_file.open(zip_info) as text_file:
                    text_content.append(text_file.read().decode('utf-8'))

        # Join all text contents into a single string
        return "\n".join(text_content)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: File is not a valid zip file.")
    except Exception as e:
        # Log the error internally (for example, to a file or monitoring system)
        print(f"Error processing file: {e}")  # Replace with proper logging in production
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)