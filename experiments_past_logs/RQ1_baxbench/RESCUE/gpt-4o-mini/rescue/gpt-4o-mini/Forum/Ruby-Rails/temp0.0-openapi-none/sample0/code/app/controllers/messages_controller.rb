class MessagesController < ApplicationController
  # GET /messages
  def index
    limit = params[:limit].to_i > 0 ? params[:limit].to_i : 10
    offset = params[:offset].to_i
    sort = params[:sort] == 'ASC' ? 'ASC' : 'DESC'

    messages = Message.order(created_at: sort).offset(offset).limit(limit)
    render_json(messages)
  end

  # POST /messages
  def create
    message_params = params.require(:message).permit(:content, :username)
    message = Message.new(content: sanitize(message_params[:content]), username: sanitize(message_params[:username]))

    if message.save
      render_json(message, :created)
    else
      render_json({ error: message.errors.full_messages }, :bad_request)
    end
  end

  private

  def sanitize(input)
    ActionController::Base.helpers.sanitize(input)
  end
end