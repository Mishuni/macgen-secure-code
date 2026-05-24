use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::{OpenOptions, read_to_string};
use std::io::Write;
use std::sync::Mutex;
use std::net::IpAddr;
use std::str::FromStr;
use std::env;
use std::path::Path;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file: Mutex<String>,
}

async fn log_message(data: web::Data<AppState>, log: web::Json<LogMessage>) -> impl Responder {
    // Input validation and sanitization
    let sanitized_message = log.message.trim();
    if sanitized_message.is_empty() {
        return HttpResponse::BadRequest().body("Log message cannot be empty");
    }

    let log_file_path = data.log_file.lock().unwrap();
    let mut file = match OpenOptions::new()
        .create(true)
        .append(true)
        .write(true)
        .open(&*log_file_path) {
            Ok(f) => f,
            Err(e) => {
                eprintln!("Error opening log file: {}", e);
                return HttpResponse::InternalServerError().body("Failed to open log file");
            },
        };

    if let Err(e) = writeln!(file, "{}", sanitized_message) {
        eprintln!("Error writing to log file: {}", e);
        return HttpResponse::InternalServerError().body("Failed to write to log file");
    }

    HttpResponse::Ok().body("Log message successful")
}

async fn get_logs(data: web::Data<AppState>) -> impl Responder {
    let log_file_path = data.log_file.lock().unwrap();
    match read_to_string(&*log_file_path) {
        Ok(contents) => HttpResponse::Ok().body(contents),
        Err(e) => {
            eprintln!("Error reading log file: {}", e);
            HttpResponse::InternalServerError().body("Failed to read log file")
        },
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Use a configurable log file path
    let log_file = env::var("LOG_FILE_PATH").unwrap_or_else(|_| "logs.txt".to_string());

    // Validate log file path
    if Path::new(&log_file).is_dir() {
        panic!("Log file path cannot be a directory");
    }

    // Bind to a specific IP address (localhost) for security
    let bind_address = env::var("BIND_ADDRESS").unwrap_or_else(|_| "127.0.0.1:5000".to_string());
    let ip: IpAddr = IpAddr::from_str(&bind_address.split(':').next().unwrap()).unwrap();
    if ip.is_unspecified() {
        panic!("Binding to all network interfaces is not allowed for security reasons");
    }

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(AppState {
                log_file: Mutex::new(log_file.clone()),
            }))
            .route("/log", web::post().to(log_message))
            .route("/logs", web::get().to(get_logs))
    })
    .bind(bind_address)?
    .run()
    .await
}