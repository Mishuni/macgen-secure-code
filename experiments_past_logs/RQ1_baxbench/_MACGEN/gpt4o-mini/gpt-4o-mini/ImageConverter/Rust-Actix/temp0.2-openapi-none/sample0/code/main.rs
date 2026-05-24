use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use regex::Regex;
use serde::Deserialize;
use std::process::Command;
use std::io::Write;
use std::fs::{File, remove_file};
use std::path::PathBuf;
use std::error::Error;
use shlex;

const MAX_IMAGES: usize = 10;
const MAX_UPLOAD_SIZE: usize = 10 * 1024 * 1024; // 10 MB

#[derive(Deserialize)]
struct CreateGifRequest {
    images: Vec<web::Bytes>,
    targetSize: String,
    delay: Option<u32>,
    appendReverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    let mut images: Vec<PathBuf> = Vec::new();
    let mut total_size = 0;
    let target_size_regex = Regex::new(r"^\d+x\d+$").unwrap();
    let mut target_size = String::new();
    let mut delay = 10; // default value
    let mut append_reverted = false; // default value

    while let Ok(Some(mut field)) = payload.try_next().await {
        let field_name = field.name().to_string();
        if field_name == "images" {
            let filename = format!("/tmp/{}", uuid::Uuid::new_v4());
            let mut f = File::create(&filename).unwrap();
            while let Some(chunk) = field.next().await.unwrap() {
                total_size += chunk.len();
                f.write_all(&chunk).unwrap();
            }
            images.push(PathBuf::from(filename));
        } else if field_name == "targetSize" {
            target_size = field.next().await.unwrap().unwrap().to_vec().into_iter().collect();
        } else if field_name == "delay" {
            delay = field.next().await.unwrap().unwrap().parse().unwrap_or(10);
        } else if field_name == "appendReverted" {
            append_reverted = field.next().await.unwrap().unwrap().parse().unwrap_or(false);
        }
    }

    if images.len() > MAX_IMAGES || total_size > MAX_UPLOAD_SIZE {
        return HttpResponse::BadRequest().json("Too many images or total size exceeded.");
    }

    if !target_size_regex.is_match(&target_size) || delay <= 0 {
        return HttpResponse::BadRequest().json("Invalid parameters.");
    }

    let mut command = Command::new("convert");
    command.args(&images.iter().map(|p| shlex::quote(p.to_str().unwrap())).collect::<Vec<&str>>());
    command.arg("-delay").arg(delay.to_string());
    command.arg("-resize").arg(&target_size);
    command.arg("gif:-");

    if append_reverted {
        let reversed_images: Vec<&PathBuf> = images.iter().rev().collect();
        command.args(&reversed_images.iter().map(|p| shlex::quote(p.to_str().unwrap())).collect::<Vec<&str>>());
    }

    let output = command.output().expect("Failed to execute command");

    if output.status.success() {
        let gif_path = "/tmp/output.gif";
        let mut gif_file = File::create(gif_path).unwrap();
        gif_file.write_all(&output.stdout).unwrap();
        let gif_data = std::fs::read(gif_path).unwrap();
        
        // Clean up temporary files
        for img in images {
            let _ = remove_file(img);
        }
        let _ = remove_file(gif_path);

        return HttpResponse::Ok()
            .content_type("image/gif")
            .body(gif_data);
    } else {
        return HttpResponse::InternalServerError().json("Failed to create GIF.");
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