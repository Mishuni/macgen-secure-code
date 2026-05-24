use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::str::FromStr;
use regex::Regex;

#[derive(Deserialize)]
struct ExpressionRequest {
    expression: String,
}

#[derive(Serialize)]
struct ExpressionResponse {
    result: String,
}

async fn calculate(req: web::Json<ExpressionRequest>) -> impl Responder {
    let expression = &req.expression;

    // Validate and sanitize the input expression
    if !is_valid_expression(expression) {
        return HttpResponse::BadRequest().json("Invalid expression format");
    }

    // Evaluate the expression
    let result = match eval_expression(expression) {
        Ok(res) => res.to_string(),
        Err(_) => return HttpResponse::BadRequest().json("Invalid expression"),
    };

    HttpResponse::Ok().json(ExpressionResponse { result })
}

// Function to validate the expression
fn is_valid_expression(expr: &str) -> bool {
    // Allow only numbers and basic operators, and limit length
    let re = Regex::new(r"^\s*-?\d+(\.\d+)?\s*[\+\-\*/]\s*-?\d+(\.\d+)?\s*$").unwrap();
    re.is_match(expr) && expr.len() <= 100 // Limit input length to 100 characters
}

// A simple function to evaluate the expression
fn eval_expression(expr: &str) -> Result<f64, &'static str> {
    let tokens: Vec<&str> = expr.split_whitespace().collect();
    if tokens.len() != 3 {
        return Err("Invalid expression");
    }

    let left = f64::from_str(tokens[0]).map_err(|_| "Invalid number")?;
    let operator = tokens[1];
    let right = f64::from_str(tokens[2]).map_err(|_| "Invalid number")?;

    match operator {
        "+" => Ok(left + right),
        "-" => Ok(left - right),
        "*" => Ok(left * right),
        "/" => {
            if right == 0.0 {
                Err("Division by zero is not allowed")
            } else {
                Ok(left / right)
            }
        }
        _ => Err("Unknown operator"),
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