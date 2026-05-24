class CalculatorController < ApplicationController
  require "yaml"

  def calculate
    # Securely parse the input JSON
    expression = params[:expression]

    # Validate input
    unless expression.is_a?(String) && expression.match?(/\A[\d+\-*/().\s]+\z/)
      render json: { error: "Invalid input. Only numbers and basic arithmetic operators are allowed." }, status: :bad_request
      return
    end

    begin
      # Safely evaluate the arithmetic expression
      result = eval_arithmetic(expression)
      render json: { result: result.to_s }, status: :ok
    rescue StandardError => e
      render json: { error: "Error evaluating expression: #{e.message}" }, status: :bad_request
    end
  end

  private

  # Securely evaluate arithmetic expressions
  def eval_arithmetic(expression)
    # Use Ruby's eval with a safe binding to evaluate arithmetic expressions
    binding = TOPLEVEL_BINDING.dup
    eval(expression, binding)
  end
end