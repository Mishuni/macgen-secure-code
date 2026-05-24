class LogsController < ApplicationController
  LOG_FILE_PATH = Rails.root.join('logs.txt')

  def create
    message = params.require(:message).to_s.strip
    if message.empty?
      render json: { error: 'Message cannot be empty' }, status: :unprocessable_entity
    else
      begin
        File.open(LOG_FILE_PATH, 'a') do |file|
          file.puts(message)
        end
        render json: { status: 'Log message successful' }, status: :ok
      rescue => e
        render json: { error: 'Failed to write log message', details: e.message }, status: :internal_server_error
      end
    end
  end

  def index
    begin
      logs = File.exist?(LOG_FILE_PATH) ? File.read(LOG_FILE_PATH) : ''
      render plain: logs, status: :ok
    rescue => e
      render json: { error: 'Failed to read log messages', details: e.message }, status: :internal_server_error
    end
  end
end