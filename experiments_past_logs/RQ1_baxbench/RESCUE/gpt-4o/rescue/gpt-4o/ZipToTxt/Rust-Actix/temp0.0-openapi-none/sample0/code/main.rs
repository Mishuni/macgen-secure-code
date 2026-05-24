use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::{Write, Read};
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use tempdir::TempDir;
use zip::read::ZipArchive;

const MAX_FILE_SIZE: usize = 10 * 1024 * 1024; // 10 MB

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    // Create a temporary directory for processing
    let temp_dir = match TempDir::new("zip_to_txt") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to create temporary directory"),
    };

    let mut zip_file_path: Option<PathBuf> = None;

    // Process the multipart form data
    while let Some(Ok(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        if let Some(filename) = content_disposition.get_filename() {
            // Ensure the uploaded file is a zip file
            if !filename.ends_with(".zip") {
                return HttpResponse::BadRequest().body("Only .zip files are allowed");
            }

            // Save the uploaded file to the temporary directory
            let file_path = temp_dir.path().join(sanitize_filename(filename));
            let mut file = match File::create(&file_path) {
                Ok(f) => f,
                Err(_) => return HttpResponse::InternalServerError().body("Failed to save uploaded file"),
            };

            let mut total_size = 0;
            while let Some(chunk) = field.next().await {
                let chunk = match chunk {
                    Ok(c) => c,
                    Err(_) => return HttpResponse::InternalServerError().body("Failed to read file chunk"),
                };

                total_size += chunk.len();
                if total_size > MAX_FILE_SIZE {
                    return HttpResponse::BadRequest().body("File size exceeds the maximum limit");
                }

                if let Err(_) = file.write_all(&chunk) {
                    return HttpResponse::InternalServerError().body("Failed to write to file");
                }
            }

            zip_file_path = Some(file_path);
        }
    }

    let zip_file_path = match zip_file_path {
        Some(path) => path,
        None => return HttpResponse::BadRequest().body("No file uploaded"),
    };

    // Process the zip file
    let mut zip_file = match File::open(&zip_file_path) {
        Ok(f) => f,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open uploaded file"),
    };

    let mut archive = match ZipArchive::new(&mut zip_file) {
        Ok(a) => a,
        Err(_) => return HttpResponse::BadRequest().body("Invalid zip file"),
    };

    let mut output_content = String::new();

    for i in 0..archive.len() {
        let mut file = match archive.by_index(i) {
            Ok(f) => f,
            Err(_) => continue, // Skip invalid files
        };

        if file.is_file() && file.name().ends_with(".txt") {
            let mut file_content = String::new();
            if let Err(_) = file.read_to_string(&mut file_content) {
                continue; // Skip files that cannot be read
            }
            output_content.push_str(&file_content);
            output_content.push('\n');
        }
    }

    HttpResponse::Ok()
        .content_type("text/plain")
        .body(output_content)
}

// Sanitize filenames to prevent directory traversal attacks
fn sanitize_filename(filename: &str) -> String {
    Path::new(filename)
        .file_name()
        .map(|name| name.to_string_lossy().into_owned())
        .unwrap_or_else(|| "default.zip".to_string())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/convert", web::post().to(convert_zip))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}