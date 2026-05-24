import { Injectable } from '@nestjs/common';
import { evaluate } from 'mathjs';

@Injectable()
export class AppService {
  calculate(expression: string): number {
    // Use mathjs to safely evaluate the expression
    return evaluate(expression);
  }
}