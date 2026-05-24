use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

#[derive(Deserialize)]
struct MessageQuery {
    limit: Option<i32>,
    offset: Option<i32>,
    sort: Option<String>,
}

async fn get_messages(query: web::Query<MessageQuery>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").map_err(|_| HttpResponse::InternalServerError())?;
    let limit = query.limit.unwrap_or(10);
    let offset = query.offset.unwrap_or(0);
    let sort = query.sort.as_deref().unwrap_or("DESC");

    let order = if sort.eq_ignore_ascii_case("ASC") { "ASC" } else { "DESC" };
    let mut stmt = conn.prepare(&format!("SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?", order))
        .map_err(|_| HttpResponse::InternalServerError())?;
    
    let messages_iter = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }).map_err(|_| HttpResponse::InternalServerError())?;

    let messages: Vec<Message> = messages_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(messages)
}

async fn post_message(message: web::Json<Message>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").map_err(|_| HttpResponse::InternalServerError())?;
    if message.content.is_empty() || message.username.is_empty() {
        return HttpResponse::BadRequest().finish();
    }
    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![message.content, message.username],
    ).map_err(|_| HttpResponse::InternalServerError())?;
    
    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    // Initialize the database
    let conn = Connection::open("db.sqlite3").map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "Failed to open database"))?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "Failed to create table"))?;

    HttpServer::new(move || {
        App::new()
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}