use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use serde::{Deserialize, Serialize};
use meval; // Add meval crate for expression evaluation

#[derive(Deserialize)]
struct CalculatorRequest {
    expression: String,
}

#[derive(Serialize)]
struct CalculatorResponse {
    result: String,
}

fn evaluate_expression(expression: &str) -> Result<f64, String> {
    let re = Regex::new(r"^[0-9]+(\s*[-+*/]\s*[0-9]+)*$").unwrap(); // Updated regex to restrict input
    if !re.is_match(expression) {
        return Err("Invalid characters".to_string());
    }
    if expression.len() > 100 {
        return Err("Expression too long".to_string());
    }

    let expr = meval::eval(expression).map_err(|e| e.to_string())?;
    Ok(expr)
}

#[post("/calculator")]
async fn calculate(req: web::Json<CalculatorRequest>) -> impl Responder {
    match evaluate_expression(&req.expression) {
        Ok(result) => HttpResponse::Ok().json(CalculatorResponse {
            result: result.to_string(),
        }),
        Err(err) => HttpResponse::BadRequest().body(err),
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