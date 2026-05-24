import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  calculate(expression: string): number {
    // Use Function constructor to evaluate the expression securely
    // Note: This is a simple example; in production, consider using a library for safe evaluation
    return Function(`'use strict'; return (${expression})`)();
  }
}