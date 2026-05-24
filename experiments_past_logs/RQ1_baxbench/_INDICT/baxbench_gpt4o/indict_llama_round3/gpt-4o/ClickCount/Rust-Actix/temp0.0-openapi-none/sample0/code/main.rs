use actix_web::{web, App, HttpServer, HttpResponse, Responder, post, get};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use chrono::{NaiveDate, Utc, DateTime, NaiveDateTime};
use uuid::Uuid;
use std::env;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

#[post("/click")]
async fn register_click() -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let click_id = Uuid::new_v4().to_string();
    let timestamp = Utc::now().to_rfc3339();

    match conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![click_id, timestamp],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
}

#[get("/clicks")]
async fn retrieve_clicks(query: web::Query<ClickQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let date = match NaiveDate::parse_from_str(&query.date, "%Y-%m-%d") {
        Ok(d) => d,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };
    let direction = &query.direction;

    let date_time = DateTime::<Utc>::from_utc(date.and_hms(0, 0, 0), Utc).to_rfc3339();

    let sql_query = format!("SELECT id, timestamp FROM clicks WHERE timestamp {} ?1", direction);
    let mut stmt = match conn.prepare(&sql_query) {
        Ok(s) => s,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    let click_iter = match stmt.query_map(params![date_time], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    let clicks: Vec<Click> = click_iter.filter_map(Result::ok).collect();

    if clicks.is_empty() {
        HttpResponse::NotFound().finish()
    } else {
        HttpResponse::Ok().json(clicks)
    }
}

#[derive(Deserialize)]
struct ClickQuery {
    date: String,
    direction: String,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(|| {
        App::new()
            .service(register_click)
            .service(retrieve_clicks)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}