from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    try:
        # Parse the incoming JSON request
        json_data = request.get_json()
        if not json_data or 'fileName' not in json_data or 'fileContent' not in json_data:
            return jsonify({"error": "Invalid input. 'fileName' and 'fileContent' are required."}), 400

        file_name = json_data['fileName']
        file_content = json_data['fileContent']

        # Validate file extension
        if not (file_name.endswith('.ts') or file_name.endswith('.cpp')):
            return jsonify({"error": "Unsupported file type. Only .ts and .cpp files are allowed."}), 400

        # Create a temporary file to store the code
        temp_file_path = f"/tmp/{file_name}"
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(file_content)

        # Compile the file based on its extension
        if file_name.endswith('.ts'):
            # Compile TypeScript file
            compile_command = ['tsc', temp_file_path]
        elif file_name.endswith('.cpp'):
            # Compile C++ file
            output_file_path = temp_file_path.replace('.cpp', '')
            compile_command = ['g++', temp_file_path, '-o', output_file_path]

        # Execute the compile command
        process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check for compilation errors
        if process.returncode != 0:
            return jsonify({
                "hasError": True,
                "compilerError": process.stderr.strip()
            }), 200
        else:
            return jsonify({
                "hasError": False,
                "compilerError": None
            }), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        # Clean up the temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if 'output_file_path' in locals() and os.path.exists(output_file_path):
            os.remove(output_file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)