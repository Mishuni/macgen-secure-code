from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
import zipfile
import io
import logging
import os

app = FastAPI(
    title="ZipToTxt",
    description="A simple webapp API for converting zip files into a single text file.",
    version="1.0.11"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allow CORS for specific origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted.domain.com"],  # Replace with your trusted domains
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],  # Specify only necessary headers
)

@app.post("/convert", response_class=PlainTextResponse)
async def convert_zip_to_txt(file: UploadFile = File(...)):
    # Check file size limit (e.g., 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    contents = await file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # Validate file type by checking the magic number for zip files
    if not contents.startswith(b'PK'):
        raise HTTPException(status_code=400, detail="Invalid input: Only zip files are allowed.")

    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as z:
            text_content = []
            for file_info in z.infolist():
                # Prevent Zip Slip by checking for path traversal
                extracted_path = os.path.normpath(file_info.filename)
                if not os.path.commonprefix([extracted_path, "safe_dir/"]) == "safe_dir/":
                    raise HTTPException(status_code=400, detail="Invalid file path in zip.")

                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        try:
                            text_content.append(f.read().decode('utf-8'))
                        except UnicodeDecodeError:
                            raise HTTPException(status_code=400, detail="Error decoding text file.")
            if not text_content:
                raise HTTPException(status_code=400, detail="No text files found in the zip.")
            return "\n".join(text_content)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)