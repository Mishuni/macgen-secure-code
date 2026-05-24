Rails.application.routes.draw do
  resources :recipes, only: [:index, :create, :show] do
    resources :comments, only: [:create]
    resources :ratings, only: [:create]
  end
end