class MessagesController < ApplicationController
  before_action :validate_csrf_token, only: [:create]

  def index
    limit = params.fetch(:limit, 10).to_i
    offset = params.fetch(:offset, 0).to_i
    sort_order = params.fetch(:sort, 'desc').upcase

    messages = Message.order(created_at: sort_order).limit(limit).offset(offset)
    render json: messages
  end

  def create
    message = Message.new(message_params)
    if message.save
      render json: message, status: :created
    else
      render json: message.errors, status: :unprocessable_entity
    end
  end

  private

  def message_params
    params.require(:message).permit(:content, :username)
  end

  def validate_csrf_token
    unless request.headers['X-CSRF-Token'] == ENV['APP_SECRET']
      render json: { error: 'Invalid CSRF token' }, status: :forbidden
    end
  end
end