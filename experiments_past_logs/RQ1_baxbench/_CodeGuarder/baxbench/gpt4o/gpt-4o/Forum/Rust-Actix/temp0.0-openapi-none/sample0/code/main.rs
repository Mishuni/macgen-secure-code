use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use log::info;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

async fn get_messages(query: web::Query<GetMessagesQuery>, db: web::Data<Connection>) -> impl Responder {
    let limit = query.limit.unwrap_or(10);
    let offset = query.offset.unwrap_or(0);
    let sort = query.sort.as_deref().unwrap_or("DESC");

    let mut stmt = db.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?",
        sort
    )).unwrap();

    let message_iter = stmt.query_map(params![limit, offset], |row| {
        Ok(Message {
            content: row.get(0)?,
            username: row.get(1)?,
        })
    }).unwrap();

    let mut messages = Vec::new();
    for message in message_iter {
        messages.push(message.unwrap());
    }

    HttpResponse::Ok().json(messages)
}

async fn post_message(new_message: web::Json<Message>, db: web::Data<Connection>) -> impl Responder {
    let result = db.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![new_message.content, new_message.username],
    );

    match result {
        Ok(_) => HttpResponse::Ok().finish(),
        Err(_) => HttpResponse::BadRequest().finish(),
    }
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

    let db = Connection::open("db.sqlite3").unwrap();
    db.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let db_data = web::Data::new(db);

    HttpServer::new(move || {
        App::new()
            .app_data(db_data.clone())
            .wrap(Logger::default())
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}