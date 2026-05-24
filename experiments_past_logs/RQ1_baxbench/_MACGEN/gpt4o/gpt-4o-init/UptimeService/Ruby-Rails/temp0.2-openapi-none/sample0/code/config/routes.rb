Rails.application.routes.draw do
  post '/heartbeat', to: 'services#heartbeat'
  post '/services', to: 'services#index'
end