use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use uuid::Uuid;
use serde::Serialize;
use std::sync::Mutex;
use std::collections::HashMap;

#[derive(Serialize)]
struct UploadResponse {
    id: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

struct AppState {
    images: Mutex<HashMap<String, PathBuf>>,
}

async fn upload_image(
    mut payload: Multipart,
    data: web::Data<AppState>,
) -> impl Responder {
    let allowed_types = ["image/jpeg", "image/png", "image/gif"];
    let mut file_path = None;

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_type = field.content_type().to_string();
        if !allowed_types.contains(&content_type.as_str()) {
            return HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid file type".to_string() });
        }

        let filename = field
            .content_disposition()
            .get_filename()
            .map(|f| f.to_string())
            .unwrap_or_else(|| "file".to_string());

        let id = Uuid::new_v4().to_string();
        let original_extension = filename.split('.').last().unwrap_or("bin");
        let sanitized_filename = format!("{}.{}", id, original_extension);
        let temp_dir = std::env::temp_dir();
        let file_path_buf = temp_dir.join(sanitized_filename);
        file_path = Some(file_path_buf.clone());

        let mut f = web::block(|| std::fs::File::create(&file_path_buf))
            .await
            .map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to create file".to_string() }))?;

        while let Some(chunk) = field.next().await {
            let data = chunk.map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to read chunk".to_string() }))?;
            f = web::block(move || f.write_all(&data)).await.map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to write to file".to_string() }))?;
        }

        data.images.lock().unwrap().insert(id.clone(), file_path_buf);
        return HttpResponse::Ok().json(UploadResponse { id });
    }

    HttpResponse::BadRequest().json(ErrorResponse { error: "No file uploaded".to_string() })
}

async fn share_image(image_id: web::Path<String>, data: web::Data<AppState>) -> impl Responder {
    let images = data.images.lock().unwrap();
    if let Some(file_path) = images.get(&image_id.into_inner()) {
        let content_type = mime_guess::from_path(file_path).first_or_octet_stream();
        return HttpResponse::Ok()
            .content_type(content_type)
            .body(fs::read(file_path).map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to read file".to_string() }))?);
    }
    HttpResponse::NotFound().json(ErrorResponse { error: "Image not found".to_string() })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let state = web::Data::new(AppState {
        images: Mutex::new(HashMap::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/upload", web::post().to(upload_image))
            .route("/images/{imageId}", web::get().to(share_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}