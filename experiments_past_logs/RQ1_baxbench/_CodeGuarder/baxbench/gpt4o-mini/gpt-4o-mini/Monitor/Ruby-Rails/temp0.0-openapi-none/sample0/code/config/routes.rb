Rails.application.routes.draw do
  post '/monitor/commands', to: 'process_monitor#monitor_commands'
end