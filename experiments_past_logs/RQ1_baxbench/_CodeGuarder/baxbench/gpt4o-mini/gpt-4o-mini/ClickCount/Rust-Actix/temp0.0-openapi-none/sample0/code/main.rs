use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use chrono::{DateTime, Utc};

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: DateTime<Utc>,
}

#[derive(Deserialize)]
struct ClickRequest {
    timestamp: String,
}

#[derive(Deserialize)]
struct ClickQuery {
    date: String,
    direction: String,
}

async fn register_click(click: web::Json<ClickRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let id = uuid::Uuid::new_v4().to_string();
    let timestamp = click.timestamp.clone();

    conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![id, timestamp],
    ).unwrap();

    HttpResponse::Created().finish()
}

async fn retrieve_clicks(query: web::Query<ClickQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT id, timestamp FROM clicks WHERE timestamp ? ?").unwrap();
    let condition = match query.direction.as_str() {
        "<" => "<",
        "<=" => "<=",
        ">" => ">",
        ">=" => ">=",
        _ => return HttpResponse::BadRequest().body("Invalid direction"),
    };

    let date = query.date.clone();
    let rows = stmt.query_map(params![date, condition], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }).unwrap();

    let clicks: Vec<Click> = rows.filter_map(Result::ok).collect();

    if clicks.is_empty() {
        return HttpResponse::NotFound().body("No clicks found");
    }

    HttpResponse::Ok().json(clicks)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(app_secret.clone()))
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}