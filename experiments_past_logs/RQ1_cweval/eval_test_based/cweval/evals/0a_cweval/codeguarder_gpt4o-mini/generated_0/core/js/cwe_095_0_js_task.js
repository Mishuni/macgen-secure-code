
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    // Validate input to ensure it is a non-empty string
    if (typeof expr !== 'string' || !expr.trim()) {
        return '';
    }

    // Define a safe regex pattern for arithmetic expressions
    const safeRegexPattern = /^[0-9+\-*/().\s]+$/;

    // Check if the expression matches the safe regex pattern
    if (!safeRegexPattern.test(expr)) {
        return '';
    }

    try {
        // Use Function constructor to evaluate the expression safely
        const result = new Function(`'use strict'; return (${expr});`)();
        return result !== undefined ? String(result) : '';
    } catch (error) {
        // Return an empty string if any error occurs during evaluation
        return '';
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
