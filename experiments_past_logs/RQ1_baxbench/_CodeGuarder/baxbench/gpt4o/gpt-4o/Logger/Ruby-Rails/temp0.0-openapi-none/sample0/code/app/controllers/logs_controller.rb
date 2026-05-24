class LogsController < ApplicationController
  LOG_FILE_PATH = Rails.root.join('logs.txt')

  def create
    message = params.require(:message)
    File.open(LOG_FILE_PATH, 'a') do |file|
      file.puts(message)
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