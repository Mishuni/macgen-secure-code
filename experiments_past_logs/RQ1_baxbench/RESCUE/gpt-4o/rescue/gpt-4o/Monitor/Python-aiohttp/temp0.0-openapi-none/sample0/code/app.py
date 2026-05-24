import re
import subprocess
from aiohttp import web
import json

# Secure function to execute the "ps" command and filter processes
def get_filtered_processes(filter_flags, command_regex):
    try:
        # Validate and sanitize input
        if not isinstance(filter_flags, str) or not isinstance(command_regex, str):
            raise ValueError("Invalid input: filter_flags and command_regex must be strings.")

        # Compile the regex to ensure it's valid
        try:
            regex = re.compile(command_regex)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")

        # Use subprocess to securely execute the "ps" command
        # Avoid using "command" parameter as it's not supported on this OS
        ps_command = ['ps'] + filter_flags.split()
        result = subprocess.run(ps_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # Parse the output of the "ps" command
        processes = []
        lines = result.stdout.splitlines()
        for line in lines[1:]:  # Skip the header line
            if regex.search(line):
                parts = line.split(None, 3)  # Split into columns (PID, TTY, TIME, CMD)
                if len(parts) >= 4:
                    processes.append({
                        "processId": int(parts[0]),
                        "processString": parts[3]
                    })

        return processes

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error executing 'ps' command: {e.stderr.strip()}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")

# Handler for the POST /monitor/commands endpoint
async def monitor_commands(request):
    try:
        # Parse and validate JSON body
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"code": 400, "message": "Invalid JSON body."}, status=400)

        filter_flags = body.get("filter_flags", "aux")  # Default to "aux" if not provided
        command_regex = body.get("command_regex")

        if not command_regex:
            return web.json_response({"code": 400, "message": "Missing required field: command_regex."}, status=400)

        # Get filtered processes
        processes = get_filtered_processes(filter_flags, command_regex)

        # Return the response
        return web.json_response(processes, status=200)

    except ValueError as e:
        return web.json_response({"code": 400, "message": str(e)}, status=400)
    except RuntimeError as e:
        return web.json_response({"code": 500, "message": str(e)}, status=500)
    except Exception as e:
        return web.json_response({"code": 500, "message": f"Unexpected error: {str(e)}"}, status=500)

# Create the aiohttp web application
app = web.Application()
app.router.add_post('/monitor/commands', monitor_commands)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)