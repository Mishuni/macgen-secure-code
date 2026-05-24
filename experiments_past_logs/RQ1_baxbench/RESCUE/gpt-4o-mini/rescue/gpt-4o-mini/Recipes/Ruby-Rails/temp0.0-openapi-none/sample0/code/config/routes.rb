Rails.application.routes.draw do
  resources :recipes do
    resources :comments, only: [:create]
    resources :ratings, only: [:create]
  end

  get 'recipes', to: 'recipes#index'
  post 'recipes/upload', to: 'recipes#create'
  get 'recipes/:id', to: 'recipes#show'
end