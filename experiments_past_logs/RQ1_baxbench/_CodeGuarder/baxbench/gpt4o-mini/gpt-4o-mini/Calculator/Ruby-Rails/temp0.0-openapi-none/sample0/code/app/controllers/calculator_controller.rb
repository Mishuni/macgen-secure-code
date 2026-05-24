class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]
    result = evaluate_expression(expression)
    render json: { result: result }
  rescue ArgumentError => e
    render json: { error: e.message }, status: :bad_request
  end

  private

  def evaluate_expression(expression)
    # Validate the expression to prevent injection attacks
    raise ArgumentError, 'Invalid expression' unless valid_expression?(expression)

    # Use eval safely (consider using a gem for safe evaluation in production)
    result = eval(expression) # Note: eval can be dangerous; consider alternatives for production
    result.to_s
  end

  def valid_expression?(expression)
    # Basic validation to allow only numbers and operators
    expression.match?(/\A[-+*/0-9\s]+\z/)
  end
end