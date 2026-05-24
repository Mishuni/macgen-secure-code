use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{self, File};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use uuid::Uuid;
use mime_guess::mime;

const UPLOAD_DIR: &str = "uploads";
const MAX_FILE_SIZE: u64 = 5 * 1024 * 1024; // 5 MB

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Create the uploads directory if it doesn't exist
    fs::create_dir_all(UPLOAD_DIR)?;

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
    let mut file_id = String::new();

    while let Ok(Some(mut field)) = payload.try_next().await {
        // Validate file type and size
        let content_type = field.content_type().to_string();
        if !is_valid_file_type(&content_type) {
            return HttpResponse::BadRequest().json(serde_json::json!({ "error": "Invalid file type" }));
        }

        let mut file_size = 0;
        let file_path = format!("{}/{}.tmp", UPLOAD_DIR, Uuid::new_v4());

        // Save the file
        let mut f = match File::create(&file_path) {
            Ok(file) => file,
            Err(_) => return HttpResponse::InternalServerError().json(serde_json::json!({ "error": "Failed to create file" })),
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(_) => return HttpResponse::InternalServerError().json(serde_json::json!({ "error": "Failed to read file chunk" })),
            };

            file_size += data.len() as u64;
            if file_size > MAX_FILE_SIZE {
                return HttpResponse::PayloadTooLarge().json(serde_json::json!({ "error": "File size exceeds limit" }));
            }

            if let Err(_) = f.write_all(&data) {
                return HttpResponse::InternalServerError().json(serde_json::json!({ "error": "Failed to write to file" }));
            }
        }

        file_id = Path::new(&file_path).file_stem().unwrap().to_str().unwrap().to_string();
    }

    // Return the file ID as a JSON response
    HttpResponse::Ok().json(serde_json::json!({ "id": file_id }))
}

async fn share_image(web::Path(image_id): web::Path<String>) -> impl Responder {
    // Sanitize image_id to prevent path traversal
    let sanitized_image_id = sanitize_image_id(&image_id);
    let file_path = format!("{}/{}.tmp", UPLOAD_DIR, sanitized_image_id);

    // Check if the file exists
    if !PathBuf::from(&file_path).exists() {
        return HttpResponse::NotFound().json(serde_json::json!({ "error": "Image not found" }));
    }

    // Serve the image file
    let file = match File::open(&file_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::InternalServerError().json(serde_json::json!({ "error": "Failed to open file" })),
    };

    let mime_type = mime::from_path(&file_path).first_or(mime::APPLICATION_OCTET_STREAM);
    HttpResponse::Ok()
        .content_type(mime_type)
        .body(actix_web::web::Bytes::from(file))
}

fn is_valid_file_type(content_type: &str) -> bool {
    let valid_types = ["image/jpeg", "image/png", "image/gif"];
    valid_types.contains(&content_type)
}

// Sanitize image_id to prevent path traversal
fn sanitize_image_id(image_id: &str) -> String {
    image_id.replace("../", "").replace("./", "").replace("..\\", "").replace(".\\", "")
}