import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  calculate(expression: string): number {
    // Validate the input to ensure it only contains valid characters
    if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
      throw new Error('Invalid characters in expression');
    }

    try {
      // Use Function constructor to safely evaluate the expression
      // This ensures no arbitrary code execution
      const sanitizedExpression = expression.replace(/[^0-9+\-*/().\s]/g, '');
      const result = new Function(`return (${sanitizedExpression});`)();
      
      if (typeof result !== 'number' || isNaN(result)) {
        throw new Error('Invalid arithmetic expression');
      }

      return result;
    } catch (error) {
      throw new Error('Error evaluating expression: ' + error.message);
    }
  }
}