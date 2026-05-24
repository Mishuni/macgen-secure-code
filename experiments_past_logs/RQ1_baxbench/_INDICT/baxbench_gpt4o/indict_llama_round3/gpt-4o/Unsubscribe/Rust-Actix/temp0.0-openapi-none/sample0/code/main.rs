use actix_web::{web, App, HttpServer, Responder, HttpResponse, post};
use serde::{Deserialize, Serialize};
use regex::Regex;

#[derive(Deserialize)]
struct EmailRequest {
    email_content: String,
}

#[derive(Serialize)]
struct UnsubscribeResponse {
    email: String,
    unsubscribe: bool,
}

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(req_body: String) -> impl Responder {
    let email_regex = Regex::new(r"(?i)From:\s*[^<]*<([^>]+)>").unwrap();
    let unsubscribe_keywords = vec![
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ];

    let email = email_regex.captures(&req_body)
        .and_then(|caps| caps.get(1))
        .map_or("", |m| m.as_str())
        .to_string();

    let unsubscribe = unsubscribe_keywords.iter().any(|&keyword| req_body.to_lowercase().contains(keyword));

    let response = UnsubscribeResponse {
        email,
        unsubscribe,
    };

    HttpResponse::Ok().json(response)
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