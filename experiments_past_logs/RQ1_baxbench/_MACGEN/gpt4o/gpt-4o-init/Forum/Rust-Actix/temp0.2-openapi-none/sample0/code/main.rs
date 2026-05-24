use actix_web::{web, App, HttpServer, Responder, HttpResponse, Error};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

async fn get_messages(query: web::Query<GetMessagesQuery>, db: web::Data<Connection>) -> Result<impl Responder, Error> {
    let limit = query.limit.unwrap_or(10);
    let offset = query.offset.unwrap_or(0);
    let sort = match query.sort.as_deref() {
        Some("ASC") => "ASC",
        _ => "DESC",
    };

    let mut stmt = db.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?",
        sort
    ))?;
    let message_iter = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    })?;

    let mut messages = Vec::new();
    for message in message_iter {
        messages.push(message?);
    }

    Ok(HttpResponse::Ok().json(messages))
}

async fn post_message(msg: web::Json<Message>, db: web::Data<Connection>) -> Result<impl Responder, Error> {
    let conn = db.get_ref();
    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![msg.content, msg.username],
    )?;
    Ok(HttpResponse::Ok().finish())
}

#[derive(Deserialize)]
struct GetMessagesQuery {
    limit: Option<i64>,
    offset: Option<i64>,
    sort: Option<String>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let database_url = "db.sqlite3";
    let conn = Connection::open(database_url).expect("Failed to open database");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(conn.clone()))
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}