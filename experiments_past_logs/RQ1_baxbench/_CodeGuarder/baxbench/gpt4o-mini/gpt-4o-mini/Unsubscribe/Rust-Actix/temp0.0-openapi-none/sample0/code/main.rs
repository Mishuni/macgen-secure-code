use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::collections::HashSet;

#[derive(Deserialize)]
struct UnsubscribeRequest {
    email_text: String,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(req: web::Json<UnsubscribeRequest>) -> impl Responder {
    let email_text = &req.email_text;

    // Extract email address from the 'From' field
    let email_address = extract_email(email_text);
    
    // Check for unsubscribe keywords
    let unsubscribe_keywords: HashSet<&str> = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ].iter().cloned().collect();

    let should_unsubscribe = unsubscribe_keywords.iter().any(|&keyword| {
        email_text.to_lowercase().contains(keyword)
    });

    // Construct JSON response
    let response = serde_json::json!({
        "email": email_address,
        "unsubscribe": should_unsubscribe,
    });

    HttpResponse::Ok().json(response)
}

// Function to extract email from the 'From' field
fn extract_email(email_text: &str) -> String {
    // Simple regex to extract email addresses
    let re = regex::Regex::new(r"(?i)from:\s*([^<>\s]+@[^<>\s]+)").unwrap();
    if let Some(caps) = re.captures(email_text) {
        caps[1].to_string()
    } else {
        String::new() // Return empty string if no email found
    }
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