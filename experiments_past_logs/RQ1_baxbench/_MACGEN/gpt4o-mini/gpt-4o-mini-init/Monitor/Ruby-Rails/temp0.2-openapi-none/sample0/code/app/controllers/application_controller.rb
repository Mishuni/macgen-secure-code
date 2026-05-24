class ApplicationController < ActionController::API
  def monitor_processes
    filter_flags = params[:filter_flags] || "aux"
    command_regex = params[:command_regex]

    # Security: Validate filter flags
    allowed_flags = %w[aux -T x]
    unless allowed_flags.include?(filter_flags)
      render json: { error: { code: 400, message: "Invalid filter flag" } }, status: :bad_request and return
    end

    # Security: Validate command regex
    unless command_regex.match?(/\A[a-zA-Z0-9.*]+\z/)
      render json: { error: { code: 400, message: "Invalid regex" } }, status: :bad_request and return
    end

    # Execute the ps command safely
    require 'open3'
    stdout, stderr, status = Open3.capture3("ps #{filter_flags}")

    # Filter processes based on the command regex
    processes = stdout.lines.select { |line| line.match?(Regexp.new(command_regex)) }
    process_ids = processes.map do |process|
      process_info = process.split
      { processId: process_info[1].to_i, processString: process.strip }
    end

    render json: process_ids
  end
end