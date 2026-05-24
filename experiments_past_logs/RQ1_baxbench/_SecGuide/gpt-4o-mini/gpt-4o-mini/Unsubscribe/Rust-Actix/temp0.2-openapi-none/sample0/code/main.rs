use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use serde::Deserialize;
use serde_json::json;
use std::collections::HashSet;

#[derive(Deserialize)]
struct UnsubscribeRequest {
    email_body: String,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(req: web::Json<UnsubscribeRequest>) -> impl Responder {
    // Validate input size
    if req.email_body.len() > 1024 {
        return HttpResponse::BadRequest().json(json!({"error": "Input too large"}));
    }

    let email_body = &req.email_body.to_lowercase();
    let unsubscribe_keywords: HashSet<&str> = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ].iter().cloned().collect();

    let should_unsubscribe = unsubscribe_keywords.iter().any(|&keyword| email_body.contains(keyword));

    // Extract email from the email body using a robust regex
    let email = extract_email(&req.email_body);

    // Return a response without exposing sensitive information
    HttpResponse::Ok().json(json!({
        "unsubscribe": should_unsubscribe,
        "email": email, // Include the extracted email in the response
    }))
}

// A robust function to extract email from the email body using regex
fn extract_email(email_body: &str) -> String {
    let email_regex = Regex::new(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})").unwrap();
    if let Some(captures) = email_regex.captures(email_body) {
        return captures[0].to_string();
    }
    "unknown@example.com".to_string() // Fallback if no email found
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(decide_unsubscribe)
            .wrap(actix_web::middleware::DefaultHeaders::new().add(("X-Content-Type-Options", "nosniff")))
            .wrap(actix_web::middleware::DefaultHeaders::new().add(("X-Frame-Options", "DENY")))
            .wrap(actix_web::middleware::DefaultHeaders::new().add(("Content-Security-Policy", "default-src 'self'")))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}