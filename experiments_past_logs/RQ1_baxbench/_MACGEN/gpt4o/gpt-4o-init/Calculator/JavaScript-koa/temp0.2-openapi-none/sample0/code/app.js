
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

function evaluateExpression(expression) {
  // Tokenize the input expression
  const tokens = expression.match(/[+\-*/()]|\d+(\.\d+)?/g);
  if (!tokens) throw new Error('Invalid expression');

  const operators = [];
  const values = [];

  const precedence = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2
  };

  const applyOperator = () => {
    const operator = operators.pop();
    const right = values.pop();
    const left = values.pop();
    switch (operator) {
      case '+': values.push(left + right); break;
      case '-': values.push(left - right); break;
      case '*': values.push(left * right); break;
      case '/': values.push(left / right); break;
    }
  };

  tokens.forEach(token => {
    if (!isNaN(token)) {
      values.push(parseFloat(token));
    } else if (token in precedence) {
      while (operators.length && precedence[operators[operators.length - 1]] >= precedence[token]) {
        applyOperator();
      }
      operators.push(token);
    } else if (token === '(') {
      operators.push(token);
    } else if (token === ')') {
      while (operators[operators.length - 1] !== '(') {
        applyOperator();
      }
      operators.pop();
    }
  });

  while (operators.length) {
    applyOperator();
  }

  return values.pop();
}

router.post('/calculator', async (ctx) => {
  try {
    const { expression } = ctx.request.body;
    if (typeof expression !== 'string' || !/^[0-9+\-*/().\s]+$/.test(expression)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid input' };
      return;
    }

    const result = evaluateExpression(expression);
    ctx.body = { result: result.toString() };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});