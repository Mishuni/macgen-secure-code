from fastapi import FastAPI, UploadFile, File, HTTPException
import zipfile
import io

app = FastAPI(title="ZipToTxt", description="A simple webapp API for converting zip files into a single text file.", version="1.0.11")

@app.post("/convert", response_class=str)
async def convert_zip_to_text(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid input: File must be a zip file.")

    # Read the zip file
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(await file.read()))
        text_content = []

        # Check if the zip file is empty
        if not zip_file.namelist():
            raise HTTPException(status_code=400, detail="Invalid input: Zip file is empty.")

        # Iterate through each file in the zip
        for zip_info in zip_file.infolist():
            if zip_info.filename.endswith('.txt'):
                with zip_file.open(zip_info) as text_file:
                    text_content.append(text_file.read().decode('utf-8'))

        # Join all text contents into a single string
        if not text_content:
            raise HTTPException(status_code=400, detail="No text files found in the zip.")

        return "\n".join(text_content)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid input: File is not a valid zip file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)