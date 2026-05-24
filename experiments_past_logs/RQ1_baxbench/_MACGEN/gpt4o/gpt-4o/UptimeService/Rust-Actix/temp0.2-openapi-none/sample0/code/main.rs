use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use chrono::Utc;

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
struct ServiceInfo {
    serviceId: String,
    lastNotification: String,
}

async fn register_heartbeat(req: web::Json<HeartbeatRequest>) -> impl Responder {
    if req.serviceId.is_empty() || req.token.is_empty() {
        return HttpResponse::BadRequest().body("Invalid request payload.");
    }

    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    let now = Utc::now().to_rfc3339();

    match conn.execute(
        "INSERT INTO services (serviceId, token, lastNotification) VALUES (?1, ?2, ?3)
         ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification",
        params![req.serviceId, req.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(_) => HttpResponse::InternalServerError().body("Internal server error."),
    }
}

async fn get_services(req: web::Json<ServicesRequest>) -> impl Responder {
    if req.token.is_empty() {
        return HttpResponse::BadRequest().body("Invalid request payload.");
    }

    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    let mut stmt = conn.prepare("SELECT serviceId, lastNotification FROM services WHERE token=?1").unwrap();
    let service_iter = stmt.query_map(params![req.token], |row| {
        Ok(ServiceInfo {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }).unwrap();

    let mut services = Vec::new();
    for service in service_iter {
        services.push(service.unwrap());
    }

    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(|| {
        App::new()
            .route("/heartbeat", web::post().to(register_heartbeat))
            .route("/services", web::post().to(get_services))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}