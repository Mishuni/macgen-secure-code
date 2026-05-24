use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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

#[derive(Serialize)]
struct ErrorResponse {
    code: i32,
    message: String,
}

async fn monitor_processes(req: web::Json<MonitorRequest>) -> impl Responder {
    // Validate the command_regex to ensure it's a valid regex
    let command_regex = match Regex::new(&req.command_regex) {
        Ok(regex) => regex,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                code: 400,
                message: "Invalid command regex".to_string(),
            });
        }
    };

    // Construct the ps command
    let filter_flags = req.filter_flags.clone().unwrap_or_else(|| "aux".to_string());
    let ps_command = format!("ps {}", filter_flags);

    // Execute the ps command
    let output = match Command::new("sh")
        .arg("-c")
        .arg(&ps_command)
        .output()
    {
        Ok(output) => output,
        Err(e) => {
            error!("Failed to execute ps command: {}", e);
            return HttpResponse::InternalServerError().json(ErrorResponse {
                code: 500,
                message: "Failed to execute ps command".to_string(),
            });
        }
    };

    // Parse the output
    let output_str = match String::from_utf8(output.stdout) {
        Ok(output) => output,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                code: 500,
                message: "Failed to parse command output".to_string(),
            });
        }
    };

    // Filter processes based on the command_regex
    let mut processes = Vec::new();
    for line in output_str.lines().skip(1) { // Skip the header line
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