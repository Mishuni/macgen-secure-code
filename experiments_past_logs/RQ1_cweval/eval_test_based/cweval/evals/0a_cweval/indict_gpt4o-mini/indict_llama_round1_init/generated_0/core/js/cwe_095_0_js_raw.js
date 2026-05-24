
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Use the Function constructor to evaluate the expression safely
        const result = new Function(`'use strict'; return (${expr})`)();
        // Check if the result is a number and return it as a string
        if (typeof result === 'number') {
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}