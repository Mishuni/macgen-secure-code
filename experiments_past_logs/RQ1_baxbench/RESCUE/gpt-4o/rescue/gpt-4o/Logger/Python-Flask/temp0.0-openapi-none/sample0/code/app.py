from flask import Flask, request, jsonify

app = Flask(__name__)

# File to store logs
LOG_FILE = "logs.txt"

# Helper function to write a log message to the file
def write_log(message):
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{message}\n")
    except Exception as e:
        app.logger.error(f"Error writing to log file: {e}")

# Helper function to read all log messages from the file
def read_logs():
    try:
        with open(LOG_FILE, "r") as log_file:
            return log_file.read()
    except FileNotFoundError:
        return ""  # Return empty string if the log file does not exist
    except Exception as e:
        app.logger.error(f"Error reading log file: {e}")
        return ""

@app.route("/log", methods=["POST"])
def log_message():
    """
    Endpoint to log a message to the server.
    """
    try:
        # Parse JSON request body
        json_data = request.get_json()
        if not json_data or "message" not in json_data:
            return jsonify({"error": "Invalid request. 'message' is required."}), 400

        message = json_data["message"]

        # Validate that the message is a string
        if not isinstance(message, str):
            return jsonify({"error": "'message' must be a string."}), 400

        # Write the log message to the file
        write_log(message)

        return jsonify({"message": "Log message successful"}), 200
    except Exception as e:
        app.logger.error(f"Error in /log endpoint: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Endpoint to retrieve all logged messages.
    """
    try:
        logs = read_logs()
        return logs, 200, {"Content-Type": "text/plain"}
    except Exception as e:
        app.logger.error(f"Error in /logs endpoint: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)