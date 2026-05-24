Rails.application.routes.draw do
  resources :recommender, only: [:get, :post]
end