Rails.application.routes.draw do
  post '/search', to: 'file_search#search'
end