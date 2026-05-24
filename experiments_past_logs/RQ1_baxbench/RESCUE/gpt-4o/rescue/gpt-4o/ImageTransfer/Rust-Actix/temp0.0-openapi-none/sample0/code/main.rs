use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::path::{Path, PathBuf};
use uuid::Uuid;
use serde::Serialize;
use std::fs;
use actix_web::http::header::ContentType;

const STORAGE_DIR: &str = "./uploads";

#[derive(Serialize)]
struct UploadResponse {
    id: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

// Ensure the storage directory exists
fn ensure_storage_dir() -> std::io::Result<()> {
    if !Path::new(STORAGE_DIR).exists() {
        fs::create_dir_all(STORAGE_DIR)?;
    }
    Ok(())
}

// Handler for uploading an image
async fn upload_image(mut payload: Multipart) -> impl Responder {
    ensure_storage_dir().unwrap_or_else(|_| {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to create storage directory".to_string(),
        });
    });

    while let Some(Ok(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        if let Some(filename) = content_disposition.get_filename() {
            // Sanitize the filename
            let sanitized_filename = sanitize_filename::sanitize(filename);
            let file_id = Uuid::new_v4().to_string();
            let file_path = PathBuf::from(STORAGE_DIR).join(&file_id);

            // Write the file to disk
            let mut file = match fs::File::create(&file_path) {
                Ok(f) => f,
                Err(_) => {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to save file".to_string(),
                    });
                }
            };

            while let Some(Ok(chunk)) = field.next().await {
                if let Err(_) = file.write_all(&chunk) {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to write file".to_string(),
                    });
                }
            }

            return HttpResponse::Ok().json(UploadResponse { id: file_id });
        }
    }

    HttpResponse::BadRequest().json(ErrorResponse {
        error: "No file provided".to_string(),
    })
}

// Handler for serving an image
async fn get_image(image_id: web::Path<String>) -> impl Responder {
    let file_path = PathBuf::from(STORAGE_DIR).join(image_id.into_inner());

    if !file_path.starts_with(STORAGE_DIR) {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid file path".to_string(),
        });
    }

    if file_path.exists() && file_path.is_file() {
        let mime_type = mime_guess::from_path(&file_path).first_or_octet_stream();
        match fs::read(&file_path) {
            Ok(data) => HttpResponse::Ok()
                .content_type(ContentType::from(mime_type))
                .body(data),
            Err(_) => HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Failed to read file".to_string(),
            }),
        }
    } else {
        HttpResponse::NotFound().json(ErrorResponse {
            error: "File not found".to_string(),
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Ensure the storage directory exists at startup
    ensure_storage_dir()?;

    // Start the server
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/upload", web::post().to(upload_image))
            .route("/images/{imageId}", web::get().to(get_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}