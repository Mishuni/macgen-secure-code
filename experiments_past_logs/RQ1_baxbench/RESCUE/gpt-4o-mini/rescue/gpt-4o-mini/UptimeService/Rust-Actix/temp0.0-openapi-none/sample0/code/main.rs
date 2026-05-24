use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Deserialize)]
struct HeartbeatRequest {
    serviceId: String,
    token: String,
}

#[derive(Deserialize)]
struct ServicesRequest {
    token: String,
}

#[derive(Serialize)]
struct ServiceStatus {
    serviceId: String,
    lastNotification: String,
}

#[post("/heartbeat")]
async fn heartbeat(req: web::Json<HeartbeatRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let _ = conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            lastNotification TEXT NOT NULL,
            token TEXT NOT NULL
        )",
        [],
    );

    let current_time = chrono::Utc::now().to_rfc3339();
    let result = conn.execute(
        "INSERT INTO services (serviceId, lastNotification, token) VALUES (?1, ?2, ?3)
         ON CONFLICT(serviceId) DO UPDATE SET lastNotification = excluded.lastNotification",
        params![req.serviceId, current_time, req.token],
    );

    match result {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(_) => HttpResponse::InternalServerError().body("Internal server error."),
    }
}

#[post("/services")]
async fn services(req: web::Json<ServicesRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT serviceId, lastNotification FROM services WHERE token = ?1").unwrap();
    let service_iter = stmt.query_map(params![req.token], |row| {
        Ok(ServiceStatus {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }).unwrap();

    let services: Vec<ServiceStatus> = service_iter.filter_map(Result::ok).collect();

    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Create the SQLite database and tables if they do not exist
    let _ = Connection::open("db.sqlite3").unwrap();

    HttpServer::new(|| {
        App::new()
            .service(heartbeat)
            .service(services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}