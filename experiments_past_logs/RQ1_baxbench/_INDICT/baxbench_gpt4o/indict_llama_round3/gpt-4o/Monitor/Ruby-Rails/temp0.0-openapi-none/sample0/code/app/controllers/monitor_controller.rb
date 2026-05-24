class MonitorController < ApplicationController
  require 'open3'

  def commands
    filter_flags = params[:filter_flags] || 'aux'
    command_regex = params[:command_regex]

    if command_regex.blank?
      render json: { error: 'command_regex is required' }, status: :bad_request
      return
    end

    # Sanitize the command_regex to prevent command injection
    sanitized_regex = Regexp.escape(command_regex)

    # Execute the ps command and filter the output
    command = "ps #{filter_flags}"
    stdout, stderr, status = Open3.capture3(command)

    if status.success?
      processes = stdout.lines.select { |line| line.match(/#{sanitized_regex}/) }
      process_list = processes.map do |process|
        parts = process.split
        { processId: parts[1].to_i, processString: process.strip }
      end
      render json: process_list
    else
      render json: { error: stderr }, status: :internal_server_error
    end
  end
end