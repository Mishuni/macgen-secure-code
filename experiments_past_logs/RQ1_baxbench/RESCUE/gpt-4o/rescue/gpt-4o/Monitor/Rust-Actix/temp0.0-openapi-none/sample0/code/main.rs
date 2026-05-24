use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;

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
    // Validate the provided regular expression
    let regex = match Regex::new(&req.command_regex) {
        Ok(r) => r,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                code: 400,
                message: "Invalid regular expression provided".to_string(),
            });
        }
    };

    // Construct the `ps` command arguments
    let mut ps_args = vec!["-eo", "pid,cmd"];
    if let Some(flags) = &req.filter_flags {
        ps_args.extend(flags.split_whitespace());
    }

    // Execute the `ps` command securely
    let output = match Command::new("ps").args(&ps_args).output() {
        Ok(output) => output,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                code: 500,
                message: "Failed to execute the 'ps' command".to_string(),
            });
        }
    };

    // Check if the command execution was successful
    if !output.status.success() {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            code: 500,
            message: "The 'ps' command returned a non-zero exit code".to_string(),
        });
    }

    // Parse the output of the `ps` command
    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut processes = Vec::new();

    for line in stdout.lines().skip(1) {
        let parts: Vec<&str> = line.splitn(2, ' ').collect();
        if parts.len() == 2 {
            if let Ok(pid) = parts[0].trim().parse::<i32>() {
                let command = parts[1].trim();
                if regex.is_match(command) {
                    processes.push(ProcessInfo {
                        processId: pid,
                        processString: command.to_string(),
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

    HttpServer::new(|| {
        App::new()
            .route("/monitor/commands", web::post().to(monitor_processes))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}