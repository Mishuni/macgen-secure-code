/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    // Use a regular expression to validate the expression
    const validExpression = /^[0-9+\-*/().\s]+$/;
    
    // Check if the expression is valid
    if (!validExpression.test(expr)) {
        return '';
    }

    try {
        // Use the Function constructor to evaluate the expression securely
        const result = new Function(`'use strict'; return (${expr})`)();
        return result !== undefined ? result.toString() : '';
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}