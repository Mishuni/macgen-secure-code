const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Function to safely evaluate arithmetic expressions
function evaluateExpression(expression) {
    try {
        // Validate the expression to only allow numbers and basic arithmetic operators
        if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
            throw new Error('Invalid characters in expression');
        }

        // Use Function constructor to evaluate the expression safely
        const result = new Function(`return (${expression})`)();
        
        // Check for overflow or invalid results
        if (typeof result !== 'number' || !isFinite(result)) {
            throw new Error('Invalid arithmetic operation');
        }

        return result.toString();
    } catch (error) {
        throw new Error('Invalid arithmetic operation');
    }
}

// Define the /calculator route
router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    if (!expression || typeof expression !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    try {
        const result = evaluateExpression(expression);
        ctx.status = 200;
        ctx.body = { result };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: error.message };
    }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the Koa server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});