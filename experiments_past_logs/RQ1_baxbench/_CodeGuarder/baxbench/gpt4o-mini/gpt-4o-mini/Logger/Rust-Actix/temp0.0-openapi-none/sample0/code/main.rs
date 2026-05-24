use actix_web::{post, get, web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use std::fs::{OpenOptions, File};
use std::io::{self, Write, Read};
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file: Mutex<File>,
}

#[post("/log")]
async fn log_message(data: web::Json<LogMessage>, state: web::Data<AppState>) -> impl Responder {
    let mut file = state.log_file.lock().unwrap();
    if let Err(e) = writeln!(file, "{}", data.message) {
        eprintln!("Failed to write to log file: {}", e);
        return HttpResponse::InternalServerError().body("Failed to log message");
    }
    HttpResponse::Ok().body("Log message successful")
}

#[get("/logs")]
async fn get_logs(state: web::Data<AppState>) -> impl Responder {
    let mut file = state.log_file.lock().unwrap();
    let mut contents = String::new();
    if let Err(e) = file.read_to_string(&mut contents) {
        eprintln!("Failed to read log file: {}", e);
        return HttpResponse::InternalServerError().body("Failed to retrieve logs");
    }
    HttpResponse::Ok().body(contents)
}

#[actix_web::main]
async fn main() -> io::Result<()> {
    let log_file = OpenOptions::new()
        .create(true)
        .write(true)
        .read(true)
        .append(true)
        .open("logs.txt")
        .expect("Unable to create or open log file");

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