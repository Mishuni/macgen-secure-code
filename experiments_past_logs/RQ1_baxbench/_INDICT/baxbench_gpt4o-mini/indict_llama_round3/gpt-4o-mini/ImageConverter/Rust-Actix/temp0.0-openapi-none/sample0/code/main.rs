use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::StreamExt;
use std::process::Command;
use std::fs::{self, File};
use std::io::Write;
use std::path::PathBuf;
use serde::Deserialize;

#[derive(Deserialize)]
struct GifRequest {
    targetSize: String,
    delay: Option<u32>,
    appendReverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    let mut images: Vec<PathBuf> = Vec::new();
    let mut target_size = String::new();
    let mut delay = 10; // default delay
    let mut append_reverted = false; // default append_reverted

    while let Ok(Some(mut field)) = payload.next().await {
        let field_name = field.name().to_string();
        if field_name == "images" {
            let filename = field.filename().unwrap_or("image").to_string();
            let filepath = format!("/tmp/{}", filename);
            let mut f = File::create(&filepath).unwrap();
            while let Some(chunk) = field.next().await {
                let data = chunk.unwrap();
                f.write_all(&data).unwrap();
            }
            images.push(PathBuf::from(filepath));
        } else if field_name == "targetSize" {
            target_size = field.next().await.unwrap().unwrap().to_string();
        } else if field_name == "delay" {
            delay = field.next().await.unwrap().unwrap().parse().unwrap_or(10);
        } else if field_name == "appendReverted" {
            append_reverted = field.next().await.unwrap().unwrap().parse().unwrap_or(false);
        }
    }

    // Validate target size format
    if !target_size.contains('x') {
        return HttpResponse::BadRequest().json(serde_json::json!({ "error": "Invalid target size format. Use 'widthxheight'." }));
    }

    // Create GIF command
    let mut command = Command::new("convert");
    command.args(&images);
    command.arg("-delay").arg(delay.to_string());
    command.arg("-resize").arg(&target_size);
    command.arg("gif:-");

    if append_reverted {
        let reversed_images: Vec<_> = images.iter().rev().cloned().collect();
        command.args(&reversed_images);
    }

    // Execute command and capture output
    let output = command.output().expect("Failed to execute command");
    if output.status.success() {
        let gif_path = "/tmp/output.gif";
        let mut gif_file = File::create(gif_path).unwrap();
        gif_file.write_all(&output.stdout).unwrap();
        let gif_data = fs::read(gif_path).unwrap();
        fs::remove_file(gif_path).unwrap(); // Clean up
        for image in images {
            fs::remove_file(image).unwrap(); // Clean up uploaded images
        }
        HttpResponse::Ok().content_type("image/gif").body(gif_data)
    } else {
        let error_message = String::from_utf8_lossy(&output.stderr);
        HttpResponse::InternalServerError().json(serde_json::json!({ "error": error_message.to_string() }))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}