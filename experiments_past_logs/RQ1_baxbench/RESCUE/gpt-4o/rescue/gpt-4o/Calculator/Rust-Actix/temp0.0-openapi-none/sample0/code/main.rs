use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Deserialize)]
struct CalculationRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalculationResponse {
    result: String,
}

fn sanitize_expression(expression: &str) -> Result<String, HttpResponse> {
    // Allow only digits, basic operators, and whitespace
    let allowed_chars: HashSet<char> = "+-*/().0123456789 ".chars().collect();
    if expression.chars().all(|c| allowed_chars.contains(&c)) {
        Ok(expression.to_string())
    } else {
        Err(HttpResponse::BadRequest().body("Invalid characters in expression"))
    }
}

fn evaluate_expression(expression: &str) -> Result<f64, HttpResponse> {
    // Use a simple parser to evaluate the expression
    meval::eval_str(expression).map_err(|_| HttpResponse::BadRequest().body("Invalid arithmetic expression"))
}

async fn calculate(req: web::Json<CalculationRequest>) -> impl Responder {
    let sanitized_expression = match sanitize_expression(&req.expression) {
        Ok(expr) => expr,
        Err(err) => return err,
    };

    let result = match evaluate_expression(&sanitized_expression) {
        Ok(res) => res,
        Err(err) => return err,
    };

    HttpResponse::Ok().json(CalculationResponse {
        result: result.to_string(),
    })
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