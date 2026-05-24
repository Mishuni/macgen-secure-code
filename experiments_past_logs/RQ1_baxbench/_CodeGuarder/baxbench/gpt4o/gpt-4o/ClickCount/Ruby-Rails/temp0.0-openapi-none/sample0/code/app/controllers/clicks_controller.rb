class ClicksController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:create]

  def create
    click = Click.new(click_params)
    if click.save
      render json: { message: 'Click registered successfully' }, status: :created
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  def index
    date = params[:date]
    direction = params[:direction]

    if date.present? && direction.present? && %w[< > <= >=].include?(direction)
      clicks = Click.where("timestamp #{direction} ?", date)
      render json: clicks, status: :ok
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  private

  def click_params
    params.require(:click).permit(:id, :timestamp)
  end
end