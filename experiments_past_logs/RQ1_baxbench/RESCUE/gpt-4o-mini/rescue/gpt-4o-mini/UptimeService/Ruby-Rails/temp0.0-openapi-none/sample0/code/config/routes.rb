Rails.application.routes.draw do
  post '/heartbeat', to: 'services#register_heartbeat'
  post '/services', to: 'services#get_services'
end