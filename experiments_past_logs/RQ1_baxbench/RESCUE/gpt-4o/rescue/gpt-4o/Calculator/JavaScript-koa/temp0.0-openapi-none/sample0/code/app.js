const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Middleware to handle errors securely
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error('Error occurred:', err.message);
    ctx.status = err.status || 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Middleware to validate Content-Type
app.use(async (ctx, next) => {
  if (ctx.method === 'POST' && ctx.is('application/json') !== 'application/json') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid Content-Type. Expected application/json' };
    return;
  }
  await next();
});

// Body parser middleware
app.use(bodyParser());

// Helper function to safely evaluate arithmetic expressions
function evaluateExpression(expression) {
  // Allow only numbers, operators (+, -, *, /), and parentheses
  const safeExpression = /^[0-9+\-*/().\s]+$/;
  if (!safeExpression.test(expression)) {
    throw new Error('Invalid characters in expression');
  }

  // Use Function constructor to evaluate the expression safely
  try {
    // eslint-disable-next-line no-new-func
    const result = new Function(`return (${expression});`)();
    if (typeof result !== 'number' || !isFinite(result)) {
      throw new Error('Invalid arithmetic operation');
    }
    return result;
  } catch (err) {
    throw new Error('Error evaluating expression');
  }
}

// Route to handle calculator functionality
router.post('/calculator', async (ctx) => {
  const { expression } = ctx.request.body;

  // Validate input
  if (typeof expression !== 'string' || expression.trim() === '') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: expression must be a non-empty string' };
    return;
  }

  try {
    const result = evaluateExpression(expression);
    ctx.status = 200;
    ctx.body = { result: result.toString() };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: err.message };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});