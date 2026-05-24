use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use chrono::{Utc, NaiveDate};
use std::env;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

async fn register_click() -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    let click_id = Uuid::new_v4().to_string();
    let timestamp = Utc::now().to_rfc3339();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![click_id, timestamp],
    ).expect("Failed to insert click");

    HttpResponse::Created().finish()
}

async fn retrieve_clicks(query: web::Query<RetrieveQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    let date = NaiveDate::parse_from_str(&query.date, "%Y-%m-%d").expect("Invalid date format");
    let direction = &query.direction;

    if !["<", ">", "<=", ">="].contains(&direction.as_str()) {
        return HttpResponse::BadRequest().finish();
    }

    let mut stmt = conn.prepare(&format!(
        "SELECT id, timestamp FROM clicks WHERE timestamp {} ?",
        direction
    )).expect("Failed to prepare statement");

    let click_iter = stmt.query_map(params![date.and_hms(0, 0, 0)], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }).expect("Failed to query clicks");

    let clicks: Vec<Click> = click_iter.map(|click| click.unwrap()).collect();

    if clicks.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(clicks)
    }
}

#[derive(Deserialize)]
struct RetrieveQuery {
    date: String,
    direction: String,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let conn = Connection::open("db.sqlite3").expect("Failed to connect to database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(|| {
        App::new()
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}