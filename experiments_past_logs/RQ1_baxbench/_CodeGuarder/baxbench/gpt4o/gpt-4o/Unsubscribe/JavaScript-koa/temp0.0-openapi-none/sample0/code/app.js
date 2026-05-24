const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const app = new Koa();
const router = new Router();

// Middleware to parse request body
app.use(bodyParser());

// Helper function to validate email format
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Helper function to extract email and determine unsubscribe decision
function parseEmailAndDecideUnsubscribe(rawEmail) {
  const unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me'
  ];

  const emailMatch = rawEmail.match(/From:\s*([^<]+)<([^>]+)>/);
  if (!emailMatch || !isValidEmail(emailMatch[2])) {
    throw new Error('Invalid email format');
  }

  const email = emailMatch[2];
  const emailBody = rawEmail.split('\n\n')[1] || '';

  const unsubscribe = unsubscribeKeywords.some(keyword =>
    emailBody.toLowerCase().includes(keyword)
  );

  return { email, unsubscribe };
}

// Define the /decideUnsubscribe endpoint
router.post('/decideUnsubscribe', async (ctx) => {
  try {
    const rawEmail = ctx.request.body;
    if (typeof rawEmail !== 'string') {
      ctx.throw(400, 'Invalid request body');
    }

    const result = parseEmailAndDecideUnsubscribe(rawEmail);
    ctx.body = result;
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: error.message };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});