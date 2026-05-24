class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]
    if valid_expression?(expression)
      begin
        result = evaluate_expression(expression)
        render json: { result: result.to_s }, status: :ok
      rescue StandardError
        render json: { error: 'Invalid input' }, status: :bad_request
      end
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def valid_expression?(expression)
    expression.match?(/^[0-9+\-*/\s]+$/)
  end

  def evaluate_expression(expression)
    # A simple and safe evaluation using Ruby's eval with basic arithmetic operations
    # This assumes the input is already validated to contain only safe characters
    eval(expression)
  end
end