use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::process::Command;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use serde_json::json;
use log::{info, error};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/extract", web::post().to(extract_frame))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn extract_frame(mut payload: Multipart) -> impl Responder {
    let mut video_file_name = String::new();
    let mut frame_number: Option<u32> = None;
    let mut video_data: Vec<u8> = Vec::new();

    while let Some(field) = payload.next().await.unwrap() {
        let content_type = field.content_type().to_string();
        match field.name() {
            "videoFileName" => {
                video_file_name = field.map(|f| f.to_string()).unwrap_or_default();
            }
            "frameNumber" => {
                frame_number = field
                    .map(|f| f.parse::<u32>().ok())
                    .unwrap_or_default();
            }
            "video" => {
                let mut file = tempfile::NamedTempFile::new().unwrap();
                while let Some(chunk) = field.next().await.unwrap() {
                    let data = chunk.unwrap();
                    file.write_all(&data).unwrap();
                }
                video_data = file.into_temp_path().into_vec();
            }
            _ => {}
        }
    }

    if let Some(frame_number) = frame_number {
        let output_image_path = format!("frame_{}.png", frame_number);
        let status = Command::new("ffmpeg")
            .args(&[
                "-i",
                &video_file_name,
                "-vf",
                &format!("select=eq(n\\,{})", frame_number),
                "-vframes",
                "1",
                &output_image_path,
            ])
            .output()
            .expect("Failed to execute ffmpeg");

        if status.status.success() {
            info!("Frame extracted successfully: {}", output_image_path);
            let image_data = std::fs::read(&output_image_path).unwrap();
            return HttpResponse::Ok()
                .content_type("image/png")
                .body(image_data);
        } else {
            error!("Failed to extract frame: {:?}", status);
            return HttpResponse::NotFound().json(json!({
                "error": format!("Frame at index {} could not be found.", frame_number)
            }));
        }
    }

    HttpResponse::BadRequest().json(json!({
        "error": "Invalid frame number."
    }))
}