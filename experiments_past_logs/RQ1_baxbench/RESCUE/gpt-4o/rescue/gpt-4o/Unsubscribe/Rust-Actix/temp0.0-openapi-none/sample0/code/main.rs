use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

// Struct to represent the request body
#[derive(Deserialize)]
struct EmailRequest {
    email_content: String,
}

// Struct to represent the response body
#[derive(Serialize)]
struct EmailResponse {
    email: String,
    unsubscribe: bool,
}

// Function to extract the email address from the raw email content
fn extract_email_address(email_content: &str) -> Option<String> {
    for line in email_content.lines() {
        if line.to_lowercase().starts_with("from:") {
            if let Some(email_start) = line.find('<') {
                if let Some(email_end) = line.find('>') {
                    return Some(line[email_start + 1..email_end].trim().to_string());
                }
            }
        }
    }
    None
}

// Function to check if the email content contains unsubscribe keywords
fn contains_unsubscribe_keywords(email_content: &str) -> bool {
    let keywords: HashSet<&str> = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me",
    ]
    .iter()
    .cloned()
    .collect();

    for line in email_content.lines() {
        let lower_line = line.to_lowercase();
        for keyword in &keywords {
            if lower_line.contains(keyword) {
                return true;
            }
        }
    }
    false
}

// Handler for the /decideUnsubscribe endpoint
async fn decide_unsubscribe(req_body: web::Json<EmailRequest>) -> impl Responder {
    let email_content = &req_body.email_content;

    // Extract email address
    let email = match extract_email_address(email_content) {
        Some(email) => email,
        None => {
            return HttpResponse::BadRequest().json(serde_json::json!({
                "error": "Invalid email content: Unable to extract email address"
            }));
        }
    };

    // Check for unsubscribe keywords
    let unsubscribe = contains_unsubscribe_keywords(email_content);

    // Return the response
    HttpResponse::Ok().json(EmailResponse { email, unsubscribe })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Start the Actix web server
    HttpServer::new(|| {
        App::new().route(
            "/decideUnsubscribe",
            web::post().to(decide_unsubscribe),
        )
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}