import os
import json
from aiohttp import web

# Define the base directory for file storage
BASE_DIR = os.path.abspath("/data")

# Utility function to sanitize and validate directory paths
def sanitize_and_validate_path(base_dir, path):
    if path is None:
        return base_dir
    abs_path = os.path.abspath(os.path.join(base_dir, path))
    if not abs_path.startswith(base_dir):
        raise ValueError("Invalid directory path")
    return abs_path

# Utility function to search for files by content
def search_files_by_content(directory, search_content):
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if search_content in f.read():
                        matching_files.append(file_path)
            except (UnicodeDecodeError, OSError):
                # Skip files that cannot be read as text
                continue
    return matching_files

# Utility function to search for files by filename
def search_files_by_name(directory, search_filename):
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == search_filename:
                matching_files.append(os.path.join(root, file))
    return matching_files

# Handler for the /search endpoint
async def search_files(request):
    try:
        # Parse the JSON request body
        data = await request.json()
        search_content = data.get("search_content")
        search_filename = data.get("search_filename")
        search_dir = data.get("search_dir")

        # Validate and sanitize the search directory
        try:
            target_dir = sanitize_and_validate_path(BASE_DIR, search_dir)
        except ValueError:
            return web.Response(status=400, body=b"Invalid directory path")

        # Perform the search
        matching_files = set()
        if search_content:
            matching_files.update(search_files_by_content(target_dir, search_content))
        if search_filename:
            matching_files.update(search_files_by_name(target_dir, search_filename))

        # Return the results as a JSON response
        return web.json_response({"files": list(matching_files)}, status=200)

    except json.JSONDecodeError:
        return web.Response(status=400, body=b"Invalid JSON input")
    except Exception as e:
        return web.Response(status=500, body=str(e).encode("utf-8"))

# Create the aiohttp application and define routes
app = web.Application()
app.router.add_post("/search", search_files)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)