use actix_web::{post, get, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use chrono::{DateTime, Utc};

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

#[post("/click")]
async fn register_click() -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let id = uuid::Uuid::new_v4().to_string();
    let timestamp: String = Utc::now().to_rfc3339();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![id, timestamp],
    ).unwrap();

    HttpResponse::Created().finish()
}

#[get("/clicks")]
async fn retrieve_clicks(web::Query(params): web::Query<ClickQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    
    let direction = match params.direction.as_str() {
        "<" | ">" | "<=" | ">=" => params.direction,
        _ => return HttpResponse::BadRequest().finish(),
    };

    let date = match DateTime::parse_from_rfc3339(&params.date) {
        Ok(dt) => dt.to_rfc3339(),
        Err(_) => return HttpResponse::BadRequest().finish(),
    };

    let query = format!("SELECT id, timestamp FROM clicks WHERE timestamp {} ?", direction);
    let mut stmt = conn.prepare(&query).unwrap();
    let clicks_iter = stmt.query_map(params![date]).unwrap();

    let mut clicks = Vec::new();
    for click in clicks_iter {
        let click = click.unwrap();
        clicks.push(Click {
            id: click.get(0).unwrap(),
            timestamp: click.get(1).unwrap(),
        });
    }

    if clicks.is_empty() {
        return HttpResponse::NotFound().finish();
    }

    HttpResponse::Ok().json(clicks)
}

#[derive(Deserialize)]
struct ClickQuery {
    date: String,
    direction: String,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(register_click)
            .service(retrieve_clicks)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}