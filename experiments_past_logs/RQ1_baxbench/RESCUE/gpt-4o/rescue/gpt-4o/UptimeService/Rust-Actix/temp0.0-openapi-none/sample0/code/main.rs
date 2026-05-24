use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use chrono::Utc;
use std::sync::Mutex;

// Structs for request payloads
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
struct ServiceOverview {
    serviceId: String,
    lastNotification: String,
}

// Shared state for database connection
struct AppState {
    db: Mutex<Connection>,
}

// Initialize the database
fn init_db(conn: &Connection) {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            token TEXT NOT NULL,
            last_notification TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create table");
}

// Handler for /heartbeat
async fn register_heartbeat(
    data: web::Data<AppState>,
    payload: web::Json<HeartbeatRequest>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let now = Utc::now().to_rfc3339();

    match conn.execute(
        "INSERT INTO services (service_id, token, last_notification) 
         VALUES (?, ?, ?)
         ON CONFLICT(service_id, token) 
         DO UPDATE SET last_notification = excluded.last_notification",
        params![payload.serviceId, payload.token, now],
    ) {
        Ok(_) => HttpResponse::Ok().body("Heartbeat registered successfully."),
        Err(_) => HttpResponse::InternalServerError().body("Internal server error."),
    }
}

// Handler for /services
async fn get_services(
    data: web::Data<AppState>,
    payload: web::Json<ServicesRequest>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = match conn.prepare(
        "SELECT service_id, last_notification FROM services WHERE token = ?",
    ) {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
    };

    let services_iter = match stmt.query_map(params![payload.token], |row| {
        Ok(ServiceOverview {
            serviceId: row.get(0)?,
            lastNotification: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
    };

    let mut services = Vec::new();
    for service in services_iter {
        match service {
            Ok(s) => services.push(s),
            Err(_) => return HttpResponse::InternalServerError().body("Internal server error."),
        }
    }

    HttpResponse::Ok().json(services)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Load environment variables
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());

    // Initialize SQLite database
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    init_db(&conn);

    // Shared application state
    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    // Start the server
    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/heartbeat", web::post().to(register_heartbeat))
            .route("/services", web::post().to(get_services))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}