class ClicksController < ApplicationController
  def create
    click = Click.new(timestamp: Time.now)
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
      if clicks.any?
        render json: clicks, status: :ok
      else
        render json: { error: 'No clicks found' }, status: :not_found
      end
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end
end