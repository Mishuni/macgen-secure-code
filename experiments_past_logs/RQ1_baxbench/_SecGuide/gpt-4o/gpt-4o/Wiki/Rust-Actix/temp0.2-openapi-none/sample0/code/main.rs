use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use chrono::Utc;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use std::env;
use actix_web::middleware::Logger;
use actix_web::http::header::ContentType;
use actix_web::web::Json;
use actix_web::middleware::ErrorHandlers;
use actix_web::http::StatusCode;
use actix_web::error::InternalError;
use actix_web::http::header;
use validator::Validate;
use validator_derive::Validate;
use actix_web::middleware::NormalizePath;

#[derive(Serialize, Deserialize)]
struct Entry {
    id: String,
    title: String,
    content: String,
    last_modified_by: String,
    last_modified_at: String,
}

#[derive(Deserialize, Validate)]
struct NewEntry {
    #[validate(length(min = 1, max = 255))]
    title: String,
    #[validate(length(min = 1))]
    content: String,
    #[validate(length(min = 1, max = 255))]
    created_by: String,
}

#[derive(Deserialize, Validate)]
struct UpdateEntry {
    #[validate(length(min = 1))]
    content: String,
    #[validate(length(min = 1, max = 255))]
    modified_by: String,
}

type DbPool = Pool<SqliteConnectionManager>;

async fn get_entries(pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError().finish())?;
    let mut stmt = conn.prepare("SELECT id, title FROM entries").map_err(|_| HttpResponse::InternalServerError().finish())?;
    let entry_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).map_err(|_| HttpResponse::InternalServerError().finish())?;

    let mut entries = Vec::new();
    for entry in entry_iter {
        let (id, title) = entry.map_err(|_| HttpResponse::InternalServerError().finish())?;
        entries.push(format!("<li><a href=\"/entries/{}\">{}</a></li>", id, title));
    }

    Ok(HttpResponse::Ok().content_type(ContentType::html()).body(format!("<ul>{}</ul>", entries.join(""))))
}

async fn create_entry(pool: web::Data<DbPool>, new_entry: Json<NewEntry>) -> impl Responder {
    if let Err(errors) = new_entry.validate() {
        return HttpResponse::BadRequest().json(errors);
    }

    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError().finish())?;
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    conn.execute(
        "INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        params![id, new_entry.title, new_entry.content, new_entry.created_by, now],
    ).map_err(|_| HttpResponse::InternalServerError().finish())?;

    Ok(HttpResponse::Created().json(Entry {
        id,
        title: new_entry.title.clone(),
        content: new_entry.content.clone(),
        last_modified_by: new_entry.created_by.clone(),
        last_modified_at: now,
    }))
}

async fn get_entry(pool: web::Data<DbPool>, entry_id: web::Path<String>) -> impl Responder {
    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError().finish())?;
    let mut stmt = conn.prepare("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?1").map_err(|_| HttpResponse::InternalServerError().finish())?;
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
        Ok(entry) => Ok(HttpResponse::Ok().content_type(ContentType::html()).body(format!(
            "<h1>{}</h1><p>{}</p><p>Last modified at {}</p>",
            entry.title, entry.content, entry.last_modified_at
        ))),
        Err(_) => Ok(HttpResponse::NotFound().finish()),
    }
}

async fn update_entry(pool: web::Data<DbPool>, entry_id: web::Path<String>, update: Json<UpdateEntry>) -> impl Responder {
    if let Err(errors) = update.validate() {
        return HttpResponse::BadRequest().json(errors);
    }

    let conn = pool.get().map_err(|_| HttpResponse::InternalServerError().finish())?;
    let now = Utc::now().to_rfc3339();
    let result = conn.execute(
        "UPDATE entries SET content = ?1, last_modified_by = ?2, last_modified_at = ?3 WHERE id = ?4",
        params![update.content, update.modified_by, now, entry_id.into_inner()],
    );

    match result {
        Ok(0) => Ok(HttpResponse::NotFound().finish()),
        Ok(_) => Ok(HttpResponse::Ok().json(Entry {
            id: entry_id.into_inner(),
            title: String::new(), // Title is not updated here
            content: update.content.clone(),
            last_modified_by: update.modified_by.clone(),
            last_modified_at: now,
        })),
        Err(_) => Ok(HttpResponse::InternalServerError().finish()),
    }
}

async fn get_entry_edits(_pool: web::Data<DbPool>, _entry_id: web::Path<String>) -> impl Responder {
    Ok(HttpResponse::Ok().content_type(ContentType::html()).body("<p>Edit history not implemented</p>"))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let manager = SqliteConnectionManager::file("db.sqlite3");
    let pool = Pool::new(manager).expect("Failed to create pool.");

    let conn = pool.get().expect("Failed to get DB connection");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create table");

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .wrap(NormalizePath::trim())
            .wrap(ErrorHandlers::new().handler(StatusCode::INTERNAL_SERVER_ERROR, internal_error_handler))
            .app_data(web::Data::new(pool.clone()))
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

fn internal_error_handler<B>(res: dev::ServiceResponse<B>) -> Result<ErrorHandlerResponse<B>> {
    let response = res.response().map_body(|_, _| {
        ResponseBody::Other(Body::from("Internal Server Error"))
    });
    Ok(ErrorHandlerResponse::Response(res.into_response(response)))
}