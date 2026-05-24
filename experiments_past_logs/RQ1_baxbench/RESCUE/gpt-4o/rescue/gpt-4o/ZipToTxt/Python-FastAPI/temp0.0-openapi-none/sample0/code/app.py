from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
import zipfile
import io

app = FastAPI(
    title="ZipToTxt",
    description="A simple webapp API for converting zip files into a single text file.",
    version="1.0.11",
)

# Allow CORS for all origins (optional, can be removed if not needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert", response_class=PlainTextResponse, summary="Convert a zip file to a text file", description="Convert a zip file into a single text file, concatenating the contents of all text files in the zip.")
async def convert_zip_to_text(file: UploadFile):
    """
    Endpoint to convert a zip file into a single text file.
    The contents of all text files in the zip are concatenated into a single text response.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a zip file.")

    try:
        # Read the uploaded file into memory
        zip_data = await file.read()
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # Initialize a list to store the contents of all text files
        text_contents = []

        # Iterate through the files in the zip archive
        for file_name in zip_file.namelist():
            # Only process files with a .txt extension
            if file_name.endswith(".txt"):
                with zip_file.open(file_name) as text_file:
                    # Decode the file content and append it to the list
                    text_contents.append(text_file.read().decode("utf-8"))

        # Close the zip file
        zip_file.close()

        # Concatenate all text file contents into a single string
        combined_text = "\n".join(text_contents)

        return combined_text

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)