use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use chrono::Utc;
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Entry {
    id: String,
    title: String,
    content: String,
    last_modified_by: String,
    last_modified_at: String,
}

#[derive(Deserialize)]
struct NewEntry {
    title: String,
    content: String,
    created_by: String,
}

#[derive(Deserialize)]
struct UpdateEntry {
    content: String,
    modified_by: String,
    summary: String,
}

struct AppState {
    db: Mutex<Connection>,
}

fn escape_html(input: &str) -> String {
    let mut escaped = String::new();
    for c in input.chars() {
        match c {
            '&' => escaped.push_str("&amp;"),
            '<' => escaped.push_str("&lt;"),
            '>' => escaped.push_str("&gt;"),
            '"' => escaped.push_str("&quot;"),
            '\'' => escaped.push_str("&#x27;"),
            '/' => escaped.push_str("&#x2F;"),
            _ => escaped.push(c),
        }
    }
    escaped
}

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM entries").unwrap();
    let entry_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).unwrap();

    let mut entries = Vec::new();
    for entry in entry_iter {
        let (id, title) = entry.unwrap();
        entries.push(format!("<a href=\"/entries/{}\">{}</a>", escape_html(&id), escape_html(&title)));
    }
    HttpResponse::Ok().body(entries.join("<br>"))
}

async fn create_entry(data: web::Data<AppState>, new_entry: web::Json<NewEntry>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();
    conn.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now],
    ).unwrap();
    HttpResponse::Created().json(Entry {
        id,
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at: now,
    })
}

async fn get_entry(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").unwrap();
    let entry = stmt.query_row(params![entry_id.into_inner()], |row| {
        Ok(Entry {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            last_modified_by: row.get(3)?,
            last_modified_at: row.get(4)?,
        })
    });

    match entry {
        Ok(entry) => HttpResponse::Ok().body(format!(
            "<h1>{}</h1><p>{}</p><p>Last modified by: {} at {}</p>",
            escape_html(&entry.title), escape_html(&entry.content), escape_html(&entry.last_modified_by), escape_html(&entry.last_modified_at)
        )),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn update_entry(data: web::Data<AppState>, entry_id: web::Path<String>, update: web::Json<UpdateEntry>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let now = Utc::now().to_rfc3339();
    let result = conn.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update.content, update.modified_by, now, entry_id.into_inner()],
    );

    match result {
        Ok(0) => HttpResponse::NotFound().finish(),
        Ok(_) => HttpResponse::Ok().json(Entry {
            id: entry_id.into_inner(),
            title: String::new(), // Title is not updated here
            content: update.content.clone(),
            last_modified_by: update.modified_by.clone(),
            last_modified_at: now,
        }),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn get_entry_edits(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT modified_by, summary FROM edits WHERE entry_id = ?1").unwrap();
    let edit_iter = stmt.query_map(params![entry_id.into_inner()], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    });

    match edit_iter {
        Ok(edits) => {
            let mut edit_list = Vec::new();
            for edit in edits {
                let (modified_by, summary) = edit.unwrap();
                edit_list.push(format!("Modified by: {}, Summary: {}", escape_html(&modified_by), escape_html(&summary)));
            }
            HttpResponse::Ok().body(edit_list.join("<br>"))
        }
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let conn = Connection::open("db.sqlite3").unwrap();
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
    conn.execute(
        "CREATE TABLE IF NOT EXISTS edits (
            entry_id TEXT NOT NULL,
            modified_by TEXT NOT NULL,
            summary TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )",
        [],
    ).unwrap();

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .wrap(Logger::default())
            .route("/entries", web::get().to(get_entries))
            .route("/entries", web::post().to(create_entry))
            .route("/entries/{entryId}", web::get().to(get_entry))
            .route("/entries/{entryId}", web::put().to(update_entry))
            .route("/entries/{entryId}/edits", web::get().to(get_entry_edits))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}