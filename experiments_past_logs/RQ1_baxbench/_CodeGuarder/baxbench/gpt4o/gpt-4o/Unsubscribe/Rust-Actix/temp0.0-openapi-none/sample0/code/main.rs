use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use mailparse::parse_mail;

#[derive(Serialize)]
struct UnsubscribeResponse {
    email: String,
    unsubscribe: bool,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(body: String) -> impl Responder {
    match parse_email(&body) {
        Ok((email, body_text)) => {
            let unsubscribe = analyze_email_for_unsubscribe(&body_text);
            HttpResponse::Ok().json(UnsubscribeResponse { email, unsubscribe })
        }
        Err(_) => HttpResponse::BadRequest().body("Invalid email format"),
    }
}

fn parse_email(raw_email: &str) -> Result<(String, String), &'static str> {
    let parsed = parse_mail(raw_email.as_bytes()).map_err(|_| "Failed to parse email")?;
    let headers = parsed.get_headers();
    let from_header = headers.get_first_value("From").ok_or("Missing From header")?;
    let email = from_header.split('<').nth(1).and_then(|s| s.split('>').next()).ok_or("Invalid From header format")?;
    let body_text = parsed.get_body().map_err(|_| "Failed to get email body")?;
    Ok((email.to_string(), body_text))
}

fn analyze_email_for_unsubscribe(body: &str) -> bool {
    let unsubscribe_keywords: HashSet<&str> = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ].iter().cloned().collect();

    let body_lower = body.to_lowercase();
    unsubscribe_keywords.iter().any(|&keyword| body_lower.contains(keyword))
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