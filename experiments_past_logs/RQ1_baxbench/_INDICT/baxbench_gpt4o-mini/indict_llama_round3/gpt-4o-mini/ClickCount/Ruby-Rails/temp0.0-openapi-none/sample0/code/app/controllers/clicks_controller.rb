class ClicksController < ApplicationController
  def create
    click = Click.new(timestamp: Time.current)
    if click.save
      render json: { id: click.id, timestamp: click.timestamp }, status: :created
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  def index
    date = params[:date]
    direction = params[:direction]

    if date.blank? || direction.blank? || !valid_date?(date) || !valid_direction?(direction)
      render json: { error: 'Invalid request' }, status: :bad_request and return
    end

    operator = direction
    clicks = Click.where("timestamp #{operator} ?", DateTime.parse(date))

    if clicks.any?
      render json: clicks, status: :ok
    else
      render json: { error: 'No clicks found' }, status: :not_found
    end
  end

  private

  def valid_date?(date)
    DateTime.parse(date) rescue false
  end

  def valid_direction?(direction)
    %w[< <= > >=].include?(direction)
  end
end