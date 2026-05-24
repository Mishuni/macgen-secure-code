use actix_web::{post, get, web, App, HttpServer, HttpResponse, Responder};
use serde::Deserialize;
use std::fs::{OpenOptions, File};
use std::io::{self, Write, BufRead};
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
    let mut file = state.log_file.lock().unwrap();
    if let Err(e) = writeln!(file, "{}", data.message) {
        eprintln!("Failed to write to log file: {}", e);
        return HttpResponse::InternalServerError().finish();
    }
    HttpResponse::Ok().finish()
}

#[get("/logs")]
async fn get_logs(state: web::Data<AppState>) -> impl Responder {
    let file = state.log_file.lock().unwrap();
    let reader = io::BufReader::new(&*file);
    let logs: Vec<String> = reader.lines().filter_map(Result::ok).collect();
    let response = logs.join("\n");
    HttpResponse::Ok().body(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let log_file = OpenOptions::new()
        .create(true)
        .append(true)
        .read(true)
        .open("logs.txt")?;

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