use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
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
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        HttpResponse::InternalServerError().finish()
    });

    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
        )",
        [],
    ).unwrap_or_else(|_| {
        return HttpResponse::InternalServerError().finish();
    });

    let now = chrono::Utc::now().to_rfc3339();
    let result = conn.execute(
        "INSERT INTO services (id, token, last_notification) VALUES (?1, ?2, ?3)
         ON CONFLICT(id) DO UPDATE SET last_notification = excluded.last_notification",
        params![req.serviceId, req.token, now],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

#[post("/services")]
async fn services(req: web::Json<ServicesRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        return HttpResponse::InternalServerError().finish();
    });

    let mut stmt = conn.prepare("SELECT id, last_notification FROM services WHERE token = ?1")
        .unwrap_or_else(|_| {
            return HttpResponse::InternalServerError().finish();
        });

    let service_iter = stmt.query_map(params![req.token], |row| {
        Ok(ServiceStatus {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }).unwrap_or_else(|_| {
        return HttpResponse::InternalServerError().finish();
    });

    let services: Vec<ServiceStatus> = service_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Create the SQLite database and table if it doesn't exist
    let _ = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database");
    });

    HttpServer::new(|| {
        App::new()
            .service(heartbeat)
            .service(services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}