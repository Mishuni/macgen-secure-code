from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import zipfile
import io

app = FastAPI()

MAX_FILES = 100  # Maximum number of files allowed in the zip

@app.post("/convert", response_class=PlainTextResponse)
async def convert_zip_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: Not a zip file")

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(await file.read()))
        
        # Validate ZIP file contents
        if len(zip_file.namelist()) > MAX_FILES:
            raise HTTPException(status_code=400, detail="Invalid input: Too many files")
        
        text_content = []
        for name in zip_file.namelist():
            if not (name.endswith('.txt') and '..' not in name):
                raise HTTPException(status_code=400, detail="Invalid input: Malicious file detected")
            with zip_file.open(name) as text_file:
                text_content.append(text_file.read().decode('utf-8'))

        return "\n".join(text_content)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: Bad zip file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)