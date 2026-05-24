use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct Message {
    content: String,
    username: String,
}

impl Message {
    fn validate(&self) -> Result<(), &'static str> {
        if self.content.is_empty() || self.username.is_empty() {
            return Err("Content and username cannot be empty");
        }
        Ok(())
    }
}

async fn get_messages(
    limit: Option<web::Query<i32>>,
    offset: Option<web::Query<i32>>,
    sort: Option<web::Query<String>>,
) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database");
    });
    
    let limit = limit.unwrap_or(web::Query(Some(10))).0.clamp(1, 100);
    let offset = offset.unwrap_or(web::Query(Some(0))).0.max(0);
    let sort_order = sort.unwrap_or(web::Query(Some("DESC".to_string()))).0;

    let mut stmt = conn.prepare(&format!(
        "SELECT content, username FROM messages ORDER BY id {} LIMIT ? OFFSET ?",
        if sort_order == "ASC" { "ASC" } else { "DESC" }
    )).unwrap();

    let messages_iter = stmt
        .query_map(params![limit, offset], |row| {
            Ok(Message {
                content: row.get(0)?,
                username: row.get(1)?,
            })
        })
        .unwrap();

    let messages: Vec<Message> = messages_iter.filter_map(Result::ok).collect();
    HttpResponse::Ok().json(messages)
}

async fn post_message(message: web::Json<Message>) -> impl Responder {
    if let Err(err) = message.validate() {
        return HttpResponse::BadRequest().body(err);
    }

    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database");
    });
    
    conn.execute(
        "INSERT INTO messages (content, username) VALUES (?1, ?2)",
        params![message.content, message.username],
    ).unwrap();
    
    HttpResponse::Ok().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env::var("APP_SECRET").expect("APP_SECRET must be set");

    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database");
    });
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/messages", web::get().to(get_messages))
            .route("/messages", web::post().to(post_message))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}