class MessagesController < ApplicationController
  def index
    limit = params[:limit].to_i
    offset = params[:offset].to_i
    sort = params[:sort] || 'DESC'

    # Validate and sanitize inputs
    limit = [[limit, 100].min, 0].max
    offset = [offset, 0].max
    sort = %w[ASC DESC].include?(sort) ? sort : 'DESC'

    messages = Message.order(created_at: sort == 'ASC' ? :asc : :desc)
                      .limit(limit)
                      .offset(offset)

    render json: messages
  end

  def create
    message = Message.new(message_params)
    if message.save
      render json: { status: 'success' }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def message_params
    params.require(:message).permit(:content, :username)
  end
end