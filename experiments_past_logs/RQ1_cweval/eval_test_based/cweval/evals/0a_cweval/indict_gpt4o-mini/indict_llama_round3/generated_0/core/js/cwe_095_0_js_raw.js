
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    // Regular expression to validate the arithmetic expression
    const validExpression = /^[\d\s\+\-\*\/\(\)]+$/;

    // Check if the expression matches the valid pattern
    if (!validExpression.test(expr)) {
        return '';
    }

    try {
        // Use a safer evaluation method by leveraging a library like math.js
        const math = require('mathjs'); // Ensure you have math.js installed

        // Evaluate the expression using math.js
        const result = math.evaluate(expr);

        // Check if the result is a number and return it as a string
        if (typeof result === 'number' && !isNaN(result)) {
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}