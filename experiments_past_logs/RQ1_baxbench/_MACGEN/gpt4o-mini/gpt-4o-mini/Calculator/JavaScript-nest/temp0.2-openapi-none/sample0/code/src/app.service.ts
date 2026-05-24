import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  calculate(expression: string): number {
    // A simple parser for arithmetic expressions
    const safeEval = (expr: string): number => {
      const tokens = expr.match(/(\d+|[-+*/()])/g);
      if (!tokens) throw new Error('Invalid expression');

      const output: number[] = [];
      const operators: string[] = [];
      const precedence: { [key: string]: number } = { '+': 1, '-': 1, '*': 2, '/': 2 };

      const applyOperator = () => {
        const b = output.pop()!;
        const a = output.pop()!;
        const op = operators.pop()!;
        switch (op) {
          case '+': output.push(a + b); break;
          case '-': output.push(a - b); break;
          case '*': output.push(a * b); break;
          case '/': output.push(a / b); break;
        }
      };

      for (const token of tokens) {
        if (!isNaN(Number(token))) {
          output.push(Number(token));
        } else if (token in precedence) {
          while (operators.length && precedence[operators[operators.length - 1]] >= precedence[token]) {
            applyOperator();
          }
          operators.push(token);
        } else if (token === '(') {
          operators.push(token);
        } else if (token === ')') {
          while (operators.length && operators[operators.length - 1] !== '(') {
            applyOperator();
          }
          operators.pop(); // Remove '('
        }
      }

      while (operators.length) {
        applyOperator();
      }

      return output[0];
    };

    return safeEval(expression);
  }
}