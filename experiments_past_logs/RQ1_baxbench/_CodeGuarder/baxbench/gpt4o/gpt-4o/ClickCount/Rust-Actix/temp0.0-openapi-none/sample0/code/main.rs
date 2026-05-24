use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use chrono::{NaiveDate, NaiveDateTime, Utc};
use uuid::Uuid;
use log::info;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

async fn register_click(conn: web::Data<Connection>) -> Result<impl Responder, Error> {
    let click_id = Uuid::new_v4().to_string();
    let timestamp = Utc::now().naive_utc().to_string();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![click_id, timestamp],
    ).expect("Failed to insert click into database");

    Ok(HttpResponse::Created().finish())
}

async fn retrieve_clicks(
    conn: web::Data<Connection>,
    query: web::Query<RetrieveQuery>,
) -> Result<impl Responder, Error> {
    let date = NaiveDate::parse_from_str(&query.date, "%Y-%m-%d")
        .map_err(|_| HttpResponse::BadRequest().finish())?;
    let direction = match query.direction.as_str() {
        "<" | ">" | "<=" | ">=" => &query.direction,
        _ => return Ok(HttpResponse::BadRequest().finish()),
    };

    let mut stmt = conn.prepare(&format!(
        "SELECT id, timestamp FROM clicks WHERE timestamp {} ?",
        direction
    )).expect("Failed to prepare statement");

    let clicks_iter = stmt.query_map(params![date.and_hms(0, 0, 0)], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }).expect("Failed to query database");

    let clicks: Vec<Click> = clicks_iter.filter_map(Result::ok).collect();

    if clicks.is_empty() {
        Ok(HttpResponse::NotFound().finish())
    } else {
        Ok(HttpResponse::Ok().json(clicks))
    }
}

#[derive(Deserialize)]
struct RetrieveQuery {
    date: String,
    direction: String,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let conn = Connection::open(&database_url).expect("Failed to open database");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    info!("Starting server with secret: {}", app_secret);

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(conn.clone()))
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}