use actix_web::{web, App, HttpServer, Responder, HttpResponse, post};
use serde::Serialize;
use regex::Regex;

#[derive(Serialize)]
struct UnsubscribeResponse {
    email: String,
    unsubscribe: bool,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(body: String) -> impl Responder {
    let email = extract_email(&body).unwrap_or_default();
    let unsubscribe = check_unsubscribe_keywords(&body);
    HttpResponse::Ok().json(UnsubscribeResponse { email, unsubscribe })
}

fn extract_email(raw_email: &str) -> Option<String> {
    let re = Regex::new(r"(?i)^From:\s*[^<]+<([^>]+)>").unwrap();
    re.captures(raw_email).and_then(|caps| caps.get(1).map(|m| m.as_str().to_string()))
}

fn check_unsubscribe_keywords(content: &str) -> bool {
    let keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"];
    keywords.iter().any(|&keyword| content.to_lowercase().contains(keyword))
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