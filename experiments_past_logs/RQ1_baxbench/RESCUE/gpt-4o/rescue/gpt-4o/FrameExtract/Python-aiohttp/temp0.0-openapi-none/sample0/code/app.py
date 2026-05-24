import os
import tempfile
import shutil
import subprocess
from aiohttp import web
import json

# Define constants
STORAGE_DIR = tempfile.mkdtemp()  # Temporary directory for storing uploaded files
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}  # Allowed video file extensions

# Helper function to sanitize and validate file paths
def is_safe_path(base_path, target_path):
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(target_path)
    return abs_target.startswith(abs_base)

# Route handler for extracting a frame
async def extract_frame(request):
    reader = await request.multipart()
    video_file = None
    frame_number = None
    video_file_name = None

    # Parse multipart form data
    while True:
        part = await reader.next()
        if part is None:
            break
        if part.name == "video":
            video_file = part
        elif part.name == "frameNumber":
            frame_number = await part.text()
        elif part.name == "videoFileName":
            video_file_name = await part.text()

    # Validate inputs
    if not video_file or not frame_number or not video_file_name:
        return web.Response(
            status=400,
            body=json.dumps({"error": "Missing required fields"}).encode("utf8"),
            content_type="application/json",
        )

    try:
        frame_number = int(frame_number)
        if frame_number < 0:
            raise ValueError("Frame number must be non-negative")
    except ValueError:
        return web.Response(
            status=400,
            body=json.dumps({"error": "Invalid frame number"}).encode("utf8"),
            content_type="application/json",
        )

    file_extension = os.path.splitext(video_file_name)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return web.Response(
            status=400,
            body=json.dumps({"error": "Unsupported file type"}).encode("utf8"),
            content_type="application/json",
        )

    # Save the uploaded video file securely
    video_path = os.path.join(STORAGE_DIR, video_file_name)
    if not is_safe_path(STORAGE_DIR, video_path):
        return web.Response(
            status=400,
            body=json.dumps({"error": "Invalid file path"}).encode("utf8"),
            content_type="application/json",
        )

    with open(video_path, "wb") as f:
        while True:
            chunk = await video_file.read_chunk()
            if not chunk:
                break
            f.write(chunk)

    # Extract the frame using ffmpeg
    output_image_path = os.path.join(STORAGE_DIR, f"frame_{frame_number}.png")
    if not is_safe_path(STORAGE_DIR, output_image_path):
        return web.Response(
            status=400,
            body=json.dumps({"error": "Invalid output path"}).encode("utf8"),
            content_type="application/json",
        )

    try:
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"select=eq(n\\,{frame_number})",
            "-vframes",
            "1",
            output_image_path,
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return web.Response(
            status=404,
            body=json.dumps({"error": f"Frame at index {frame_number} could not be found."}).encode("utf8"),
            content_type="application/json",
        )

    # Return the extracted frame as a response
    if os.path.isfile(output_image_path):
        return web.FileResponse(output_image_path, headers={"Content-Type": "image/png"})
    else:
        return web.Response(
            status=404,
            body=json.dumps({"error": f"Frame at index {frame_number} could not be found."}).encode("utf8"),
            content_type="application/json",
        )

# Create the app and define routes
app = web.Application()
app.router.add_post("/extract", extract_frame)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)