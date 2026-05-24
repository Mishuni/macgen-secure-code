use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use uuid::Uuid;
use chrono::Utc;

#[derive(Serialize, Deserialize)]
struct Entry {
    id: String,
    title: String,
    content: String,
    last_modified_by: String,
    last_modified_at: String,
}

#[derive(Serialize, Deserialize)]
struct NewEntry {
    title: String,
    content: String,
    created_by: String,
}

#[derive(Serialize, Deserialize)]
struct UpdateEntry {
    content: String,
    modified_by: String,
    summary: String,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap_or_else(|_| {
        panic!("Failed to open database");
    });
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let state = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/entries", web::get().to(get_entries))
            .route("/entries", web::post().to(create_entry))
            .route("/entries/{entry_id}", web::get().to(get_entry))
            .route("/entries/{entry_id}", web::put().to(update_entry))
            .route("/entries/{entry_id}/edits", web::get().to(get_entry_edits))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title FROM entries").unwrap();
    let entries = stmt
        .query_map([], |row| {
            Ok(format!("<a href=\"/entries/{}\">{}</a>", row.get::<_, String>(0)?, row.get::<_, String>(1)?))
        })
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    
    HttpResponse::Ok().content_type("text/html").body(entries.join("<br/>"))
}

async fn create_entry(data: web::Data<AppState>, new_entry: web::Json<NewEntry>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();
    
    db.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now],
    ).unwrap();

    let entry = Entry {
        id: id.clone(),
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at: now,
    };

    HttpResponse::Created().json(entry)
}

async fn get_entry(data: web::Data<AppState>, web::Path(entry_id): web::Path<String>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").unwrap();
    
    if let Ok(entry) = stmt.query_row(params![entry_id], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            last_modified_by: row.get(3)?,
            last_modified_at: row.get(4)?,
        })
    }) {
        HttpResponse::Ok().content_type("text/html").body(format!("<h1>{}</h1><p>{}</p>", entry.title, entry.content))
    } else {
        HttpResponse::NotFound().finish()
    }
}

async fn update_entry(data: web::Data<AppState>, web::Path(entry_id): web::Path<String>, update_entry: web::Json<UpdateEntry>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let now = Utc::now().to_rfc3339();
    
    if db.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update_entry.content, update_entry.modified_by, now, entry_id],
    ).unwrap() > 0 {
        HttpResponse::Ok().finish()
    } else {
        HttpResponse::NotFound().finish()
    }
}

async fn get_entry_edits(data: web::Data<AppState>, web::Path(entry_id): web::Path<String>) -> impl Responder {
    // Placeholder for edit history functionality
    HttpResponse::Ok().content_type("text/html").body(format!("Edit history for entry: {}", entry_id))
}