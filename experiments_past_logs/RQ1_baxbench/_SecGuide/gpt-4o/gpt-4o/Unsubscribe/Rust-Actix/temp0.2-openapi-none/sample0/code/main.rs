use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use actix_web::cookie::Cookie;
use actix_web::http::header::SET_COOKIE;
use regex::Regex;
use std::collections::HashSet;

#[derive(Deserialize)]
struct EmailRequest {
    email_content: String,
}

#[derive(Serialize)]
struct EmailResponse {
    email: String,
    unsubscribe: bool,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(req_body: web::Json<EmailRequest>) -> impl Responder {
    // Validate and sanitize input
    let email_content = sanitize_input(&req_body.email_content);

    // Extract email address from the email content
    let email = match extract_email(&email_content) {
        Some(email) => email,
        None => {
            // Log the error for monitoring purposes
            eprintln!("Failed to extract email address from content");
            return HttpResponse::BadRequest().body("Invalid email content");
        }
    };

    // Check for unsubscribe keywords
    let unsubscribe_keywords: HashSet<&str> = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ].iter().cloned().collect();
    let unsubscribe = unsubscribe_keywords.iter().any(|&keyword| email_content.to_lowercase().contains(keyword));

    // Generate a pseudorandom value for CSRF protection
    let csrf_token = Uuid::new_v4().to_string();
    let cookie = Cookie::build("csrf_token", csrf_token.clone())
        .http_only(true)
        .secure(true) // Ensure the cookie is only sent over HTTPS
        .finish();

    // Create response
    let response = EmailResponse {
        email,
        unsubscribe,
    };

    HttpResponse::Ok()
        .insert_header((SET_COOKIE, cookie.to_string()))
        .json(response)
}

fn extract_email(email_content: &str) -> Option<String> {
    let email_regex = Regex::new(r"(?i)from:\s*.*<([^>]+)>").unwrap();
    email_regex.captures(email_content).and_then(|caps| caps.get(1).map(|m| m.as_str().to_string()))
}

fn sanitize_input(input: &str) -> String {
    // Basic sanitization to prevent script injection
    input.replace("<", "&lt;").replace(">", "&gt;")
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