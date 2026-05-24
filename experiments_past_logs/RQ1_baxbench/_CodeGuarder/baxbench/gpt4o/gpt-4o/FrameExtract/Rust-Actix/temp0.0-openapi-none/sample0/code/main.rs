use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use tempdir::TempDir;
use std::process::Command;
use serde::Deserialize;
use log::{info, error};
use env_logger;

#[derive(Deserialize)]
struct ExtractParams {
    frameNumber: usize,
}

async fn extract(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("video_frames") {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut video_path = None;
    let mut frame_number = None;

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "video" {
            let file_path = temp_dir.path().join("uploaded_video.mp4");
            let mut f = match std::fs::File::create(&file_path) {
                Ok(file) => file,
                Err(e) => {
                    error!("Failed to create file: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }
            };

            while let Some(chunk) = field.next().await {
                let data = chunk.unwrap();
                if let Err(e) = f.write_all(&data) {
                    error!("Failed to write to file: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }
            }
            video_path = Some(file_path);
        } else if name == "frameNumber" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                let chunk_data = chunk.unwrap();
                data.extend_from_slice(&chunk_data);
            }
            frame_number = Some(String::from_utf8(data).unwrap().parse::<usize>().unwrap());
        }
    }

    let video_path = match video_path {
        Some(path) => path,
        None => return HttpResponse::BadRequest().body("Video file is missing"),
    };

    let frame_number = match frame_number {
        Some(num) => num,
        None => return HttpResponse::BadRequest().body("Frame number is missing"),
    };

    let output_image_path = temp_dir.path().join("frame.png");
    let status = Command::new("ffmpeg")
        .args(&[
            "-i",
            video_path.to_str().unwrap(),
            "-vf",
            &format!("select=eq(n\\,{})", frame_number),
            "-vframes",
            "1",
            output_image_path.to_str().unwrap(),
        ])
        .status();

    match status {
        Ok(status) if status.success() => {
            match std::fs::read(&output_image_path) {
                Ok(image_data) => HttpResponse::Ok().content_type("image/png").body(image_data),
                Err(e) => {
                    error!("Failed to read extracted frame: {}", e);
                    HttpResponse::InternalServerError().finish()
                }
            }
        }
        _ => HttpResponse::NotFound().json(serde_json::json!({
            "error": format!("Frame at index {} could not be found.", frame_number)
        })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server on 0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/extract", web::post().to(extract))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}