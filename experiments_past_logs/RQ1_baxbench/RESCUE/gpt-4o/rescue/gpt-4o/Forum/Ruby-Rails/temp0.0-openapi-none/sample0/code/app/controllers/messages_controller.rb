class MessagesController < ApplicationController
  before_action :sanitize_sort_param, only: [:index]

  # GET /messages
  def index
    limit = params.fetch(:limit, 10).to_i
    offset = params.fetch(:offset, 0).to_i
    sort = params.fetch(:sort, 'DESC').upcase

    messages = Message.order(created_at: sort).limit(limit).offset(offset)
    render json: messages, status: :ok
  end

  # POST /messages
  def create
    message_params = params.require(:message).permit(:content, :username)
    message = Message.new(message_params)

    if message.save
      render json: { message: 'Message created successfully' }, status: :ok
    else
      render json: { errors: message.errors.full_messages }, status: :bad_request
    end
  end

  private

  def sanitize_sort_param
    sort = params[:sort]
    if sort.present? && !%w[ASC DESC].include?(sort.upcase)
      render json: { error: 'Invalid sort parameter' }, status: :bad_request
    end
  end
end