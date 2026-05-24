
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Use a safe parser to evaluate the expression instead of eval
        const result = safeEvaluate(expr);
        return result.toString();
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}

/**
 * Safely evaluates a mathematical expression.
 * This function should be implemented to parse and evaluate the expression
 * without using eval, ensuring that only safe arithmetic operations are allowed.
 *
 * @param {string} expression - The arithmetic expression to evaluate.
 * @returns {number} The result of the evaluated expression.
 */
function safeEvaluate(expression) {
    // Implement a simple parser or use a library to safely evaluate the expression
    // For demonstration, using a simple implementation that only allows basic arithmetic
    const allowedCharacters = /^[0-9+\-*/().\s]+$/;
    if (!allowedCharacters.test(expression)) {
        throw new Error('Invalid characters in expression');
    }

    // Use Function constructor in a controlled manner
    const sanitizedExpression = expression.replace(/[^0-9+\-*/().]/g, '');
    const func = new Function(`return (${sanitizedExpression})`);
    return func();
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
