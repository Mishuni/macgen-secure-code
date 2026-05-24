class ClicksController < ApplicationController
  def create
    click = Click.create!(click_params)
    render json: { id: click.id, timestamp: click.timestamp }, status: :created
  end

  def index
    date = params.require(:date)
    direction = params.require(:direction)

    validate_direction(direction)

    clicks = Click.where("timestamp #{direction} ?", Date.parse(date).beginning_of_day)
    if clicks.empty?
      render json: { error: 'No clicks found' }, status: :not_found
    else
      render json: clicks, status: :ok
    end
  end

  private

  def click_params
    params.permit(:timestamp)
  end

  def validate_direction(direction)
    raise ArgumentError unless ["<", ">", "<=", ">="].include?(direction)
  end
end