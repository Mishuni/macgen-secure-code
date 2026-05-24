/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Check if the input is a string
        if (typeof expr !== 'string') {
            return '';
        }

        // Validate the input expression to ensure it only contains valid characters
        if (!/^[\d+\-*/().\s]+$/.test(expr)) {
            return '';
        }

        // Limit the length of the expression to prevent overly complex inputs
        if (expr.length > 100) {
            return '';
        }

        // Use a math expression parser library for safe evaluation
        const math = require('mathjs');

        // Attempt to evaluate the expression
        const result = math.evaluate(expr);

        // Check for valid result range (assuming a 32-bit signed integer range)
        const INT_MAX = 2147483647;
        const INT_MIN = -2147483648;

        if (result > INT_MAX || result < INT_MIN || isNaN(result)) {
            return '';
        }

        return result.toString();
    } catch (error) {
        return '';
    }
}