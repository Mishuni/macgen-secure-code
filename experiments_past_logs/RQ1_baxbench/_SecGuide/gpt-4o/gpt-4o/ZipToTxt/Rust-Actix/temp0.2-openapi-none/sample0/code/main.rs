use actix_multipart::Multipart;
use actix_web::{web, App, Error, HttpResponse, HttpServer, Responder};
use futures_util::stream::StreamExt as _;
use std::io::{Read, Write};
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use tempfile::Builder;
use zip::read::ZipArchive;
use log::{info, error};
use uuid::Uuid;

async fn convert_zip(mut payload: Multipart) -> Result<HttpResponse, Error> {
    // Create a secure temporary directory
    let temp_dir = Builder::new().prefix("zip_to_txt").tempdir().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        actix_web::error::ErrorInternalServerError("Internal Server Error")
    })?;
    let temp_file_path = temp_dir.path().join(format!("{}.zip", Uuid::new_v4()));
    let mut temp_file = File::create(&temp_file_path)?;

    // Limit the size of the uploaded file to prevent DoS
    const MAX_SIZE: usize = 10 * 1024 * 1024; // 10 MB
    let mut total_size = 0;

    while let Some(item) = payload.next().await {
        let mut field = item?;
        while let Some(chunk) = field.next().await {
            let data = chunk?;
            total_size += data.len();
            if total_size > MAX_SIZE {
                error!("Uploaded file is too large");
                return Err(actix_web::error::ErrorBadRequest("File too large"));
            }
            temp_file.write_all(&data)?;
        }
    }

    let mut zip_file = File::open(&temp_file_path)?;
    let mut archive = ZipArchive::new(&mut zip_file)?;

    let mut result_text = String::new();
    const MAX_DECOMPRESSED_SIZE: usize = 50 * 1024 * 1024; // 50 MB
    let mut decompressed_size = 0;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let file_name = file.name();

        // Validate file names to prevent path traversal
        let file_path = Path::new(file_name);
        if file_path.components().any(|comp| matches!(comp, std::path::Component::ParentDir)) || file_path.is_absolute() {
            error!("Invalid file name detected: {}", file_name);
            return Err(actix_web::error::ErrorBadRequest("Invalid file name"));
        }

        if file_name.ends_with(".txt") {
            let mut contents = String::new();
            file.read_to_string(&mut contents)?;
            decompressed_size += contents.len();
            if decompressed_size > MAX_DECOMPRESSED_SIZE {
                error!("Decompressed content is too large");
                return Err(actix_web::error::ErrorBadRequest("Decompressed content too large"));
            }
            result_text.push_str(&contents);
        }
    }

    info!("Successfully processed ZIP file");
    Ok(HttpResponse::Ok().content_type("text/plain").body(result_text))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init(); // Initialize logging
    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_zip))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}