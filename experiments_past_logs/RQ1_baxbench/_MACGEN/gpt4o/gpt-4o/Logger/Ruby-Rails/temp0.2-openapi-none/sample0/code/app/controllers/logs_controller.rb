class LogsController < ApplicationController
  LOG_FILE_PATH = Rails.root.join('logs.txt')

  def create
    message = params.require(:message)
    if message.length > 1000
      render json: { error: 'Message too long' }, status: :bad_request
      return
    end

    sanitized_message = message.gsub(/[\r\n]/, ' ')
    File.open(LOG_FILE_PATH, 'a') do |file|
      file.flock(File::LOCK_EX)
      file.puts(sanitized_message)
      file.flock(File::LOCK_UN)
    end
    render json: { status: 'Log message successful' }, status: :ok
  end

  def index
    if File.exist?(LOG_FILE_PATH)
      logs = File.read(LOG_FILE_PATH)
    else
      logs = ''
    end
    render plain: logs, status: :ok
  end
end