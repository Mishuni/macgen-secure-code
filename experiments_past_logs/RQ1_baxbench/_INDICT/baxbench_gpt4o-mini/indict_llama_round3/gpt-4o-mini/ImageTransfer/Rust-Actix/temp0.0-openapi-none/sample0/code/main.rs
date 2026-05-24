use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use uuid::Uuid;
use serde_json::json;
use mime_guess::from_path;

#[derive(Debug)]
struct AppState {
    upload_dir: String,
}

async fn upload_image(
    mut payload: Multipart,
    data: web::Data<AppState>,
) -> impl Responder {
    while let Ok(Some(mut field)) = payload.try_next().await {
        let filename = field
            .content_disposition()
            .get_filename()
            .map(|f| f.to_string())
            .unwrap_or_else(|| "file".to_string());

        // Validate file type
        let mime_type = from_path(&filename).first().unwrap_or(mime_guess::mime::IMAGE_JPEG);
        if !mime_type.type_().starts_with("image/") {
            return HttpResponse::BadRequest().json(json!({ "error": "Invalid file type" }));
        }

        let unique_id = Uuid::new_v4().to_string();
        let file_extension = mime_type.extension().unwrap_or("jpg"); // Default to jpg if unknown
        let file_path = format!("{}/{}.{}", data.upload_dir, unique_id, file_extension);

        let mut f = web::block(|| std::fs::File::create(&file_path)).await.unwrap().unwrap();
        while let Some(chunk) = field.next().await {
            let data = chunk.unwrap();
            f = web::block(move || f.write_all(&data)).await.unwrap().unwrap();
        }

        return HttpResponse::Ok().json(json!({ "id": unique_id }));
    }

    HttpResponse::BadRequest().json(json!({ "error": "Invalid input" }))
}

async fn share_image(image_id: web::Path<String>, data: web::Data<AppState>) -> impl Responder {
    let file_path = format!("{}/{}.jpg", data.upload_dir, image_id); // Assuming jpg for simplicity

    if Path::new(&file_path).exists() {
        let file = fs::read(file_path).unwrap();
        let mime_type = from_path(&file_path).first().unwrap_or(mime_guess::mime::IMAGE_JPEG);
        HttpResponse::Ok()
            .content_type(mime_type.as_ref())
            .body(file)
    } else {
        HttpResponse::NotFound().json(json!({ "error": "Image not found" }))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let upload_dir = "uploads";
    fs::create_dir_all(upload_dir).unwrap();

    let state = web::Data::new(AppState {
        upload_dir: upload_dir.to_string(),
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