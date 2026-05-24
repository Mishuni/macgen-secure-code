use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result as SqlResult};
use std::env;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use chrono::Utc;
use log::error;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

struct AppState {
    db_pool: Pool<SqliteConnectionManager>,
}

async fn get_messages(data: web::Data<AppState>, query: web::Query<GetMessagesQuery>) -> Result<impl Responder> {
    let conn = match data.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => {
            error!("Failed to acquire database connection");
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let mut stmt = match conn.prepare("SELECT content, username FROM messages ORDER BY timestamp DESC LIMIT ? OFFSET ?") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let message_iter = match stmt.query_map(params![query.limit.unwrap_or(10), query.offset.unwrap_or(0)], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query messages: {}", err);
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let mut messages = Vec::new();
    for message in message_iter {
        match message {
            Ok(msg) => messages.push(msg),
            Err(err) => {
                error!("Failed to map message: {}", err);
                return Ok(HttpResponse::InternalServerError().finish());
            }
        }
    }

    Ok(HttpResponse::Ok().json(messages))
}

#[derive(Deserialize)]
struct GetMessagesQuery {
    limit: Option<i64>,
    offset: Option<i64>,
    sort: Option<String>,
}

async fn post_message(data: web::Data<AppState>, message: web::Json<Message>) -> Result<impl Responder> {
    if message.content.trim().is_empty() || message.username.trim().is_empty() {
        return Ok(HttpResponse::BadRequest().body("Content and username cannot be empty"));
    }

    let conn = match data.db_pool.get() {
        Ok(conn) => conn,
        Err(_) => {
            error!("Failed to acquire database connection");
            return Ok(HttpResponse::InternalServerError().finish());
        }
    };

    let timestamp = Utc::now().naive_utc();
    let result = conn.execute(
        "INSERT INTO messages (content, username, timestamp) VALUES (?1, ?2, ?3)",
        params![message.content, message.username, timestamp],
    );

    match result {
        Ok(_) => Ok(HttpResponse::Ok().finish()),
        Err(err) => {
            error!("Failed to insert message: {}", err);
            Ok(HttpResponse::InternalServerError().finish())
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(&database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    let conn = pool.get().expect("Failed to get connection from pool");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    let app_data = web::Data::new(AppState {
        db_pool: pool,
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_data.clone())
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}