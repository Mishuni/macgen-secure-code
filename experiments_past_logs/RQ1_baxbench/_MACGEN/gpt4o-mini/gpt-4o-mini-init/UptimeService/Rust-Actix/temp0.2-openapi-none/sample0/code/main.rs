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
    if req.token.len() < 1 || req.serviceId.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let now = chrono::Utc::now().to_rfc3339();
    let result = conn.execute(
        "INSERT INTO services (id, token, last_notification) VALUES (?1, ?2, ?3)
         ON CONFLICT(id) DO UPDATE SET token = excluded.token, last_notification = excluded.last_notification",
        params![req.serviceId, req.token, now],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

#[post("/services")]
async fn services(req: web::Json<ServicesRequest>) -> impl Responder {
    if req.token.len() < 1 {
        return HttpResponse::BadRequest().finish();
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT id, last_notification FROM services WHERE token = ?1").unwrap();
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
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(heartbeat)
            .service(services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}