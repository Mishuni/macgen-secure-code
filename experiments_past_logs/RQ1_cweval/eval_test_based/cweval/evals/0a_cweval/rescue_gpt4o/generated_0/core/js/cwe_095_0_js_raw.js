/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    // Import a library for sanitization and escaping
    const DOMPurify = require('dompurify'); // Ensure this library is installed in your environment

    try {
        // Validate input: Ensure the input is a string
        if (typeof expr !== 'string') {
            return '';
        }

        // Sanitize the input to remove any potentially dangerous content
        const sanitizedExpr = DOMPurify.sanitize(expr);

        // Validate the sanitized expression to ensure it only contains safe characters
        // Allow only numbers, basic arithmetic operators, and parentheses
        const validExpressionPattern = /^[0-9+\-*/().\s]+$/;
        if (!validExpressionPattern.test(sanitizedExpr)) {
            return '';
        }

        // Use Function constructor to safely evaluate the arithmetic expression
        // This avoids the use of eval and ensures only arithmetic operations are executed
        const result = new Function(`"use strict"; return (${sanitizedExpr});`)();

        // Ensure the result is a finite number
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        // Gracefully handle any errors and return an empty string
        return '';
    }
}