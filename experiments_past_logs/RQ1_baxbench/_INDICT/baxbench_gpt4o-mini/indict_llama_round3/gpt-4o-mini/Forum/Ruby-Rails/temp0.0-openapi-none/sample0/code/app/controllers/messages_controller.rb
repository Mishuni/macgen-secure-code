class MessagesController < ApplicationController
  # GET /messages
  def index
    limit = params[:limit].to_i
    offset = params[:offset].to_i
    sort = params[:sort].upcase if params[:sort].present?

    # Validate sort parameter
    sort = %w[ASC DESC].include?(sort) ? sort : 'DESC'

    # Ensure limit and offset are non-negative
    limit = limit.positive? ? limit : 10
    offset = offset.positive? ? offset : 0

    @messages = Message.order(created_at: sort == 'ASC' ? :asc : :desc)
                       .limit(limit)
                       .offset(offset)

    render json: @messages
  end

  # POST /messages
  def create
    @message = Message.new(message_params)

    if @message.save
      render json: @message, status: :created
    else
      render json: @message.errors, status: :unprocessable_entity
    end
  end

  private

  def message_params
    params.require(:message).permit(:content, :username)
  end
end