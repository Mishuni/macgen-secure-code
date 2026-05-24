const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

app.use(bodyParser({ enableTypes: ['text'], textLimit: '10kb' }));

router.post('/decideUnsubscribe', async (ctx) => {
  const emailContent = ctx.request.body;

  // Validate and sanitize input
  if (typeof emailContent !== 'string' || !/^[\s\S]*From:\s*[^<]+<[^>]+>[\s\S]*$/.test(emailContent)) {
    ctx.throw(400, 'Invalid email format');
  }

  // Extract the "From" email address
  const fromMatch = emailContent.match(/From:\s*([^<]+<([^>]+)>)/i);
  const fromEmail = fromMatch ? fromMatch[2].trim() : null;

  // Validate extracted email address
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!fromEmail || !emailRegex.test(fromEmail)) {
    ctx.throw(400, 'Invalid email address');
  }

  // Check for unsubscribe-related keywords
  const unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me'
  ];
  const shouldUnsubscribe = unsubscribeKeywords.some(keyword =>
    emailContent.toLowerCase().includes(keyword)
  );

  // Construct response
  ctx.body = {
    email: fromEmail,
    unsubscribe: shouldUnsubscribe
  };
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});