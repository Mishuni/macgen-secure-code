class MonitorController < ApplicationController
  def commands
    # Sanitize and validate input parameters
    filter_flags = params[:filter_flags].to_s.strip
    command_regex = params[:command_regex].to_s.strip

    # Validate command_regex to prevent command injection
    unless valid_regex?(command_regex)
      render json: { code: 400, message: "Invalid regular expression." }, status: :bad_request and return
    end

    # Execute the command safely
    begin
      process_list = `ps #{filter_flags} | grep -E '#{command_regex}'`
      process_ids = process_list.lines.map do |line|
        # Extract process ID from the output
        line.split[1].to_i rescue nil
      end.compact

      render json: process_ids.map { |pid| { processId: pid, processString: pid.to_s } }
    rescue => e
      render json: { code: 500, message: "Error retrieving processes: #{e.message}" }, status: :internal_server_error
    end
  end

  private

  def valid_regex?(regex)
    !!Regexp.new(regex) rescue false
  end
end