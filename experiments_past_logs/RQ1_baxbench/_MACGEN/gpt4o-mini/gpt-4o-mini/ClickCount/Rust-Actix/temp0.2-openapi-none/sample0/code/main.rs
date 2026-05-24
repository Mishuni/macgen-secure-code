use actix_web::{post, get, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

#[post("/click")]
async fn register_click(click: web::Json<Click>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (id TEXT PRIMARY KEY, timestamp TEXT NOT NULL)",
        [],
    ).unwrap();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![click.id, click.timestamp],
    ).unwrap();

    HttpResponse::Created().finish()
}

#[get("/clicks")]
async fn retrieve_clicks(web::Query(params): web::Query<(String, String)>) -> impl Responder {
    let (date, direction) = params;

    // Validate direction
    if !["<", ">", "<=", ">="].contains(&direction.as_str()) {
        return HttpResponse::BadRequest().finish();
    }

    // Validate date format
    let date_regex = Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap();
    if !date_regex.is_match(&date) {
        return HttpResponse::BadRequest().finish();
    }

    let query = format!("SELECT id, timestamp FROM clicks WHERE timestamp {} ?1", direction);
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare(&query).unwrap();
    let clicks_iter = stmt.query_map(params![date], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }).unwrap();

    let clicks: Vec<Click> = clicks_iter.filter_map(Result::ok).collect();

    if clicks.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(clicks)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(register_click)
            .service(retrieve_clicks)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}