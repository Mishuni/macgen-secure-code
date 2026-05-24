class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]
    if valid_expression?(expression)
      result = evaluate_expression(expression)
      render json: { result: result.to_s }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  rescue StandardError => e
    handle_error(e)
  end

  private

  def valid_expression?(expression)
    expression.match?(/\A[\d\s+\-*/()]+\z/)
  end

  def evaluate_expression(expression)
    eval(expression)
  end
end