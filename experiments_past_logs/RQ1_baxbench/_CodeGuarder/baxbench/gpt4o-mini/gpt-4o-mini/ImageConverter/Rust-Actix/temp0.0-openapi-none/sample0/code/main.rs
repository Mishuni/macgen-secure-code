use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs;
use std::process::Command;
use std::path::PathBuf;
use serde::Deserialize;
use log::{error, info};
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Deserialize)]
struct GifRequest {
    targetSize: String,
    delay: Option<u32>,
    appendReverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart, params: web::Json<GifRequest>) -> impl Responder {
    let mut images: Vec<PathBuf> = Vec::new();
    let target_size = &params.targetSize;
    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.appendReverted.unwrap_or(false);

    while let Ok(Some(mut field)) = payload.try_next().await {
        let filename = field
            .content_disposition()
            .get_filename()
            .map(|f| f.to_string())
            .unwrap_or_else(|| "temp_image".to_string());

        let filepath = format!("./tmp/{}", filename);
        let filepath = PathBuf::from(filepath);

        // Save the file
        let mut f = fs::File::create(&filepath).unwrap();
        while let Some(chunk) = field.next().await {
            let data = chunk.unwrap();
            f.write_all(&data).unwrap();
        }
        images.push(filepath);
    }

    // Validate target size
    let size_parts: Vec<&str> = target_size.split('x').collect();
    if size_parts.len() != 2 {
        return HttpResponse::BadRequest().json("Invalid target size format. Use 'widthxheight'.");
    }

    let width: u32 = size_parts[0].parse().unwrap_or(0);
    let height: u32 = size_parts[1].parse().unwrap_or(0);
    if width == 0 || height == 0 {
        return HttpResponse::BadRequest().json("Width and height must be positive integers.");
    }

    // Create the GIF using ImageMagick
    let mut command = Command::new("convert");
    for image in &images {
        command.arg(image);
    }
    command.arg("-resize").arg(target_size);
    command.arg("-delay").arg(delay.to_string());
    command.arg("output.gif");

    if let Err(e) = command.output() {
        error!("Failed to create GIF: {}", e);
        return HttpResponse::InternalServerError().json("Failed to create GIF.");
    }

    // Handle appending reverted images if required
    if append_reverted {
        let reversed_images: Vec<PathBuf> = images.iter().rev().cloned().collect();
        for image in reversed_images {
            command.arg(image);
        }
        command.arg("output.gif");
        if let Err(e) = command.output() {
            error!("Failed to append reverted images: {}", e);
            return HttpResponse::InternalServerError().json("Failed to append reverted images.");
        }
    }

    // Clean up temporary files
    for image in images {
        let _ = fs::remove_file(image);
    }

    HttpResponse::Ok().content_type("image/gif").body(fs::read("output.gif").unwrap())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}