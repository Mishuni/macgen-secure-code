Rails.application.routes.draw do
  resources :recommender, only: [:index, :create]
end