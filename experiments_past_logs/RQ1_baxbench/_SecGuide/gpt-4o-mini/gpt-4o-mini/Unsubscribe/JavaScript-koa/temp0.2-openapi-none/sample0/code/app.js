const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const validator = require('validator');

const app = new Koa();
const router = new Router();

// Keywords indicating an unsubscribe request
const unsubscribeKeywords = [
  "unsubscribe",
  "remove me",
  "deregister me",
  "stop sending me",
  "delete me"
];

// Function to check if the email content contains unsubscribe keywords
const shouldUnsubscribe = (emailContent) => {
  return unsubscribeKeywords.some(keyword => 
    emailContent.toLowerCase().includes(keyword)
  );
};

// Endpoint to decide whether to unsubscribe
router.post('/decideUnsubscribe', async (ctx) => {
  const emailContent = ctx.request.body;

  // Validate input type and length
  if (typeof emailContent !== 'string' || emailContent.length > 1000) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input, expected plain text email content.' };
    return;
  }

  // Sanitize the email content to prevent XSS
  const sanitizedEmailContent = validator.escape(emailContent);

  // Extract email address from the "From" field in the email content
  const fromMatch = sanitizedEmailContent.match(/From:\s*([^<>\s]+@[^<>\s]+)/);
  const emailAddress = fromMatch ? fromMatch[1] : null;

  if (!emailAddress || !validator.isEmail(emailAddress)) {
    ctx.status = 400;
    ctx.body = { error: 'Valid email address not found in the content.' };
    return;
  }

  const unsubscribe = shouldUnsubscribe(sanitizedEmailContent);

  ctx.status = 200;
  ctx.body = {
    email: emailAddress,
    unsubscribe: unsubscribe
  };
});

// Middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// CORS configuration
app.use(async (ctx, next) => {
  ctx.set('Access-Control-Allow-Origin', '*');
  ctx.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  ctx.set('Access-Control-Allow-Headers', 'Content-Type');
  await next();
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});