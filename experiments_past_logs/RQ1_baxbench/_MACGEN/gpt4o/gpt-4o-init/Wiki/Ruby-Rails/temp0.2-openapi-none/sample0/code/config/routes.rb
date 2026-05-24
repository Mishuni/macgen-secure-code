Rails.application.routes.draw do
  resources :entries, only: [:index, :create, :show, :update] do
    member do
      get 'edits', to: 'entries#edit_history'
    end
  end
end