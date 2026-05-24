use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use uuid::Uuid;
use std::fs;
use std::path::PathBuf;
use serde::{Serialize, Deserialize};
use std::sync::Mutex;
use std::collections::HashMap;
use actix_web::web::Data;
use mime_guess;

#[derive(Serialize, Deserialize)]
struct ImageResponse {
    id: String,
}

#[derive(Serialize, Deserialize)]
struct ErrorResponse {
    error: String,
}

struct AppState {
    images: Mutex<HashMap<String, PathBuf>>,
}

async fn upload_image(
    mut payload: Multipart,
    data: Data<AppState>,
) -> Result<HttpResponse, Error> {
    let mut file_path = None;

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().ok_or_else(|| HttpResponse::BadRequest().json(ErrorResponse { error: "Filename missing".to_string() }))?;
        let file_extension = PathBuf::from(filename).extension().unwrap().to_str().unwrap();

        let upload_dir = std::env::var("UPLOAD_DIR").unwrap_or_else(|_| "/secure/uploads".to_string());
        let file_id = Uuid::new_v4().to_string();
        let file_name = format!("{}.{}", file_id, file_extension);
        let file_path_buf = PathBuf::from(&upload_dir).join(file_name);
        file_path = Some(file_path_buf.clone());

        let mut f = fs::File::create(&file_path_buf)?;
        while let Some(chunk) = field.next().await {
            let data = chunk?;
            f.write_all(&data)?;
        }

        let mut images = data.images.lock().unwrap();
        images.insert(file_id.clone(), file_path_buf);
    }

    if let Some(file_path) = file_path {
        let file_id = file_path.file_stem().unwrap().to_str().unwrap().to_string();
        Ok(HttpResponse::Ok().json(ImageResponse { id: file_id }))
    } else {
        Ok(HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid input".to_string() }))
    }
}

async fn get_image(
    path: web::Path<String>,
    data: Data<AppState>,
) -> impl Responder {
    let image_id = path.into_inner();
    let images = data.images.lock().unwrap();

    if let Some(file_path) = images.get(&image_id) {
        if let Ok(image_data) = fs::read(file_path) {
            let mime_type = mime_guess::from_path(file_path).first_or_octet_stream();
            return HttpResponse::Ok()
                .content_type(mime_type.as_ref())
                .body(image_data);
        }
    }

    HttpResponse::NotFound().json(ErrorResponse { error: "Image not found".to_string() })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_state = Data::new(AppState {
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