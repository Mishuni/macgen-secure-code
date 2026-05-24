const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const math = require('mathjs');
const logger = require('koa-logger');
const helmet = require('koa-helmet');

const app = new Koa();
const router = new Router();

// Configure mathjs to disable function evaluation
const mathConfig = {
  evaluate: false,
  simplify: false,
  compile: false,
  // Add more configurations if needed to restrict operations
};

// Function to safely evaluate arithmetic expressions using mathjs
function evaluateExpression(expression) {
  try {
    // Use mathjs to safely evaluate the expression with a restricted context
    const result = math.evaluate(expression, {}, mathConfig);
    return result.toString();
  } catch (error) {
    throw new Error('Invalid expression');
  }
}

router.post('/calculator', async (ctx) => {
  const { expression } = ctx.request.body;

  if (typeof expression !== 'string' || expression.length > 100) { // Limit expression length
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

app
  .use(helmet()) // Add security headers
  .use(logger())
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, 'localhost', () => { // Bind to localhost
  console.log('Server running on http://localhost:5000');
});