use actix_web::{post, get, web, App, HttpServer, HttpResponse, Responder};
use serde::Deserialize;
use std::fs::{OpenOptions, File};
use std::io::{self, Write};
use std::sync::Mutex;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file: Mutex<File>,
}

#[post("/log")]
async fn log_message(data: web::Json<LogMessage>, state: web::Data<AppState>) -> impl Responder {
    // Validate the log message to prevent log injection attacks
    if data.message.contains('\n') || data.message.is_empty() {
        return HttpResponse::BadRequest().body("Log message cannot contain newlines or be empty.");
    }

    let mut file = state.log_file.lock().unwrap();
    if let Err(e) = writeln!(file, "{}", data.message) {
        eprintln!("Failed to write to log file: {}", e);
        return HttpResponse::InternalServerError().finish();
    }
    HttpResponse::Ok().finish()
}

#[get("/logs")]
async fn get_logs() -> impl Responder {
    match std::fs::read_to_string("logs.txt") {
        Ok(content) => HttpResponse::Ok().content_type("text/plain").body(content),
        Err(e) => {
            eprintln!("Failed to read log file: {}", e);
            HttpResponse::InternalServerError().body("Failed to retrieve logs.")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let log_file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("logs.txt")
        .unwrap_or_else(|e| {
            eprintln!("Unable to open log file: {}", e);
            std::process::exit(1);
        });

    let state = web::Data::new(AppState {
        log_file: Mutex::new(log_file),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .service(log_message)
            .service(get_logs)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}