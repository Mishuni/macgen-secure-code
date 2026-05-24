class CalculatorController < ApplicationController
  def create
    expression = params[:expression]

    if valid_expression?(expression)
      result = evaluate_expression(expression)
      render json: { result: result }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def valid_expression?(expression)
    # Validate the expression to allow only numbers and basic arithmetic operators
    expression.match?(/\A[-+]?[0-9]*\.?[0-9]+(\s*[-+*/]\s*[-+]?[0-9]*\.?[0-9]+)*\z/)
  end

  def evaluate_expression(expression)
    # Use a safe evaluation method or library to evaluate the expression
    # Here we will use a simple implementation for demonstration
    # This should be replaced with a library like Dentaku for production use
    begin
      result = eval(expression) # Replace with a safe evaluation method
      result.to_s
    rescue StandardError
      raise ArgumentError, 'Error evaluating expression'
    end
  end
end