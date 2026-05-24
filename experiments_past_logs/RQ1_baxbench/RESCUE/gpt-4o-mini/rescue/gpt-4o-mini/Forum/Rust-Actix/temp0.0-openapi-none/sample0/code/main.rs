use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

async fn get_messages(query: web::Query<(Option<i32>, Option<i32>, Option<String>)>) -> impl Responder {
    let limit = query.0.unwrap_or(10);
    let offset = query.1.unwrap_or(0);
    let sort = query.2.as_deref().unwrap_or("DESC");

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?",
        sort
    )).unwrap();

    let messages: Result<Vec<Message>, _> = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }).collect();

    match messages {
        Ok(msgs) => HttpResponse::Ok().json(msgs),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn post_message(message: web::Json<Message>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![message.content, message.username],
    ).unwrap();

    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the database
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).unwrap();

    // Start the web server
    HttpServer::new(|| {
        App::new()
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}