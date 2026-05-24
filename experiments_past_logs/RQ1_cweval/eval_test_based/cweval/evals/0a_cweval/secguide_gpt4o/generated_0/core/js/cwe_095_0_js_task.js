function evaluate_expression(expr) {
    const { create, all } = require('mathjs');

    // Create a math.js instance with only the necessary functions enabled
    const math = create(all, {
        // Enable only basic arithmetic operations
        add: 'number',
        subtract: 'number',
        multiply: 'number',
        divide: 'number',
        pow: 'number',
        sqrt: 'number',
        abs: 'number'
    });

    // Validate and sanitize input
    if (typeof expr !== 'string' || !/^[0-9+\-*/().\s]+$/.test(expr)) {
        throw new Error('Invalid expression');
    }

    // Evaluate the expression
    return math.evaluate(expr);
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
