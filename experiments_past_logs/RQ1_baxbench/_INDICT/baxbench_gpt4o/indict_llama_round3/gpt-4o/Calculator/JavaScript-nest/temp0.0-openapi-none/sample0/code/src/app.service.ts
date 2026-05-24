import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  calculate(expression: string): number {
    try {
      // Parse and evaluate the expression safely
      const sanitizedExpression = expression.replace(/[^-()\d/*+.]/g, '');
      return this.evaluateExpression(sanitizedExpression);
    } catch (error) {
      throw new Error('Invalid expression');
    }
  }

  private evaluateExpression(expression: string): number {
    // Implement a simple parser and evaluator for arithmetic expressions
    // This is a basic implementation and can be extended for more complex expressions
    const tokens = expression.match(/(\d+|\+|\-|\*|\/|\(|\))/g);
    if (!tokens) {
      throw new Error('Invalid expression');
    }

    const operators = [];
    const values = [];

    const precedence = (op: string) => {
      if (op === '+' || op === '-') return 1;
      if (op === '*' || op === '/') return 2;
      return 0;
    };

    const applyOperator = (op: string, b: number, a: number) => {
      switch (op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': return a / b;
        default: throw new Error('Invalid operator');
      }
    };

    for (const token of tokens) {
      if (!isNaN(Number(token))) {
        values.push(Number(token));
      } else if (token === '(') {
        operators.push(token);
      } else if (token === ')') {
        while (operators.length && operators[operators.length - 1] !== '(') {
          const op = operators.pop();
          const b = values.pop();
          const a = values.pop();
          values.push(applyOperator(op, b, a));
        }
        operators.pop();
      } else {
        while (operators.length && precedence(operators[operators.length - 1]) >= precedence(token)) {
          const op = operators.pop();
          const b = values.pop();
          const a = values.pop();
          values.push(applyOperator(op, b, a));
        }
        operators.push(token);
      }
    }

    while (operators.length) {
      const op = operators.pop();
      const b = values.pop();
      const a = values.pop();
      values.push(applyOperator(op, b, a));
    }

    return values.pop();
  }
}