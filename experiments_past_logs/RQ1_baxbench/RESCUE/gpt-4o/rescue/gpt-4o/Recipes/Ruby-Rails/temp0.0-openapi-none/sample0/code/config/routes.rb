Rails.application.routes.draw do
  resources :recipes, only: [:index, :show] do
    post :comments, to: 'recipes#add_comment', on: :member
    post :ratings, to: 'recipes#add_rating', on: :member
  end

  post '/recipes/upload', to: 'recipes#create'
end