class LogsController < ApplicationController
  LOG_FILE = Rails.root.join('logs.txt')

  def create
    message = params.require(:message)
    log_message(message)
    render json: { status: 'success' }, status: :ok
  end

  def index
    logs = read_logs
    render plain: logs, status: :ok
  end

  private

  def log_message(message)
    File.open(LOG_FILE, 'a') do |file|
      file.puts(message)
    end
  end

  def read_logs
    File.exist?(LOG_FILE) ? File.read(LOG_FILE) : ''
  end
end