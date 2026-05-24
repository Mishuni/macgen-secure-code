class MonitorController < ApplicationController
  require 'open3'

  def commands
    filter_flags = params[:filter_flags] || 'aux'
    command_regex = params[:command_regex]

    if command_regex.blank?
      render json: { error: 'command_regex is required' }, status: :bad_request
      return
    end

    unless filter_flags.match?(/\A[a-zA-Z0-9\s-]+\z/)
      render json: { error: 'Invalid filter flags' }, status: :bad_request
      return
    end

    begin
      stdout, stderr, status = Open3.capture3('ps', *filter_flags.split)
      if status.success?
        processes = stdout.lines.map(&:strip).select { |line| line.match(/#{Regexp.escape(command_regex)}/) }
        process_list = processes.map do |process|
          parts = process.split
          { processId: parts[1].to_i, processString: process }
        end
        render json: process_list, status: :ok
      else
        render json: { error: stderr }, status: :internal_server_error
      end
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end
end