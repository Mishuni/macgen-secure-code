Rails.application.routes.draw do
  resources :recipes, only: [:index, :show, :create] do
    resources :comments, only: [:create], module: :recipes
    resources :ratings, only: [:create], module: :recipes
  end
end