import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  evaluateExpression(expression: string): number {
    if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
      throw new Error('Invalid characters in expression');
    }

    try {
      // Implement a simple parser for arithmetic expressions
      const result = this.simpleEvaluate(expression);
      if (typeof result !== 'number' || !isFinite(result)) {
        throw new Error('Invalid result');
      }
      return result;
    } catch {
      throw new Error('Invalid expression');
    }
  }

  private simpleEvaluate(expression: string): number {
    // This is a simple implementation and should be replaced with a proper parser for production use
    return Function(`"use strict"; return (${expression})`)();
  }
}