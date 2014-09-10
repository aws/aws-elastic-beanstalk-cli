require 'sinatra/base'

class WorkerSample < Sinatra::Base
    set :logging, true

    post '/' do
        msg_id = request.env["HTTP_X_AWS_SQSD_MSGID"]
        data = request.body.read
        File.open("/tmp/sample-app.log", 'a') do |file|
            file.puts "#{data}"
        end
    end
end
