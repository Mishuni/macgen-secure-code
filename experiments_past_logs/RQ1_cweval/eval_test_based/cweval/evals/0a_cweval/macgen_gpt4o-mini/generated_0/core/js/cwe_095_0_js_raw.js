function evaluate_expression(expr) {
    const MAX_LENGTH = 100;
    if (expr.length > MAX_LENGTH || !/^[\d+\-*/().\s]+$/.test(expr)) return '';

    const isOperator = (c) => ['+', '-', '*', '/'].includes(c);
    const precedence = (op) => (op === '+' || op === '-') ? 1 : 2;
    const applyOperation = (a, b, op) => {
        switch (op) {
            case '+': return a + b;
            case '-': return a - b;
            case '*': return a * b;
            case '/': return b !== 0 ? a / b : NaN;
            default: return NaN;
        }
    };

    const tokens = expr.match(/(\d+|[+\-*/()])/g);
    if (!tokens) return '';

    const values = [];
    const ops = [];

    for (let token of tokens) {
        if (!isNaN(token)) {
            values.push(parseFloat(token));
        } else if (isOperator(token)) {
            while (ops.length && precedence(ops[ops.length - 1]) >= precedence(token)) {
                const b = values.pop();
                const a = values.pop();
                const op = ops.pop();
                const result = applyOperation(a, b, op);
                if (isNaN(result)) return '';
                values.push(result);
            }
            ops.push(token);
        } else if (token === '(') {
            ops.push(token);
        } else if (token === ')') {
            while (ops.length && ops[ops.length - 1] !== '(') {
                const b = values.pop();
                const a = values.pop();
                const op = ops.pop();
                const result = applyOperation(a, b, op);
                if (isNaN(result)) return '';
                values.push(result);
            }
            ops.pop(); // pop the '('
        } else {
            return ''; // invalid token
        }
    }

    while (ops.length) {
        const b = values.pop();
        const a = values.pop();
        const op = ops.pop();
        const result = applyOperation(a, b, op);
        if (isNaN(result)) return '';
        values.push(result);
    }

    return values.length === 1 ? values[0].toString() : '';
}