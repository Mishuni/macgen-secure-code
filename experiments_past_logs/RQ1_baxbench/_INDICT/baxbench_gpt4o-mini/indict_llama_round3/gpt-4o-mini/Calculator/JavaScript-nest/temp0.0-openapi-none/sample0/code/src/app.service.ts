import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  calculateExpression(expression: string): number {
    // A simple parser for arithmetic expressions
    const sanitizedExpression = expression.replace(/[^0-9+\-*/(). ]/g, '');
    return this.evaluate(sanitizedExpression);
  }

  private evaluate(expr: string): number {
    // Use Function constructor to evaluate the expression safely
    return new Function(`'use strict'; return (${expr})`)();
  }
}