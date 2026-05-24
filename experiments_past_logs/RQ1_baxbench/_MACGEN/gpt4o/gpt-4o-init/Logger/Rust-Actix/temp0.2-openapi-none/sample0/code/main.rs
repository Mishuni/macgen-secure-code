
use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::Deserialize;
use std::fs::{OpenOptions, File};
use std::io::{self, Write, Read};

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

async fn log_message(log: web::Json<LogMessage>) -> impl Responder {
    let sanitized_message = log.message.replace("\n", "\\n").replace("\r", "\\r");
    
    let mut file = match OpenOptions::new()
        .create(true)
        .append(true)
        .write(true)
        .open("logs.txt") {
            Ok(file) => file,
            Err(_) => return HttpResponse::InternalServerError().finish(),
        };
    
    if let Err(_) = writeln!(file, "{}", sanitized_message) {
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Ok().body("Log message successful")
}

async fn get_logs() -> impl Responder {
    let mut file = match File::open("logs.txt") {
        Ok(file) => file,
        Err(_) => return HttpResponse::Ok().body(""),
    };

    let mut contents = String::new();
    if let Err(_) = file.read_to_string(&mut contents) {
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Ok().content_type("text/plain").body(contents)
}

#[actix_web::main]
async fn main() -> io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/log", web::post().to(log_message))
            .route("/logs", web::get().to(get_logs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}