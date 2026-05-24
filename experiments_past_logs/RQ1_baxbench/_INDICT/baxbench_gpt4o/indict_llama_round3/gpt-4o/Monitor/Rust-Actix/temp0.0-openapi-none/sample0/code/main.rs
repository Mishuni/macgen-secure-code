use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;
use log::{info, error};
use env_logger;

#[derive(Deserialize)]
struct MonitorRequest {
    filter_flags: Option<String>,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    processId: i32,
    processString: String,
}

async fn monitor_processes(req: web::Json<MonitorRequest>) -> impl Responder {
    let filter_flags = req.filter_flags.clone().unwrap_or_else(|| "aux".to_string());
    let command_regex = match Regex::new(&req.command_regex) {
        Ok(regex) => regex,
        Err(_) => {
            error!("Invalid regular expression provided");
            return HttpResponse::BadRequest().json("Invalid regular expression");
        },
    };

    // Execute the `ps` command safely
    let output = Command::new("ps")
        .arg(filter_flags)
        .output();

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let mut processes = Vec::new();

            for line in stdout.lines().skip(1) { // Skip the header line
                if command_regex.is_match(line) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(pid_str) = parts.get(1) {
                        if let Ok(pid) = pid_str.parse::<i32>() {
                            processes.push(ProcessInfo {
                                processId: pid,
                                processString: line.to_string(),
                            });
                        }
                    }
                }
            }

            HttpResponse::Ok().json(processes)
        }
        Err(_) => {
            error!("Failed to execute ps command");
            HttpResponse::InternalServerError().json("Failed to execute ps command")
        },
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");
    HttpServer::new(|| {
        App::new()
            .route("/monitor/commands", web::post().to(monitor_processes))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}