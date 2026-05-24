class LogsController < ApplicationController
  LOG_FILE = 'logs.txt'

  def create
    # Enhanced sanitization to prevent log injection attacks
    message = params.require(:message).gsub(/[^\w\s]/, '').gsub(/[\n\r]/, '')[0...256]
    File.open(LOG_FILE, 'a') do |f|
      f.puts(message)
      f.chmod(0600) unless File.exist?(LOG_FILE) # Set permissions only if the file is created
    end
    render json: { status: 'Log message successful' }, status: :ok
  end

  def index
    logs = File.exist?(LOG_FILE) ? File.read(LOG_FILE) : ''
    render plain: logs, status: :ok
  end
end