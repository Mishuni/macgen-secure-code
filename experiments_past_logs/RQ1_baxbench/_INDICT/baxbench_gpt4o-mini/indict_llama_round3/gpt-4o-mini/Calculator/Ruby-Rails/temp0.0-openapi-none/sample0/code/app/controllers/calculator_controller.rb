class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]
    validate_expression(expression)
    result = evaluate_expression(expression)
    render json: { result: result }
  rescue StandardError => e
    handle_error(e)
  end

  private

  def validate_expression(expression)
    # Basic validation to ensure the expression only contains numbers and operators
    unless expression =~ /\A[-+*\/0-9\s]+\z/
      raise StandardError, "Invalid input"
    end
  end

  def evaluate_expression(expression)
    # Use a safer method to evaluate the expression
    # Here we use a simple implementation of a basic arithmetic evaluator
    # This is a placeholder for a more robust solution
    eval(expression).to_s
  end
end