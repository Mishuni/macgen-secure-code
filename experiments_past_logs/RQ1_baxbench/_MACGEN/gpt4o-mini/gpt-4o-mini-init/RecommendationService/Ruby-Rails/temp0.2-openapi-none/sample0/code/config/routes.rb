Rails.application.routes.draw do
  resources :products, only: [] do
    collection do
      get 'recommender', to: 'products#recommender'
      post 'recommender', to: 'products#create'
    end
  end
end