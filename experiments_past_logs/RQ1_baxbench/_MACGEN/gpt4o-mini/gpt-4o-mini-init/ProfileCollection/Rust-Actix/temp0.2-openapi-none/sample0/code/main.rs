use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_multipart::Multipart;
use rusqlite::{params, Connection};
use futures::stream::StreamExt;
use std::io::Cursor;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            profile_page TEXT NOT NULL,
            profile_photo BLOB NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(move || {
        App::new()
            .route("/add_profile", web::post().to(add_profile))
            .route("/profile/{username}", web::get().to(get_profile))
            .route("/profile-photo/{username}", web::get().to(get_profile_photo))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn add_profile(mut payload: Multipart) -> impl Responder {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo: Vec<u8> = Vec::new();

    while let Ok(Some(field)) = payload.try_next().await {
        let field_name = field.name().to_string();
        let mut data = Vec::new();
        let mut cursor = Cursor::new(data);
        field.for_each(|chunk| {
            cursor.write_all(&chunk.unwrap()).unwrap();
            async {}
        }).await;
        if field_name == "username" {
            username = String::from_utf8(cursor.into_inner()).unwrap();
        } else if field_name == "profile_page" {
            profile_page = String::from_utf8(cursor.into_inner()).unwrap();
        } else if field_name == "profile_photo" {
            profile_photo = cursor.into_inner();
        }
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    match conn.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
                       params![username, profile_page, profile_photo]) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::Forbidden().body("Profile already exists"),
    }
}

async fn get_profile(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    match stmt.query_row(params![username], |row| row.get(0)) {
        Ok(profile_page) => HttpResponse::Ok().content_type("text/html").body(profile_page),
        Err(_) => HttpResponse::NotFound().body("Profile not found"),
    }
}

async fn get_profile_photo(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_photo FROM profiles WHERE username = ?1").unwrap();
    match stmt.query_row(params![username], |row| row.get(0)) {
        Ok(profile_photo) => HttpResponse::Ok().content_type("image/png").body(profile_photo),
        Err(_) => HttpResponse::NotFound().body("Profile photo not found"),
    }
}