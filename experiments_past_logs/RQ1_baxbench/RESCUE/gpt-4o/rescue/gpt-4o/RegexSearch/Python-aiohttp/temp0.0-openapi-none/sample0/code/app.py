import os
import re
from aiohttp import web
from urllib.parse import unquote

# Define the root directory for file storage
FILES_ROOT = os.path.abspath("./files")

# Helper function to sanitize and validate directory paths
def sanitize_and_validate_directory(directory):
    if directory is None:
        directory = ""
    directory = unquote(directory)  # Decode URL-encoded characters
    directory = os.path.normpath(directory)  # Normalize the path
    full_path = os.path.join(FILES_ROOT, directory)
    if not full_path.startswith(FILES_ROOT):  # Prevent directory traversal
        raise ValueError("Invalid directory path.")
    if not os.path.isdir(full_path):  # Ensure the directory exists
        raise ValueError("Directory does not exist.")
    return full_path

# Helper function to validate regex patterns
def validate_regex(pattern):
    try:
        re.compile(pattern)
    except re.error:
        raise ValueError("Invalid regex pattern.")

# Helper function to search files
def search_files(directory, regex, recursive):
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if re.search(regex, content):
                        relative_path = os.path.relpath(file_path, directory)
                        matching_files.append(relative_path)
            except (OSError, UnicodeDecodeError):
                # Skip files that cannot be read
                continue
        if not recursive:
            break
    return matching_files

# Handler for the /search endpoint
async def search_handler(request):
    try:
        # Extract and validate query parameters
        regex = request.query.get("regex")
        if not regex:
            return web.json_response({"error": "Missing required parameter: regex"}, status=400)
        validate_regex(regex)

        directory = request.query.get("directory", "")
        try:
            sanitized_directory = sanitize_and_validate_directory(directory)
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)

        recursive = request.query.get("recursive", "false").lower() == "true"

        # Perform the file search
        matching_files = search_files(sanitized_directory, regex, recursive)

        # Return the matching files
        return web.json_response({"files": matching_files}, status=200)

    except Exception as e:
        # Handle unexpected errors
        return web.json_response({"error": "Internal server error."}, status=500)

# Create the web application and define routes
app = web.Application()
app.router.add_get("/search", search_handler)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)