use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use uuid::Uuid;

const STORAGE_DIR: &str = "./uploads/";

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Create the storage directory if it doesn't exist
    fs::create_dir_all(STORAGE_DIR)?;

    HttpServer::new(|| {
        App::new()
            .route("/upload", web::post().to(upload_image))
            .route("/images/{image_id}", web::get().to(share_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn upload_image(mut payload: Multipart) -> impl Responder {
    let mut file_path: Option<PathBuf> = None;

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        let filename = content_disposition.get_filename().unwrap_or("file").to_string();
        let unique_id = Uuid::new_v4().to_string();
        let sanitized_filename = sanitize_filename::sanitize(&filename);
        let full_path = Path::new(STORAGE_DIR).join(format!("{}_{}", unique_id, sanitized_filename));

        // Save the file
        let mut f = web::block(move || std::fs::File::create(&full_path)).await.unwrap().unwrap();
        while let Some(chunk) = field.next().await {
            let data = chunk.unwrap();
            f = web::block(move || f.write_all(&data)).await.unwrap().unwrap();
        }

        file_path = Some(full_path);
    }

    match file_path {
        Some(path) => {
            let id = path.file_name().unwrap().to_str().unwrap().to_string();
            HttpResponse::Ok().json(serde_json::json!({ "id": id }))
        }
        None => HttpResponse::BadRequest().json(serde_json::json!({ "error": "File upload failed" })),
    }
}

async fn share_image(web::Path(image_id): web::Path<String>) -> impl Responder {
    let file_path = Path::new(STORAGE_DIR).join(&image_id);

    if file_path.exists() {
        let mime_type = mime_guess::from_path(&file_path).first_or_octet_stream();
        let file = web::block(move || std::fs::File::open(file_path)).await;

        match file {
            Ok(file) => {
                HttpResponse::Ok()
                    .content_type(mime_type)
                    .body(web::block(move || {
                        let mut buf = Vec::new();
                        std::io::copy(&mut file.take(1_000_000), &mut buf).unwrap(); // Limit to 1MB for safety
                        buf
                    }).await.unwrap())
            }
            Err(_) => HttpResponse::InternalServerError().json(serde_json::json!({ "error": "Internal server error" })),
        }
    } else {
        HttpResponse::NotFound().json(serde_json::json!({ "error": "Image not found" }))
    }
}