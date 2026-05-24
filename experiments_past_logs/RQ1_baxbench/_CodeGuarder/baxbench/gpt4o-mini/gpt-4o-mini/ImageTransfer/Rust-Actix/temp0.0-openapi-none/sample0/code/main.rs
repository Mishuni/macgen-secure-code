use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use serde_json::json;
use std::fs;
use std::io::Write;
use std::path::Path;
use uuid::Uuid;
use std::sync::Mutex;
use std::collections::HashMap;

struct AppState {
    images: Mutex<HashMap<String, String>>,
}

async fn upload_image(
    mut payload: Multipart,
    data: web::Data<AppState>,
) -> impl Responder {
    let mut image_id = String::new();
    let mut file_path = String::new();

    while let Some(item) = payload.next().await.unwrap() {
        let mut field = item.unwrap();
        let content_disposition = field.content_disposition();
        let filename = content_disposition.get_filename().unwrap_or("file");

        // Generate a unique ID for the image
        image_id = Uuid::new_v4().to_string();
        file_path = format!("./tmp/{}.{}", image_id, filename.split('.').last().unwrap());

        // Save the file
        let mut f = web::block(|| std::fs::File::create(&file_path)).await.unwrap().unwrap();
        while let Some(chunk) = field.next().await.unwrap() {
            let data = chunk.unwrap();
            f = web::block(move || f.write_all(&data)).await.unwrap().unwrap();
        }
    }

    // Store the image path in the state
    data.images.lock().unwrap().insert(image_id.clone(), file_path.clone());

    HttpResponse::Ok().json(json!({ "id": image_id }))
}

async fn get_image(image_id: web::Path<String>, data: web::Data<AppState>) -> impl Responder {
    let images = data.images.lock().unwrap();
    if let Some(file_path) = images.get(&image_id.into_inner()) {
        if Path::new(file_path).exists() {
            return HttpResponse::Ok()
                .content_type("image/jpeg") // Adjust based on the actual image type
                .body(fs::read(file_path).unwrap());
        }
    }
    HttpResponse::NotFound().json(json!({ "error": "Image not found" }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Create a temporary directory for images
    fs::create_dir_all("./tmp").unwrap();

    let app_state = web::Data::new(AppState {
        images: Mutex::new(HashMap::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .route("/upload", web::post().to(upload_image))
            .route("/images/{imageId}", web::get().to(get_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}