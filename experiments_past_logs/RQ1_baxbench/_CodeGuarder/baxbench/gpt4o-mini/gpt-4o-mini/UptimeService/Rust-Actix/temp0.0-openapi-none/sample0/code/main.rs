use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use log::{error, info};

#[derive(Serialize, Deserialize)]
struct HeartbeatRequest {
    serviceId: String,
    token: String,
}

#[derive(Serialize, Deserialize)]
struct ServicesRequest {
    token: String,
}

#[derive(Serialize)]
struct ServiceOverview {
    serviceId: String,
    lastNotification: String,
}

fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

#[post("/heartbeat")]
async fn heartbeat(req: web::Json<HeartbeatRequest>) -> impl Responder {
    let conn = init_db().unwrap_or_else(|err| {
        error!("Database initialization failed: {}", err);
        HttpResponse::InternalServerError().finish()
    });

    if req.token != env::var("APP_SECRET").unwrap_or_default() {
        return HttpResponse::BadRequest().body("Invalid token");
    }

    let current_time = chrono::Utc::now().to_rfc3339();
    if let Err(err) = conn.execute(
        "INSERT OR REPLACE INTO services (serviceId, token, lastNotification) VALUES (?1, ?2, ?3)",
        params![req.serviceId, req.token, current_time],
    ) {
        error!("Failed to insert heartbeat: {}", err);
        return HttpResponse::InternalServerError().finish();
    }

    info!("Heartbeat registered for service: {}", req.serviceId);
    HttpResponse::Ok().finish()
}

#[post("/services")]
async fn services(req: web::Json<ServicesRequest>) -> impl Responder {
    let conn = init_db().unwrap_or_else(|err| {
        error!("Database initialization failed: {}", err);
        HttpResponse::InternalServerError().finish()
    });

    if req.token != env::var("APP_SECRET").unwrap_or_default() {
        return HttpResponse::BadRequest().body("Invalid token");
    }

    let mut stmt = conn
        .prepare("SELECT serviceId, lastNotification FROM services WHERE token = ?1")
        .unwrap();
    let service_iter = stmt
        .query_map(params![req.token], |row| {
            Ok(ServiceOverview {
                serviceId: row.get(0)?,
                lastNotification: row.get(1)?,
            })
        })
        .unwrap();

    let services: Vec<ServiceOverview> = service_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(heartbeat)
            .service(services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}