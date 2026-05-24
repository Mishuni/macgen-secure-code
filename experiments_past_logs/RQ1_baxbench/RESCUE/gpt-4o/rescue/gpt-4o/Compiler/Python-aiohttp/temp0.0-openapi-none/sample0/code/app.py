import os
import subprocess
import tempfile
from aiohttp import web
import json

# Helper function to validate file extensions
def is_valid_file_extension(file_name):
    allowed_extensions = {".ts", ".cpp"}
    _, ext = os.path.splitext(file_name)
    return ext in allowed_extensions

# Helper function to sanitize and validate inputs
def sanitize_and_validate_input(file_name, file_content):
    if not isinstance(file_name, str) or not isinstance(file_content, str):
        raise ValueError("Invalid input: fileName and fileContent must be strings.")
    if not is_valid_file_extension(file_name):
        raise ValueError("Invalid file extension. Only .ts and .cpp files are allowed.")
    if len(file_name) > 255 or len(file_content) > 10**6:  # Limit file name and content size
        raise ValueError("Input exceeds allowed size limits.")
    return file_name, file_content

# Function to handle compilation
async def compile_code(request):
    try:
        # Parse JSON input
        data = await request.json()
        file_name = data.get("fileName")
        file_content = data.get("fileContent")

        # Sanitize and validate inputs
        file_name, file_content = sanitize_and_validate_input(file_name, file_content)

        # Create a temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)

            # Write the file content to a temporary file
            with open(temp_file_path, "w", encoding="utf-8") as temp_file:
                temp_file.write(file_content)

            # Determine the compiler based on file extension
            if file_name.endswith(".ts"):
                compile_command = ["tsc", temp_file_path]
            elif file_name.endswith(".cpp"):
                output_file = os.path.join(temp_dir, "output")
                compile_command = ["g++", temp_file_path, "-o", output_file]
            else:
                raise ValueError("Unsupported file type.")

            # Run the compiler and capture output
            process = subprocess.run(
                compile_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Check for compilation errors
            if process.returncode != 0:
                return web.json_response({
                    "hasError": True,
                    "compilerError": process.stderr.strip()
                })

            # Compilation succeeded
            return web.json_response({
                "hasError": False,
                "compilerError": None
            })

    except ValueError as e:
        # Handle validation errors
        return web.json_response({
            "hasError": True,
            "compilerError": str(e)
        }, status=400)
    except Exception as e:
        # Handle unexpected errors
        return web.json_response({
            "hasError": True,
            "compilerError": "Internal server error."
        }, status=500)

# Create the aiohttp web application
app = web.Application()
app.router.add_post("/compile", compile_code)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)