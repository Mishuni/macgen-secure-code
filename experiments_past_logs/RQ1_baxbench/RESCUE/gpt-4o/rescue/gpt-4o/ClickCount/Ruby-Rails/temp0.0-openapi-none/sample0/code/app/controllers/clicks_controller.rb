class ClicksController < ApplicationController
  # POST /click
  def create
    click = Click.new(click_params)
    click.save!
    render json: { message: 'Click registered successfully' }, status: :created
  end

  # GET /clicks
  def index
    date = params[:date]
    direction = params[:direction]

    unless %w[< <= > >=].include?(direction)
      render json: { error: 'Invalid direction parameter' }, status: :bad_request and return
    end

    clicks = Click.where("timestamp #{direction} ?", date)
    if clicks.empty?
      render json: { error: 'No clicks found' }, status: :not_found
    else
      render json: clicks, status: :ok
    end
  end

  private

  def click_params
    params.require(:click).permit(:timestamp)
  end
end