use actix_web::{post, get, web, App, HttpServer, HttpResponse, Responder};
use serde::Deserialize;
use std::fs::{OpenOptions, read_to_string};
use std::io::Write;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

fn sanitize_message(message: &str) -> String {
    message.replace("\n", "\\n").replace("\r", "\\r")
}

#[post("/log")]
async fn log_message(log: web::Json<LogMessage>) -> impl Responder {
    if log.message.len() > 256 {
        return HttpResponse::BadRequest().finish();
    }

    let sanitized_message = sanitize_message(&log.message);
    let mut file = OpenOptions::new()
        .append(true)
        .create(true)
        .open("logs.txt")
        .unwrap();
    
    if let Err(e) = writeln!(file, "{}", sanitized_message) {
        eprintln!("Couldn't write to file: {}", e);
        return HttpResponse::InternalServerError().finish();
    }
    
    HttpResponse::Ok().finish()
}

#[get("/logs")]
async fn get_logs() -> impl Responder {
    match read_to_string("logs.txt") {
        Ok(contents) => HttpResponse::Ok().content_type("text/plain").body(contents),
        Err(e) => {
            eprintln!("Couldn't read file: {}", e);
            HttpResponse::InternalServerError().finish()
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(log_message)
            .service(get_logs)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}