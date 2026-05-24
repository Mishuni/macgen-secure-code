Rails.application.routes.draw do
  post '/compile', to: 'compilation#compile'
end