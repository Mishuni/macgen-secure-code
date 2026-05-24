use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use serde::Serialize;
use std::collections::HashSet;

#[derive(Serialize)]
struct UnsubscribeResponse {
    email: String,
    unsubscribe: bool,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(body: String) -> impl Responder {
    // Define unsubscribe keywords
    let unsubscribe_keywords: HashSet<&str> = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ].iter().cloned().collect();

    // Sanitize input
    let sanitized_body = sanitize_input(&body);
    
    // Extract email
    let email = extract_email(&sanitized_body);
    
    // Validate email
    if !is_valid_email(&email) {
        return HttpResponse::BadRequest().finish();
    }

    // Check for unsubscribe keywords
    let unsubscribe = unsubscribe_keywords.iter().any(|&keyword| sanitized_body.to_lowercase().contains(keyword));

    // Construct response
    let response = UnsubscribeResponse {
        email,
        unsubscribe,
    };

    HttpResponse::Ok().json(response)
}

// Function to sanitize input
fn sanitize_input(input: &str) -> String {
    input.replace(&['<', '>', '&', '"', '\''][..], "")
}

// Function to extract email from the raw email content
fn extract_email(body: &str) -> String {
    if let Some(from_line) = body.lines().find(|line| line.to_lowercase().starts_with("from:")) {
        if let Some(email) = from_line.split('<').nth(1).and_then(|s| s.split('>').next()) {
            return email.trim().to_string();
        }
    }
    String::new()
}

// Function to validate email format
fn is_valid_email(email: &str) -> bool {
    let email_regex = Regex::new(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").unwrap();
    email_regex.is_match(email)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(decide_unsubscribe)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}