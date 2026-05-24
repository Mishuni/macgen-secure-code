use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::str::FromStr;

#[derive(Deserialize)]
struct ExpressionRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalculationResult {
    result: String,
}

#[post("/calculator")]
async fn calculate(expr: web::Json<ExpressionRequest>) -> impl Responder {
    let expression = &expr.expression;

    match eval_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(CalculationResult { result }),
        Err(err) => HttpResponse::BadRequest().body(err),
    }
}

fn eval_expression(expression: &str) -> Result<String, &'static str> {
    // Basic validation to prevent empty expressions
    if expression.trim().is_empty() {
        return Err("Invalid expression: empty input");
    }

    // Evaluate the expression safely
    let result = match eval_basic_expression(expression) {
        Ok(res) => res.to_string(),
        Err(err) => return Err(err),
    };

    Ok(result)
}

// A very basic evaluator for simple arithmetic expressions
fn eval_basic_expression(expression: &str) -> Result<f64, &'static str> {
    let tokens: Vec<&str> = expression.split_whitespace().collect();
    if tokens.len() < 3 {
        return Err("Invalid expression: insufficient tokens");
    }

    let left: f64 = tokens[0].parse().map_err(|_| "Invalid number: left operand")?;
    let operator = tokens[1];
    let right: f64 = tokens[2].parse().map_err(|_| "Invalid number: right operand")?;

    match operator {
        "+" => Ok(left + right),
        "-" => Ok(left - right),
        "*" => Ok(left * right),
        "/" => {
            if right == 0.0 {
                Err("Error: division by zero")
            } else {
                Ok(left / right)
            }
        }
        _ => Err("Invalid operator: must be one of +, -, *, /"),
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