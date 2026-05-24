class LogsController < ApplicationController
  LOG_FILE = Rails.root.join('logs.txt')

  def create
    message = params[:message]

    # Validate input
    if message.blank?
      render json: { error: 'Message cannot be blank' }, status: :unprocessable_entity
      return
    end

    # Sanitize input to prevent injection attacks
    sanitized_message = message.gsub(/[^0-9A-Za-z\s\.\,\!\?]/, '')

    # Use a mutex to prevent concurrent writes to the log file
    mutex = Mutex.new
    mutex.synchronize do
      begin
        File.open(LOG_FILE, 'a') { |f| f.puts(sanitized_message) }
        render json: { status: 'success' }, status: :ok
      rescue => e
        render json: { error: 'Failed to log message', details: e.message }, status: :internal_server_error
      end
    end
  end

  def index
    if File.exist?(LOG_FILE)
      logs = File.read(LOG_FILE)
      render plain: logs, status: :ok
    else
      render plain: 'No logs found', status: :ok
    end
  end
end