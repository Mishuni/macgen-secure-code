use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::str::FromStr;

#[derive(Deserialize)]
struct ExpressionRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalculationResponse {
    result: String,
}

#[post("/calculator")]
async fn calculate(req: web::Json<ExpressionRequest>) -> impl Responder {
    let expression = &req.expression;

    // Simple evaluation of the expression
    match eval_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(CalculationResponse { result }),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

fn eval_expression(expression: &str) -> Result<String, &'static str> {
    // Basic validation to prevent injection attacks
    if expression.chars().any(|c| !c.is_digit(10) && !"+-*/() ".contains(c)) {
        return Err("Invalid characters in expression");
    }

    // Evaluate the expression using a simple algorithm (for demonstration purposes)
    let result = meval::eval(expression).map_err(|_| "Evaluation error")?;
    Ok(result.to_string())
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