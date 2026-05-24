require 'open3'

class MonitorController < ApplicationController
  def commands
    # Validate and sanitize input
    filter_flags = params[:filter_flags].to_s.strip
    command_regex = params.require(:command_regex).to_s.strip

    # Validate the regular expression
    begin
      Regexp.new(command_regex)
    rescue RegexpError => e
      render json: { code: 400, message: "Invalid regular expression: #{e.message}" }, status: :bad_request
      return
    end

    # Execute the `ps` command securely
    ps_command = "ps #{filter_flags} -o pid,command"
    stdout, stderr, status = Open3.capture3(ps_command)

    if !status.success?
      render json: { code: 500, message: "Failed to execute 'ps' command: #{stderr}" }, status: :internal_server_error
      return
    end

    # Parse the output and filter results
    processes = []
    stdout.each_line.with_index do |line, index|
      next if index.zero? # Skip the header line
      pid, command = line.strip.split(/\s+/, 2)
      next unless pid && command

      if command.match?(Regexp.new(command_regex))
        processes << { processId: pid.to_i, processString: command }
      end
    end

    render json: processes, status: :ok
  end
end