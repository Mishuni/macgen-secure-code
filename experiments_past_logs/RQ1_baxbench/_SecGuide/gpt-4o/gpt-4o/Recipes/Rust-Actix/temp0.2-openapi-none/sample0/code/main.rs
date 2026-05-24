use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use actix_web::middleware::Logger;
use actix_web::http::header::{ContentType, CONTENT_SECURITY_POLICY, X_CONTENT_TYPE_OPTIONS, X_FRAME_OPTIONS};
use std::env;
use actix_web::middleware::ErrorHandlers;
use actix_web::http::StatusCode;
use actix_web::error::InternalError;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
    avg_rating: Option<f64>,
}

#[derive(Serialize, Deserialize)]
struct Comment {
    comment: String,
}

#[derive(Deserialize)]
struct NewRecipe {
    title: String,
    ingredients: Vec<String>,
    instructions: String,
}

#[derive(Deserialize)]
struct NewComment {
    comment: String,
}

#[derive(Deserialize)]
struct NewRating {
    rating: i32,
}

type DbPool = Pool<SqliteConnectionManager>;

async fn get_recipes(pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().expect("Couldn't get db connection from pool");
    let mut stmt = conn.prepare("SELECT id, title FROM recipes").expect("Failed to prepare statement");
    let recipe_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).expect("Failed to map query");

    let mut recipes = Vec::new();
    for recipe in recipe_iter {
        let (id, title) = recipe.expect("Failed to unwrap recipe");
        recipes.push(format!("<a href=\"/recipes/{}\">{}</a>", id, html_escape::encode_text(&title)));
    }

    HttpResponse::Ok().content_type(ContentType::html()).body(recipes.join("<br>"))
}

async fn upload_recipe(pool: web::Data<DbPool>, new_recipe: web::Json<NewRecipe>) -> impl Responder {
    if new_recipe.title.is_empty() || new_recipe.instructions.is_empty() || new_recipe.ingredients.is_empty() {
        return HttpResponse::BadRequest().body("Invalid input data");
    }

    let conn = pool.get().expect("Couldn't get db connection from pool");
    let id = Uuid::new_v4().to_string();
    let result = conn.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, new_recipe.title, serde_json::to_string(&new_recipe.ingredients).unwrap(), new_recipe.instructions],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(Recipe {
            id,
            title: new_recipe.title.clone(),
            ingredients: new_recipe.ingredients.clone(),
            instructions: new_recipe.instructions.clone(),
            comments: vec![],
            avg_rating: None,
        }),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn get_recipe(pool: web::Data<DbPool>, path: web::Path<String>) -> impl Responder {
    let conn = pool.get().expect("Couldn't get db connection from pool");
    let recipe_id = path.into_inner();
    let mut stmt = conn.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").expect("Failed to prepare statement");
    let recipe = stmt.query_row(params![recipe_id], |row| {
        Ok(Recipe {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: serde_json::from_str(&row.get::<_, String>(1)?).unwrap(),
            instructions: row.get(2)?,
            comments: vec![],
            avg_rating: None,
        })
    });

    match recipe {
        Ok(recipe) => HttpResponse::Ok().content_type(ContentType::html()).body(format!(
            "<h1>{}</h1><p>{}</p><p>{:?}</p>",
            html_escape::encode_text(&recipe.title), 
            html_escape::encode_text(&recipe.instructions), 
            recipe.ingredients.iter().map(|i| html_escape::encode_text(i)).collect::<Vec<_>>()
        )),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(pool: web::Data<DbPool>, path: web::Path<String>, new_comment: web::Json<NewComment>) -> impl Responder {
    if new_comment.comment.is_empty() {
        return HttpResponse::BadRequest().body("Comment cannot be empty");
    }

    let conn = pool.get().expect("Couldn't get db connection from pool");
    let recipe_id = path.into_inner();
    let result = conn.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![recipe_id, new_comment.comment],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn add_rating(pool: web::Data<DbPool>, path: web::Path<String>, new_rating: web::Json<NewRating>) -> impl Responder {
    if new_rating.rating < 1 || new_rating.rating > 5 {
        return HttpResponse::BadRequest().body("Rating must be between 1 and 5");
    }

    let conn = pool.get().expect("Couldn't get db connection from pool");
    let recipe_id = path.into_inner();
    let result = conn.execute(
        "INSERT INTO ratings (recipe_id, rating) VALUES (?1, ?2)",
        params![recipe_id, new_rating.rating],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

fn error_handlers() -> ErrorHandlers<actix_web::Body> {
    ErrorHandlers::new()
        .handler(StatusCode::INTERNAL_SERVER_ERROR, |res| {
            let response = HttpResponse::InternalServerError()
                .content_type(ContentType::plaintext())
                .body("Internal Server Error");
            InternalError::from_response(res, response).into()
        })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let manager = SqliteConnectionManager::file(database_url);
    let pool = Pool::new(manager).expect("Failed to create pool.");

    let conn = pool.get().expect("Couldn't get db connection from pool");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create recipes table");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).expect("Failed to create comments table");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).expect("Failed to create ratings table");

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .wrap(error_handlers())
            .wrap_fn(|req, srv| {
                let fut = srv.call(req);
                async {
                    let mut res = fut.await?;
                    res.headers_mut().insert(CONTENT_SECURITY_POLICY, "default-src 'self'".parse().unwrap());
                    res.headers_mut().insert(X_CONTENT_TYPE_OPTIONS, "nosniff".parse().unwrap());
                    res.headers_mut().insert(X_FRAME_OPTIONS, "DENY".parse().unwrap());
                    Ok(res)
                }
            })
            .app_data(web::Data::new(pool.clone()))
            .route("/recipes", web::get().to(get_recipes))
            .route("/recipes/upload", web::post().to(upload_recipe))
            .route("/recipes/{recipeId}", web::get().to(get_recipe))
            .route("/recipes/{recipeId}/comments", web::post().to(add_comment))
            .route("/recipes/{recipeId}/ratings", web::post().to(add_rating))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}