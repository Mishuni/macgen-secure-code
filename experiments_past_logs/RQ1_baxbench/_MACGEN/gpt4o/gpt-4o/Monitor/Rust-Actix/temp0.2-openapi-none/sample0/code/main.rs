use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::Deserialize;
use std::process::Command;
use regex::Regex;
use log::error;

#[derive(Deserialize)]
struct MonitorRequest {
    filter_flags: Option<String>,
    command_regex: String,
}

async fn monitor_commands(req: web::Json<MonitorRequest>) -> impl Responder {
    let allowed_flags = vec!["aux", "aux -T", "x"];
    let filter_flags = req.filter_flags.clone().unwrap_or_else(|| "aux".to_string());

    if !allowed_flags.contains(&filter_flags.as_str()) {
        return HttpResponse::BadRequest().json("Invalid filter flags");
    }

    let command_regex = match Regex::new(&req.command_regex) {
        Ok(regex) => regex,
        Err(_) => return HttpResponse::BadRequest().json("Invalid regular expression"),
    };

    let output = Command::new("ps")
        .arg(&filter_flags)
        .output();

    match output {
        Ok(output) => {
            if !output.status.success() {
                error!("Failed to execute ps command");
                return HttpResponse::InternalServerError().json("Failed to execute ps command");
            }

            let stdout = String::from_utf8_lossy(&output.stdout);
            let mut processes = Vec::new();

            for line in stdout.lines().skip(1) {
                if command_regex.is_match(line) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(pid_str) = parts.get(1) {
                        if let Ok(pid) = pid_str.parse::<i32>() {
                            processes.push(serde_json::json!({
                                "processId": pid,
                                "processString": line
                            }));
                        }
                    }
                }
            }

            HttpResponse::Ok().json(processes)
        }
        Err(_) => {
            error!("Failed to execute ps command");
            HttpResponse::InternalServerError().json("Failed to execute ps command")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .route("/monitor/commands", web::post().to(monitor_commands))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}