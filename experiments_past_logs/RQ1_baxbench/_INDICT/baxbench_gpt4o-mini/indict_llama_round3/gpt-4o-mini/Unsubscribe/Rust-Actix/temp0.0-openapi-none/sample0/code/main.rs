use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde_json::json;
use regex::Regex;

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(body: String) -> impl Responder {
    let unsubscribe_keywords = vec![
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me",
    ];

    let email = extract_email(&body);
    let unsubscribe = unsubscribe_keywords.iter().any(|&keyword| body.to_lowercase().contains(keyword));

    HttpResponse::Ok().json(json!({
        "email": email,
        "unsubscribe": unsubscribe,
    }))
}

fn extract_email(body: &str) -> String {
    let re = Regex::new(r"(?i)from:\s*([^<>\s]+<([^<>]+)>)|([^<>\s]+)").unwrap();
    if let Some(captures) = re.captures(body) {
        if let Some(email) = captures.get(2) {
            return email.as_str().to_string();
        } else if let Some(email) = captures.get(3) {
            return email.as_str().to_string();
        }
    }
    String::new() // Return an empty string if no email is found
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