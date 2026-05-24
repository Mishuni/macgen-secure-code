Rails.application.routes.draw do
  resources :recipes, only: [:index, :create, :show] do
    post 'comments', to: 'recipes#add_comment'
    post 'ratings', to: 'recipes#add_rating'
  end
end