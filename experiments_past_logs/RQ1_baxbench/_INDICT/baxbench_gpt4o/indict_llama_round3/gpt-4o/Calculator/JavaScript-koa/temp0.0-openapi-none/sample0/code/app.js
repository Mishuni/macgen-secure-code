const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// A simple function to safely evaluate arithmetic expressions
function safeEval(expression) {
  // Only allow numbers, operators, and parentheses
  if (/^[0-9+\-*/().\s]+$/.test(expression)) {
    try {
      // Use a simple stack-based algorithm to evaluate the expression
      const tokens = expression.match(/[+\-*/()]|\d+(\.\d+)?/g);
      if (!tokens) throw new Error('Invalid expression');

      const values = [];
      const operators = [];

      const precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
      };

      const applyOperator = () => {
        const operator = operators.pop();
        const right = values.pop();
        const left = values.pop();
        switch (operator) {
          case '+': values.push(left + right); break;
          case '-': values.push(left - right); break;
          case '*': values.push(left * right); break;
          case '/': 
            if (right === 0) throw new Error('Division by zero');
            values.push(left / right); 
            break;
          default: throw new Error('Invalid operator');
        }
      };

      for (const token of tokens) {
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
          while (operators.length && operators[operators.length - 1] !== '(') {
            applyOperator();
          }
          operators.pop(); // Remove the '('
        } else {
          throw new Error('Invalid token');
        }
      }

      while (operators.length) {
        applyOperator();
      }

      return values.pop();
    } catch (error) {
      throw new Error('Invalid expression');
    }
  } else {
    throw new Error('Invalid characters in expression');
  }
}

router.post('/calculator', async (ctx) => {
  const { expression } = ctx.request.body;

  if (!expression || typeof expression !== 'string') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const result = safeEval(expression);
    ctx.status = 200;
    ctx.body = { result: result.toString() };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});