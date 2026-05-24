Rails.application.routes.draw do
  resources :recipes, only: [:index, :show] do
    collection do
      post 'upload'
    end
    member do
      resources :comments, only: [:create]
      resources :ratings, only: [:create]
    end
  end
end