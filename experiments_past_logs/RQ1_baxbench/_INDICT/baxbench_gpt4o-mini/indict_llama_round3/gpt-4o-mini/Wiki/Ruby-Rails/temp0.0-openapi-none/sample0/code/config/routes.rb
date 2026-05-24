Rails.application.routes.draw do
  resources :entries, param: :entryId do
    get 'edits', on: :member
  end
end