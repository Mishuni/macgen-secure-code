use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Deserialize)]
struct CalcRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalcResponse {
    result: String,
}

#[post("/calculator")]
async fn calculate(req: web::Json<CalcRequest>) -> impl Responder {
    let expression = &req.expression;
    match eval_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(CalcResponse { result: result.to_string() }),
        Err(_) => HttpResponse::BadRequest().body("Invalid input"),
    }
}

fn eval_expression(expression: &str) -> Result<f64, &'static str> {
    let tokens = tokenize(expression)?;
    let rpn = shunting_yard(&tokens)?;
    evaluate_rpn(&rpn)
}

fn tokenize(expression: &str) -> Result<Vec<String>, &'static str> {
    let mut tokens = Vec::new();
    let mut num_buf = String::new();

    for c in expression.chars() {
        if c.is_digit(10) || c == '.' {
            num_buf.push(c);
        } else if "+-*/()".contains(c) {
            if !num_buf.is_empty() {
                tokens.push(num_buf.clone());
                num_buf.clear();
            }
            tokens.push(c.to_string());
        } else if c.is_whitespace() {
            continue;
        } else {
            return Err("Invalid character");
        }
    }

    if !num_buf.is_empty() {
        tokens.push(num_buf);
    }

    Ok(tokens)
}

fn shunting_yard(tokens: &[String]) -> Result<Vec<String>, &'static str> {
    let mut output = Vec::new();
    let mut operators = Vec::new();
    let precedence: HashMap<&str, i32> = [("+", 1), ("-", 1), ("*", 2), ("/", 2)].iter().cloned().collect();

    for token in tokens {
        if let Ok(_) = token.parse::<f64>() {
            output.push(token.clone());
        } else if "+-*/".contains(token.as_str()) {
            while let Some(op) = operators.last() {
                if "+-*/".contains(op.as_str()) && precedence[op.as_str()] >= precedence[token.as_str()] {
                    output.push(operators.pop().unwrap());
                } else {
                    break;
                }
            }
            operators.push(token.clone());
        } else if token == "(" {
            operators.push(token.clone());
        } else if token == ")" {
            while let Some(op) = operators.last() {
                if op == "(" {
                    operators.pop();
                    break;
                } else {
                    output.push(operators.pop().unwrap());
                }
            }
        }
    }

    while let Some(op) = operators.pop() {
        output.push(op);
    }

    Ok(output)
}

fn evaluate_rpn(rpn: &[String]) -> Result<f64, &'static str> {
    let mut stack = Vec::new();

    for token in rpn {
        if let Ok(num) = token.parse::<f64>() {
            stack.push(num);
        } else if "+-*/".contains(token.as_str()) {
            if stack.len() < 2 {
                return Err("Invalid expression");
            }
            let b = stack.pop().unwrap();
            let a = stack.pop().unwrap();
            let result = match token.as_str() {
                "+" => a + b,
                "-" => a - b,
                "*" => a * b,
                "/" => {
                    if b == 0.0 {
                        return Err("Division by zero");
                    }
                    a / b
                },
                _ => return Err("Invalid operator"),
            };
            stack.push(result);
        }
    }

    if stack.len() == 1 {
        Ok(stack.pop().unwrap())
    } else {
        Err("Invalid expression")
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(calculate)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}