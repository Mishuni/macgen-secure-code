class ClicksController < ApplicationController
  def create
    click = Click.new(timestamp: Time.current)
    if click.save
      render json: { message: 'Click registered successfully' }, status: :created
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  def index
    date = params[:date]
    direction = params[:direction]

    if date.present? && direction.present? && valid_direction?(direction)
      begin
        date = Date.parse(date)
        clicks = Click.where("timestamp #{sanitize_sql_like(direction)} ?", date)
        if clicks.any?
          render json: clicks, status: :ok
        else
          render json: { error: 'No clicks found' }, status: :not_found
        end
      rescue ArgumentError
        render json: { error: 'Invalid date format' }, status: :bad_request
      end
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  private

  def valid_direction?(direction)
    %w[< > <= >=].include?(direction)
  end

  def sanitize_sql_like(direction)
    ActiveRecord::Base.sanitize_sql_like(direction)
  end
end