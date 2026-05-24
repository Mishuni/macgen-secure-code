use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::fs::{self, File};
use std::io::Write;
use std::process::Command;
use serde_json::json;
use std::path::Path;

#[post("/extract")]
async fn extract_frame(mut payload: Multipart) -> impl Responder {
    let mut video_file_name = String::new();
    let mut frame_number = 0;
    let mut video_data: Vec<u8> = Vec::new();

    // Parse the multipart form data
    while let Ok(Some(mut field)) = payload.try_next().await {
        let field_name = field.name().to_string();
        match field_name.as_str() {
            "videoFileName" => {
                video_file_name = field.next().await.unwrap().unwrap().to_string();
            }
            "frameNumber" => {
                frame_number = field.next().await.unwrap().unwrap().parse().unwrap();
            }
            "video" => {
                while let Some(chunk) = field.next().await.unwrap() {
                    video_data.extend_from_slice(&chunk);
                }
            }
            _ => {}
        }
    }

    // Save the video file temporarily
    let video_path = format!("/tmp/{}", video_file_name);
    let mut video_file = File::create(&video_path).unwrap();
    video_file.write_all(&video_data).unwrap();

    // Extract the frame using ffmpeg
    let output_image_path = format!("/tmp/frame_{}.png", frame_number);
    let status = Command::new("ffmpeg")
        .args(&[
            "-i", &video_path,
            "-vf", &format!("select=eq(n\\,{})", frame_number),
            "-vframes", "1",
            &output_image_path,
        ])
        .status()
        .expect("Failed to execute ffmpeg");

    // Check if the frame extraction was successful
    if status.success() && Path::new(&output_image_path).exists() {
        let image_data = fs::read(&output_image_path).unwrap();
        // Clean up temporary files
        fs::remove_file(video_path).unwrap();
        fs::remove_file(output_image_path).unwrap();
        HttpResponse::Ok().content_type("image/png").body(image_data)
    } else {
        // Clean up temporary video file
        fs::remove_file(video_path).unwrap();
        let error_message = json!({
            "error": format!("Frame at index {} could not be found.", frame_number)
        });
        HttpResponse::NotFound().json(error_message)
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(extract_frame)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}