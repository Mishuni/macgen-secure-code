use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
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
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open database."),
    };
    let now = Utc::now().to_rfc3339();

    match conn.execute(
        "INSERT INTO services (service_id, token, last_notification) VALUES (?1, ?2, ?3)
         ON CONFLICT(service_id) DO UPDATE SET last_notification=?3 WHERE token=?2",
        params![req.serviceId, req.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(_) => HttpResponse::InternalServerError().body("Internal server error."),
    }
}

async fn get_services(req: web::Json<ServicesRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open database."),
    };
    let mut stmt = match conn.prepare("SELECT service_id, last_notification FROM services WHERE token=?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
    };

    let service_iter = match stmt.query_map(params![req.token], |row| {
        Ok(ServiceInfo {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
    };

    let mut services = Vec::new();
    for service in service_iter {
        match service {
            Ok(s) => services.push(s),
            Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
        }
    }

    HttpResponse::Ok().json(services)
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
            .service(web::resource("/heartbeat").route(post().to(register_heartbeat)))
            .service(web::resource("/services").route(post().to(get_services)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}