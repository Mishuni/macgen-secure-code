use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::num::ParseFloatError;

#[derive(Deserialize)]
struct ExpressionRequest {
    expression: String,
}

#[derive(Serialize)]
struct ExpressionResponse {
    result: String,
}

#[post("/calculator")]
async fn calculate(req: web::Json<ExpressionRequest>) -> impl Responder {
    let expression = &req.expression;

    // Validate the expression to prevent code injection
    if !is_valid_expression(expression) {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    // Calculate the result
    match evaluate_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(ExpressionResponse { result }),
        Err(_) => HttpResponse::BadRequest().body("Invalid input"),
    }
}

// Simple validation to allow only numbers and basic arithmetic operators
fn is_valid_expression(expression: &str) -> bool {
    let valid_chars = "0123456789+-*/(). ";
    expression.chars().all(|c| valid_chars.contains(c))
}

// Evaluate the expression safely
fn evaluate_expression(expression: &str) -> Result<String, ParseFloatError> {
    // Here we use a simple evaluation logic for demonstration purposes.
    // In a real application, consider using a proper math expression parser.
    let result = eval(expression)?;
    Ok(result.to_string())
}

// A simple evaluation function (this is a placeholder for actual evaluation logic)
fn eval(expression: &str) -> Result<f64, ParseFloatError> {
    // For simplicity, we will just parse the expression as a float.
    // In a real application, you would implement a proper parser.
    expression.trim().parse::<f64>()
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