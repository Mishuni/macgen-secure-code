use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use uuid::Uuid;
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use serde::Serialize;
use mime_guess;
use std::ffi::OsStr;

#[derive(Serialize)]
struct UploadResponse {
    id: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn upload_image(mut payload: Multipart) -> Result<impl Responder> {
    let temp_dir = std::env::temp_dir();
    let mut file_id = Uuid::new_v4().to_string();
    let mut file_path = temp_dir.join(&file_id);

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();

        // Validate file extension
        let extension = Path::new(filename)
            .extension()
            .and_then(OsStr::to_str)
            .unwrap_or("");
        if !["jpg", "jpeg", "png", "gif"].contains(&extension) {
            return Ok(HttpResponse::BadRequest().json(ErrorResponse {
                error: "Unsupported file type".into(),
            }));
        }

        // Assign unique names to uploaded files
        file_path.set_extension(extension);

        // Create file with restrictive permissions
        let mut f = web::block(|| {
            let mut file = File::create(&file_path)?;
            file.set_permissions(fs::Permissions::from_mode(0o600))?;
            Ok(file)
        }).await??;

        while let Some(chunk) = field.next().await {
            let data = chunk?;
            f = web::block(move || f.write_all(&data).map(|_| f)).await??;
        }
    }

    Ok(HttpResponse::Ok().json(UploadResponse { id: file_id }))
}

async fn get_image(web::Path(image_id): web::Path<String>) -> Result<impl Responder> {
    let temp_dir = std::env::temp_dir();
    let file_path = temp_dir.join(&image_id);

    // Prevent path traversal
    if !file_path.starts_with(&temp_dir) {
        return Ok(HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid image ID".into(),
        }));
    }

    if !file_path.exists() {
        return Ok(HttpResponse::NotFound().json(ErrorResponse {
            error: "Image not found".into(),
        }));
    }

    let file = web::block(|| std::fs::read(&file_path)).await?;
    let mime_type = mime_guess::from_path(&file_path).first_or_octet_stream();

    Ok(HttpResponse::Ok()
        .content_type(mime_type.as_ref())
        .body(file))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .route("/upload", web::post().to(upload_image))
            .route("/images/{imageId}", web::get().to(get_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}