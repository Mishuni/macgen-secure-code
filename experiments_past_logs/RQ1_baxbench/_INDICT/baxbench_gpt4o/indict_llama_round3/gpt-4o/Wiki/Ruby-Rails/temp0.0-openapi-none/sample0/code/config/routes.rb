Rails.application.routes.draw do
  resources :entries, only: [:index, :create, :show, :update] do
    get 'edits', on: :member, to: 'entries#history'
  end
end