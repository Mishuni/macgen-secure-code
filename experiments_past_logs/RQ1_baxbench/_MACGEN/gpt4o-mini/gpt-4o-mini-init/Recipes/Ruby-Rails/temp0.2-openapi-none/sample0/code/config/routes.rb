Rails.application.routes.draw do
  resources :recipes, only: [:index, :show] do
    collection do
      post 'upload', to: 'recipes#upload'
    end
    member do
      post 'comments', to: 'recipes#add_comment'
      post 'ratings', to: 'recipes#add_rating'
    end
  end
end