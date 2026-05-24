use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde_json::json;
use std::sync::Arc;
use regex::Regex;

#[post("/decideUnsubscribe")]
async fn decide_unsubscribe(body: String) -> impl Responder {
    // Define keywords for unsubscribe requests
    let unsubscribe_keywords = vec![
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ];

    // Check if the body contains any unsubscribe keywords
    let unsubscribe_regex = Regex::new(&unsubscribe_keywords.join("|")).unwrap();
    let email_regex = Regex::new(r"(?i)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap();

    // Extract email from the body
    let email_capture = email_regex.captures(&body);
    let email = match email_capture {
        Some(caps) => caps.get(0).map_or("", |m| m.as_str()),
        None => "",
    };

    // Determine if the body contains an unsubscribe request
    let should_unsubscribe = unsubscribe_regex.is_match(&body);

    // Create the response
    let response = json!({
        "email": email,
        "unsubscribe": should_unsubscribe,
    });

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