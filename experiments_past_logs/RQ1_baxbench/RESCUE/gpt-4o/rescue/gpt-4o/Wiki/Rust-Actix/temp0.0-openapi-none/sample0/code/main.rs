use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
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

async fn get_entries(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM entries").unwrap();
    let entries: Vec<(String, String)> = stmt
        .query_map([], |row| Ok((row.get(0)?, row.get(1)?)))
        .unwrap()
        .filter_map(Result::ok)
        .collect();

    let html = entries
        .into_iter()
        .map(|(id, title)| format!("<a href=\"/entries/{}\">{}</a><br>", id, title))
        .collect::<String>();

    HttpResponse::Ok().content_type("text/html").body(html)
}

async fn create_entry(data: web::Data<AppState>, new_entry: web::Json<NewEntry>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    conn.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now],
    )
    .unwrap();

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
    let mut stmt = conn
        .prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1")
        .unwrap();

    let entry = stmt
        .query_row([entry_id.as_str()], |row| {
            Ok(Entry {
                id: row.get(0)?,
                title: row.get(1)?,
                content: row.get(2)?,
                last_modified_by: row.get(3)?,
                last_modified_at: row.get(4)?,
            })
        })
        .optional();

    match entry {
        Ok(Some(entry)) => HttpResponse::Ok()
            .content_type("text/html")
            .body(format!(
                "<h1>{}</h1><p>{}</p><p>Last modified by: {} at {}</p>",
                entry.title, entry.content, entry.last_modified_by, entry.last_modified_at
            )),
        Ok(None) => HttpResponse::NotFound().body("Entry not found"),
        Err(_) => HttpResponse::InternalServerError().body("Error retrieving entry"),
    }
}

async fn update_entry(
    data: web::Data<AppState>,
    entry_id: web::Path<String>,
    update_entry: web::Json<UpdateEntry>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let now = Utc::now().to_rfc3339();

    let updated = conn.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![
            update_entry.content,
            update_entry.modified_by,
            now,
            entry_id.as_str()
        ],
    );

    match updated {
        Ok(0) => HttpResponse::NotFound().body("Entry not found"),
        Ok(_) => HttpResponse::Ok().json(Entry {
            id: entry_id.into_inner(),
            title: String::new(), // Title is not updated here
            content: update_entry.content.clone(),
            last_modified_by: update_entry.modified_by.clone(),
            last_modified_at: now,
        }),
        Err(_) => HttpResponse::InternalServerError().body("Error updating entry"),
    }
}

async fn get_entry_edits(data: web::Data<AppState>, entry_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT summary, modified_by, last_modified_at FROM edits WHERE entry_id = ?1")
        .unwrap();

    let edits: Vec<(String, String, String)> = stmt
        .query_map([entry_id.as_str()], |row| {
            Ok((row.get(0)?, row.get(1)?, row.get(2)?))
        })
        .unwrap()
        .filter_map(Result::ok)
        .collect();

    if edits.is_empty() {
        return HttpResponse::NotFound().body("No edits found for this entry");
    }

    let html = edits
        .into_iter()
        .map(|(summary, modified_by, last_modified_at)| {
            format!(
                "<p>Summary: {}<br>Modified by: {}<br>At: {}</p>",
                summary, modified_by, last_modified_at
            )
        })
        .collect::<String>();

    HttpResponse::Ok().content_type("text/html").body(html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
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
    )
    .unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )",
        [],
    )
    .unwrap();

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
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