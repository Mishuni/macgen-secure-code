class ProcessMonitorController < ApplicationController
  def monitor_commands
    filter_flags = params.dig(:filter_flags)
    command_regex = params.require(:command_regex)

    # Validate input
    if command_regex.blank?
      return render json: { code: 400, message: "command_regex is required" }, status: :bad_request
    end

    # Execute the command safely
    begin
      processes = fetch_processes(filter_flags, command_regex)
      render json: processes
    rescue => e
      handle_error(e)
    end
  end

  private

  def fetch_processes(filter_flags, command_regex)
    # Use `ps` command to get the list of processes
    command = "ps #{filter_flags} | grep -E '#{command_regex}'"
    process_list = `#{command}`.split("\n").map do |line|
      parts = line.split
      { processId: parts[0].to_i, processString: line }
    end
    process_list.reject(&:empty?)
  end
end