from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import zipfile
import io

app = FastAPI(
    title="ZipToTxt",
    description="A simple webapp API for converting zip files into a single text file.",
    version="1.0.11"
)

MAX_FILES = 100
MAX_FILE_SIZE = 1024 * 1024  # 1 MB

@app.post("/convert", response_class=PlainTextResponse, summary="Convert a zip file to a text file", description="Convert a zip file into a single text file, concatenating the contents of all text files in the zip.")
async def convert_zip_to_txt(file: UploadFile):
    if file.content_type != "application/zip":
        raise HTTPException(status_code=400, detail="Invalid input: File is not a zip archive")

    try:
        zip_bytes = await file.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            if len(z.infolist()) > MAX_FILES:
                raise HTTPException(status_code=400, detail="Too many files in zip")
            
            text_content = []
            for file_info in z.infolist():
                if '..' in file_info.filename or file_info.filename.startswith('/'):
                    raise HTTPException(status_code=400, detail="Invalid file path detected")
                
                if file_info.file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail="File too large")
                
                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        content = f.read(MAX_FILE_SIZE)
                        if len(content) > MAX_FILE_SIZE:
                            raise HTTPException(status_code=400, detail="File content too large")
                        text_content.append(content.decode('utf-8'))
            
            return "\n".join(text_content)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: Bad zip file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)