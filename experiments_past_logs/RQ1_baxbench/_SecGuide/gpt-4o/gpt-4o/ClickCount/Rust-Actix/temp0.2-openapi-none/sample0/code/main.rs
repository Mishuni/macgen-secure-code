use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use chrono::{NaiveDate, Utc};
use log::info;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;

#[derive(Serialize, Deserialize)]
struct Click {
    id: String,
    timestamp: String,
}

async fn register_click(pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(err) => {
            log::error!("Failed to get a connection from the pool: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let click_id = Uuid::new_v4().to_string();
    let timestamp = Utc::now().to_rfc3339();

    match conn.execute(
        "INSERT INTO clicks (id, timestamp) VALUES (?1, ?2)",
        params![click_id, timestamp],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(err) => {
            log::error!("Failed to insert click: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn retrieve_clicks(
    pool: web::Data<Pool<SqliteConnectionManager>>,
    query: web::Query<RetrieveQuery>,
) -> Result<HttpResponse, Error> {
    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(err) => {
            log::error!("Failed to get a connection from the pool: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let date = match NaiveDate::parse_from_str(&query.date, "%Y-%m-%d") {
        Ok(date) => date,
        Err(_) => return Ok(HttpResponse::BadRequest().body("Invalid date format")),
    };

    let direction = match query.direction.as_str() {
        ">" | "<" => &query.direction,
        _ => return Ok(HttpResponse::BadRequest().body("Invalid direction")),
    };

    let mut stmt = match conn.prepare("SELECT id, timestamp FROM clicks WHERE timestamp ? ?") {
        Ok(stmt) => stmt,
        Err(err) => {
            log::error!("Failed to prepare statement: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let click_iter = match stmt.query_map(params![direction, date.and_hms(0, 0, 0)], |row| {
        Ok(Click {
            id: row.get(0)?,
            timestamp: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(err) => {
            log::error!("Failed to query clicks: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let clicks: Vec<Click> = click_iter.filter_map(Result::ok).collect();

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
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(database_url);
    let pool = match Pool::new(manager) {
        Ok(pool) => pool,
        Err(err) => {
            log::error!("Failed to create pool: {}", err);
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to create pool"));
        }
    };

    {
        let conn = match pool.get() {
            Ok(conn) => conn,
            Err(err) => {
                log::error!("Failed to get a connection from the pool: {}", err);
                return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to get a connection from the pool"));
            }
        };

        if let Err(err) = conn.execute(
            "CREATE TABLE IF NOT EXISTS clicks (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL
            )",
            [],
        ) {
            log::error!("Failed to create table: {}", err);
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to create table"));
        }
    }

    let bind_address = env::var("BIND_ADDRESS").unwrap_or_else(|_| "0.0.0.0:5000".to_string());

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .data(pool.clone())
            .route("/click", web::post().to(register_click))
            .route("/clicks", web::get().to(retrieve_clicks))
    })
    .bind(bind_address)?
    .run()
    .await
}