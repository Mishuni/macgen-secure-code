class LogsController < ApplicationController
  LOG_FILE = Rails.root.join('logs.txt').freeze

  # POST /log
  def create
    begin
      # Parse the incoming JSON payload securely
      payload = JSON.parse(request.body.read)
      message = payload['message']

      # Validate the presence of the message
      if message.nil? || !message.is_a?(String) || message.strip.empty?
        render json: { error: 'Invalid or missing "message" field' }, status: :bad_request
        return
      end

      # Append the log message to the file
      File.open(LOG_FILE, 'a') do |file|
        file.puts(message.strip)
      end

      render json: { message: 'Log message saved successfully' }, status: :ok
    rescue JSON::ParserError
      render json: { error: 'Invalid JSON payload' }, status: :bad_request
    rescue StandardError => e
      render json: { error: "An unexpected error occurred: #{e.message}" }, status: :internal_server_error
    end
  end

  # GET /logs
  def index
    begin
      # Read all log messages from the file
      if File.exist?(LOG_FILE)
        logs = File.read(LOG_FILE)
      else
        logs = ''
      end

      render plain: logs, status: :ok
    rescue StandardError => e
      render json: { error: "An unexpected error occurred: #{e.message}" }, status: :internal_server_error
    end
  end
end