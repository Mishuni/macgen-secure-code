use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use chrono::Utc;
use uuid::Uuid;
use std::sync::Arc;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use log::{error, info};

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

type DbPool = Pool<SqliteConnectionManager>;

#[post("/heartbeat")]
async fn register_heartbeat(pool: web::Data<DbPool>, req: web::Json<HeartbeatRequest>) -> impl Responder {
    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            error!("Failed to get a database connection: {}", e);
            return HttpResponse::InternalServerError().body("Internal server error.");
        }
    };

    let now = Utc::now().to_rfc3339();

    if req.service_id.is_empty() || req.token.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input.");
    }

    match conn.execute(
        "INSERT INTO services (service_id, token, last_notification) VALUES (?1, ?2, ?3)
         ON CONFLICT(service_id) DO UPDATE SET last_notification=?3 WHERE token=?2",
        params![req.service_id, req.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(e) => {
            error!("Database error: {}", e);
            HttpResponse::InternalServerError().body("Internal server error.")
        },
    }
}

#[post("/services")]
async fn get_services(pool: web::Data<DbPool>, req: web::Json<ServicesRequest>) -> impl Responder {
    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            error!("Failed to get a database connection: {}", e);
            return HttpResponse::InternalServerError().body("Internal server error.");
        }
    };

    if req.token.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input.");
    }

    let mut stmt = match conn.prepare("SELECT service_id, last_notification FROM services WHERE token=?1") {
        Ok(stmt) => stmt,
        Err(e) => {
            error!("Database error: {}", e);
            return HttpResponse::InternalServerError().body("Internal server error.");
        },
    };

    let services_iter = match stmt.query_map(params![req.token], |row| {
        Ok(ServiceInfo {
            service_id: row.get(0)?,
            last_notification: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(e) => {
            error!("Database error: {}", e);
            return HttpResponse::InternalServerError().body("Internal server error.");
        },
    };

    let mut services = Vec::new();
    for service in services_iter {
        match service {
            Ok(s) => services.push(s),
            Err(e) => {
                error!("Database error: {}", e);
                return HttpResponse::InternalServerError().body("Internal server error.");
            },
        }
    }

    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    let conn = pool.get().expect("Failed to get a database connection");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            service_id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let app_data = web::Data::new(pool);

    HttpServer::new(move || {
        App::new()
            .app_data(app_data.clone())
            .service(register_heartbeat)
            .service(get_services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}