use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use log::{info, error};
use env_logger;
use std::collections::HashSet;

#[derive(Deserialize)]
struct ExpressionRequest {
    expression: String,
}

async fn calculate_expression(req: web::Json<ExpressionRequest>) -> impl Responder {
    let expression = &req.expression;
    match evaluate_expression(expression) {
        Ok(result) => HttpResponse::Ok().json(serde_json::json!({ "result": result })),
        Err(err) => {
            error!("Error evaluating expression: {}", err);
            HttpResponse::BadRequest().body("Invalid input")
        }
    }
}

fn evaluate_expression(expression: &str) -> Result<f64, &'static str> {
    let safe_chars: HashSet<char> = "0123456789+-*/(). ".chars().collect();
    if !expression.chars().all(|c| safe_chars.contains(&c)) {
        return Err("Expression contains unsafe characters");
    }

    // Use a simple parser to evaluate the expression safely
    let result = meval::eval_str(expression).map_err(|_| "Failed to evaluate expression")?;
    Ok(result)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    info!("Starting server at http://0.0.0.0:5000");
    HttpServer::new(|| {
        App::new()
            .route("/calculator", web::post().to(calculate_expression))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}