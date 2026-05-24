from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
import zipfile
import os
from io import BytesIO

app = FastAPI()

@app.post("/convert", response_class=PlainTextResponse)
async def convert_zip_to_text(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a zip file.")

    try:
        # Read the uploaded zip file
        zip_file_bytes = await file.read()
        zip_file = zipfile.ZipFile(BytesIO(zip_file_bytes))

        # Initialize a list to hold the contents of text files
        text_contents = []

        # Iterate through the files in the zip
        for info in zip_file.infolist():
            # Validate the file name to prevent Zip Slip vulnerability
            if not info.filename.startswith('/') and not os.path.isabs(info.filename):
                if info.filename.endswith('.txt'):
                    with zip_file.open(info) as text_file:
                        text_contents.append(text_file.read().decode('utf-8'))
            else:
                raise HTTPException(status_code=400, detail="Invalid file path in zip.")

        # Concatenate all text contents into a single string
        result_text = "\n".join(text_contents)
        return result_text

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)