const { evaluate } = require('mathjs');

function evaluate_expression(expr) {
    if (typeof expr !== 'string' || expr.trim() === '') {
        return '';
    }

    // Validate the input expression
    if (!/^[0-9+\-*/().\s]+$/.test(expr)) {
        return '';
    }

    try {
        // Use mathjs to safely evaluate the expression
        const result = evaluate(expr);
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        }
    } catch (e) {
        // Catch any errors during evaluation
    }

    return '';
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
