use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use chrono::Utc;
use log::{info, error};
use env_logger;

#[derive(Deserialize)]
struct HeartbeatRequest {
    service_id: String,
    token: String,
}

#[derive(Deserialize)]
struct ServicesRequest {
    token: String,
}

#[derive(Serialize)]
struct ServiceInfo {
    service_id: String,
    last_notification: String,
}

async fn register_heartbeat(req: web::Json<HeartbeatRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to the database: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let now = Utc::now().to_rfc3339();
    match conn.execute(
        "INSERT INTO services (service_id, token, last_notification) VALUES (?1, ?2, ?3)
         ON CONFLICT(service_id) DO UPDATE SET last_notification=excluded.last_notification",
        params![req.service_id, req.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(err) => {
            error!("Failed to register heartbeat: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn get_services(req: web::Json<ServicesRequest>) -> Result<HttpResponse, Error> {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to the database: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let mut stmt = match conn.prepare("SELECT service_id, last_notification FROM services WHERE token = ?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let service_iter = match stmt.query_map(params![req.token], |row| {
        Ok(ServiceInfo {
            service_id: row.get(0)?,
            last_notification: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query services: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let mut services = Vec::new();
    for service in service_iter {
        match service {
            Ok(service_info) => services.push(service_info),
            Err(err) => {
                error!("Failed to fetch service info: {}", err);
                return Ok(HttpResponse::InternalServerError().finish());
            }
        }
    }

    Ok(HttpResponse::Ok().json(services))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            service_id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
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