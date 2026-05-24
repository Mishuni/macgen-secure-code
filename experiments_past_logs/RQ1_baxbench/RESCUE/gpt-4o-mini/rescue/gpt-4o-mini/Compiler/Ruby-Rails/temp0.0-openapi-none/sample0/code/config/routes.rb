Rails.application.routes.draw do
  post '/compile', to: 'compilations#compile'
end