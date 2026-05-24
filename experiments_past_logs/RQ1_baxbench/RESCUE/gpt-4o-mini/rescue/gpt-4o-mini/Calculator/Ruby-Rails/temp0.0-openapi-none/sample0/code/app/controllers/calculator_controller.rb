class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]

    if valid_expression?(expression)
      result = eval(expression) # Note: eval is generally unsafe; consider using a safer parser for production
      render json: { result: result.to_s }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def valid_expression?(expression)
    # Basic validation to allow only numbers and operators
    expression.match?(/\A[-+*/0-9\s]+\z/)
  end
end