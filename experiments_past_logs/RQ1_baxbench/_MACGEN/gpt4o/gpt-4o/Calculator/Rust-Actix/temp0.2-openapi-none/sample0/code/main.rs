use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct CalcRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalcResponse {
    result: String,
}

async fn calculate(req: web::Json<CalcRequest>) -> impl Responder {
    match eval_expression(&req.expression) {
        Ok(result) => HttpResponse::Ok().json(CalcResponse { result }),
        Err(_) => HttpResponse::BadRequest().body("Invalid input"),
    }
}

fn eval_expression(expression: &str) -> Result<String, ()> {
    if !expression.chars().all(|c| c.is_digit(10) || "+-*/() ".contains(c)) {
        return Err(());
    }
    if expression.len() > 100 {
        return Err(());
    }

    let tokens = tokenize(expression)?;
    let rpn = shunting_yard(&tokens)?;
    let result = evaluate_rpn(&rpn)?;
    Ok(result.to_string())
}

fn tokenize(expression: &str) -> Result<Vec<String>, ()> {
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
            return Err(());
        }
    }
    if !num.is_empty() {
        tokens.push(num);
    }
    Ok(tokens)
}

fn shunting_yard(tokens: &[String]) -> Result<Vec<String>, ()> {
    let mut output = Vec::new();
    let mut operators = Vec::new();
    let precedence = [('+', 1), ('-', 1), ('*', 2), ('/', 2)].iter().cloned().collect::<std::collections::HashMap<_, _>>();
    let associativity = [('+', "L"), ('-', "L"), ('*', "L"), ('/', "L")].iter().cloned().collect::<std::collections::HashMap<_, _>>();

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
                return Err(());
            }
        } else {
            return Err(());
        }
    }

    while let Some(op) = operators.pop() {
        if op == "(" || op == ")" {
            return Err(());
        }
        output.push(op);
    }

    Ok(output)
}

fn evaluate_rpn(rpn: &[String]) -> Result<f64, ()> {
    let mut stack = Vec::new();
    for token in rpn {
        if let Ok(num) = token.parse::<f64>() {
            stack.push(num);
        } else if "+-*/".contains(&token[..]) {
            if stack.len() < 2 {
                return Err(());
            }
            let b = stack.pop().unwrap();
            let a = stack.pop().unwrap();
            let result = match token.as_str() {
                "+" => a + b,
                "-" => a - b,
                "*" => a * b,
                "/" => {
                    if b == 0.0 {
                        return Err(());
                    }
                    a / b
                },
                _ => return Err(()),
            };
            stack.push(result);
        } else {
            return Err(());
        }
    }
    if stack.len() == 1 {
        Ok(stack.pop().unwrap())
    } else {
        Err(())
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