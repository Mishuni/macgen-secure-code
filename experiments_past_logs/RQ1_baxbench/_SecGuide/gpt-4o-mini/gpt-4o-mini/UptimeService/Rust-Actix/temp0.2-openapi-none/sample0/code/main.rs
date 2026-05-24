use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;
use std::sync::Arc;
use r2d2::{Pool, PooledConnection, ConnectionManager};
use r2d2_sqlite::SqliteConnectionManager;
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
struct ServiceStatus {
    serviceId: String,
    lastNotification: String,
}

// Type alias for a pooled SQLite connection
type DbConnection = PooledConnection<ConnectionManager<rusqlite::Connection>>;

// Function to create a new database connection pool
fn create_pool() -> Pool<ConnectionManager<rusqlite::Connection>> {
    let manager = SqliteConnectionManager::file("db.sqlite3");
    Pool::builder().build(manager).expect("Failed to create pool.")
}

#[post("/heartbeat")]
async fn heartbeat(req: web::Json<HeartbeatRequest>, pool: web::Data<Arc<Pool<ConnectionManager<rusqlite::Connection>>>>) -> impl Responder {
    let conn = pool.get().expect("Failed to get a connection from the pool");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let now = Utc::now().to_rfc3339();
    match conn.execute(
        "INSERT INTO services (id, token, last_notification) VALUES (?1, ?2, ?3)
        ON CONFLICT(id) DO UPDATE SET last_notification = excluded.last_notification",
        params![req.serviceId, req.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(err) => {
            log::error!("Database error: {:?}", err);
            HttpResponse::InternalServerError().body("Internal server error.")
        },
    }
}

#[post("/services")]
async fn services(req: web::Json<ServicesRequest>, pool: web::Data<Arc<Pool<ConnectionManager<rusqlite::Connection>>>>) -> impl Responder {
    let conn = pool.get().expect("Failed to get a connection from the pool");
    let mut stmt = conn.prepare("SELECT id, last_notification FROM services WHERE token = ?1").expect("Failed to prepare statement");
    
    let service_iter = stmt.query_map(params![req.token], |row| {
        Ok(ServiceStatus {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }).expect("Failed to query services");

    let services: Vec<ServiceStatus> = service_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Create a database connection pool
    let pool = Arc::new(create_pool());

    // Start the HTTP server
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .service(heartbeat)
            .service(services)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}