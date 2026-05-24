Rails.application.routes.draw do
  resources :clicks, only: [:create, :index]
end