use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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

async fn calculate(req: web::Json<CalcRequest>) -> impl Responder {
    let expression = &req.expression;
    if let Err(e) = validate_expression(expression) {
        return HttpResponse::BadRequest().body("Invalid input");
    }
    match eval_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(CalcResponse { result }),
        Err(_) => HttpResponse::BadRequest().body("Error evaluating expression"),
    }
}

fn validate_expression(expression: &str) -> Result<(), String> {
    if expression.len() > 100 {
        return Err("Expression too long".to_string());
    }
    for c in expression.chars() {
        if !c.is_digit(10) && !"+-*/(). ".contains(c) {
            return Err("Invalid character".to_string());
        }
    }
    Ok(())
}

fn eval_expression(expression: &str) -> Result<String, String> {
    let tokens = tokenize(expression)?;
    let rpn = shunting_yard(&tokens)?;
    let result = evaluate_rpn(&rpn)?;
    Ok(result.to_string())
}

fn tokenize(expression: &str) -> Result<Vec<String>, String> {
    let mut tokens = Vec::new();
    let mut num = String::new();
    for c in expression.chars() {
        if c.is_digit(10) || c == '.' {
            num.push(c);
        } else if "+-*/()".contains(c) {
            if !num.is_empty() {
                tokens.push(num.clone());
                num.clear();
            }
            tokens.push(c.to_string());
        } else if !c.is_whitespace() {
            return Err("Invalid character".to_string());
        }
    }
    if !num.is_empty() {
        tokens.push(num);
    }
    Ok(tokens)
}

fn shunting_yard(tokens: &[String]) -> Result<Vec<String>, String> {
    let mut output = Vec::new();
    let mut operators = Vec::new();
    let precedence = HashMap::from([('+', 1), ('-', 1), ('*', 2), ('/', 2)]);
    let associativity = HashMap::from([('+', "L"), ('-', "L"), ('*', "L"), ('/', "L")]);

    for token in tokens {
        if let Ok(_) = token.parse::<f64>() {
            output.push(token.clone());
        } else if "+-*/".contains(&token[..]) {
            while let Some(op) = operators.last() {
                if "+-*/".contains(op)
                    && ((associativity[&token.chars().next().unwrap()] == "L"
                        && precedence[&token.chars().next().unwrap()] <= precedence[&op.chars().next().unwrap()])
                        || (associativity[&token.chars().next().unwrap()] == "R"
                            && precedence[&token.chars().next().unwrap()] < precedence[&op.chars().next().unwrap()]))
                {
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
                    break;
                }
                output.push(operators.pop().unwrap());
            }
            if operators.last() == Some(&"(".to_string()) {
                operators.pop();
            } else {
                return Err("Mismatched parentheses".to_string());
            }
        }
    }

    while let Some(op) = operators.pop() {
        if op == "(" || op == ")" {
            return Err("Mismatched parentheses".to_string());
        }
        output.push(op);
    }

    Ok(output)
}

fn evaluate_rpn(rpn: &[String]) -> Result<f64, String> {
    let mut stack = Vec::new();
    for token in rpn {
        if let Ok(num) = token.parse::<f64>() {
            stack.push(num);
        } else if "+-*/".contains(&token[..]) {
            if stack.len() < 2 {
                return Err("Insufficient values in expression".to_string());
            }
            let b = stack.pop().unwrap();
            let a = stack.pop().unwrap();
            let result = match token.as_str() {
                "+" => a + b,
                "-" => a - b,
                "*" => a * b,
                "/" => {
                    if b == 0.0 {
                        return Err("Division by zero".to_string());
                    }
                    a / b
                },
                _ => return Err("Unknown operator".to_string()),
            };
            stack.push(result);
        }
    }
    if stack.len() == 1 {
        Ok(stack.pop().unwrap())
    } else {
        Err("Invalid expression".to_string())
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/calculator", web::post().to(calculate))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}