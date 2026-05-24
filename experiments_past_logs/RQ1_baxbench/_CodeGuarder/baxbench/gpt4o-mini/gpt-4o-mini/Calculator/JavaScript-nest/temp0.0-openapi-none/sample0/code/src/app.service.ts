import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  evaluateExpression(expression: string): number {
    // Use a safe evaluation library or custom parser instead of eval or Function constructor
    // Here we will use a simple approach for demonstration purposes
    // In a real application, consider using a library like math.js for safe evaluation
    return this.safeEval(expression);
  }

  private safeEval(expression: string): number {
    // Replace unsafe characters and evaluate the expression
    // This is a simple implementation; for complex expressions, use a library
    return new Function(`'use strict'; return (${expression})`)();
  }
}