class MessagesController < ApplicationController
  def index
    limit = params.fetch(:limit, 10).to_i
    offset = params.fetch(:offset, 0).to_i
    sort_order = params.fetch(:sort, 'desc').upcase == 'ASC' ? :asc : :desc

    messages = Message.order(created_at: sort_order).limit(limit).offset(offset)
    render json: messages
  end

  def create
    message = Message.new(message_params)
    if message.save
      render json: message, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def message_params
    params.require(:message).permit(:content, :username)
  end
end