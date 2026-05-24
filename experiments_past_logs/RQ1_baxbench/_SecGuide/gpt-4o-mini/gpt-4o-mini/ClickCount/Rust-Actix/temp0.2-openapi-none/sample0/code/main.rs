use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use chrono::{DateTime, Utc};
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: DateTime<Utc>,
}

#[derive(Deserialize)]
struct ClickRequest {
    timestamp: DateTime<Utc>,
}

#[derive(Deserialize)]
struct ClicksQuery {
    date: String,
    direction: String,
}

fn validate_date_format(date: &str) -> bool {
    // Simple validation for date format (YYYY-MM-DD)
    date.chars().count() == 10 && date.chars().all(|c| c.is_digit(10) || c == '-')
}

async fn register_click(click_request: web::Json<ClickRequest>, pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError())?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).map_err(|_| HttpResponse::InternalServerError())?;

    let id = uuid::Uuid::new_v4().to_string();
    let timestamp = click_request.timestamp.to_rfc3339();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![id, timestamp],
    ).map_err(|err| {
        eprintln!("Database error: {:?}", err);
        HttpResponse::InternalServerError()
    })?;

    HttpResponse::Created().finish()
}

async fn retrieve_clicks(query: web::Query<ClicksQuery>, pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError())?;
    
    let valid_directions = ["<", "<=", ">", ">="];
    if !valid_directions.contains(&query.direction.as_str()) {
        return HttpResponse::BadRequest().finish();
    }

    if !validate_date_format(&query.date) {
        return HttpResponse::BadRequest().finish();
    }

    let mut stmt = conn.prepare("SELECT id, timestamp FROM clicks WHERE timestamp ? ?").map_err(|_| HttpResponse::InternalServerError())?;
    let rows = stmt.query_map(params![query.date.clone(), query.direction.as_str()], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }).map_err(|err| {
        eprintln!("Database error: {:?}", err);
        HttpResponse::InternalServerError()
    })?;

    let clicks: Vec<Click> = rows.filter_map(Result::ok).collect();

    if clicks.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(clicks)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    
    let db_path = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(db_path);
    let pool = Pool::builder().build(manager).expect("Failed to create pool.");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}