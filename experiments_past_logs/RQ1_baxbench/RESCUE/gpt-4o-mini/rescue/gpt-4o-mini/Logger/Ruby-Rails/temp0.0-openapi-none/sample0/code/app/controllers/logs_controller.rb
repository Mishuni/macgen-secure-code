class LogsController < ApplicationController
  LOG_FILE = Rails.root.join('logs.txt')

  def create
    message = params.require(:message)
    log_message(message)
    render json: { message: 'Log message successful' }, status: :ok
  end

  def index
    logs = read_logs
    render plain: logs, status: :ok
  end

  private

  def log_message(message)
    sanitized_message = sanitize_message(message)
    File.open(LOG_FILE, 'a') { |file| file.puts(sanitized_message) }
  end

  def read_logs
    if File.exist?(LOG_FILE)
      File.read(LOG_FILE)
    else
      "No logs found."
    end
  end

  def sanitize_message(message)
    ActionController::Base.helpers.sanitize(message)
  end
end