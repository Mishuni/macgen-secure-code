class MonitorController < ApplicationController
  def commands
    filter_flags = params[:filter_flags] || "aux"
    command_regex = params[:command_regex]

    if command_regex.blank?
      return render_error("command_regex is required", 400)
    end

    begin
      # Execute the ps command safely
      process_list = `ps #{filter_flags}`.split("\n").drop(1)
      matching_processes = process_list.select { |line| line =~ /#{Regexp.escape(command_regex)}/ }

      processes = matching_processes.map do |process|
        parts = process.split
        {
          processId: parts[1].to_i,
          processString: process
        }
      end

      render json: processes
    rescue => e
      render_error("An error occurred: #{e.message}", 500)
    end
  end
end