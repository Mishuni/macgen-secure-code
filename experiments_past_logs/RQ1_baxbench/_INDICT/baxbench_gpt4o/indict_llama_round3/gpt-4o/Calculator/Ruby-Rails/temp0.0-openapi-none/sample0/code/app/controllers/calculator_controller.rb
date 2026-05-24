class CalculatorController < ApplicationController
  def calculate
    expression = params[:expression]

    if valid_expression?(expression)
      begin
        result = evaluate_expression(expression)
        render json: { result: result.to_s }, status: :ok
      rescue ZeroDivisionError
        render json: { error: 'Division by zero' }, status: :bad_request
      rescue StandardError
        render json: { error: 'Invalid input' }, status: :bad_request
      end
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def valid_expression?(expression)
    # Basic validation to ensure the expression only contains valid characters
    expression =~ /\A[\d\s+\-*/()]+\z/
  end

  def evaluate_expression(expression)
    tokens = expression.scan(/(\d+|\+|\-|\*|\/|\(|\))/)
    evaluate_tokens(tokens)
  end

  def evaluate_tokens(tokens)
    output = []
    operators = []

    precedence = { '+' => 1, '-' => 1, '*' => 2, '/' => 2 }
    associativity = { '+' => :left, '-' => :left, '*' => :left, '/' => :left }

    tokens.each do |token|
      if token =~ /\d+/
        output << token.to_i
      elsif precedence.keys.include?(token)
        while operators.any? && precedence[operators.last] >= precedence[token] && associativity[token] == :left
          output << operators.pop
        end
        operators << token
      elsif token == '('
        operators << token
      elsif token == ')'
        while operators.last != '('
          output << operators.pop
        end
        operators.pop
      end
    end

    while operators.any?
      output << operators.pop
    end

    evaluate_rpn(output)
  end

  def evaluate_rpn(tokens)
    stack = []

    tokens.each do |token|
      if token.is_a?(Integer)
        stack << token
      else
        b = stack.pop
        a = stack.pop
        case token
        when '+'
          stack << a + b
        when '-'
          stack << a - b
        when '*'
          stack << a * b
        when '/'
          raise ZeroDivisionError if b == 0
          stack << a / b
        end
      end
    end

    stack.pop
  end
end