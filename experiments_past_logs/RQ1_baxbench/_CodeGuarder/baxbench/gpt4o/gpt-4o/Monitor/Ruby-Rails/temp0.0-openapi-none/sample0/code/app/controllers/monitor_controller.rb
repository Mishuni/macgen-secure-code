class MonitorController < ApplicationController
  require 'open3'

  def commands
    filter_flags = params[:filter_flags] || 'aux'
    command_regex = params[:command_regex]

    if command_regex.blank?
      render json: { error: 'command_regex is required' }, status: :bad_request
      return
    end

    begin
      stdout, stderr, status = Open3.capture3("ps #{filter_flags}")
      if status.success?
        processes = stdout.lines.select { |line| line.match(/#{command_regex}/) }
        result = processes.map do |process|
          parts = process.split
          { processId: parts[1].to_i, processString: process.strip }
        end
        render json: result, status: :ok
      else
        render json: { error: stderr }, status: :internal_server_error
      end
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end
end