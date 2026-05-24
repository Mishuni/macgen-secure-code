Rails.application.routes.draw do
  post "/invite_user", to: "invites#create"
  post "/create_user", to: "users#create"
end