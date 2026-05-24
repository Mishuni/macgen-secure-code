
// Import the math.js library
const math = require('mathjs');

/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Use math.js to safely parse and evaluate the expression
        const result = math.evaluate(expr);
        
        // Check if the result is a finite number
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}