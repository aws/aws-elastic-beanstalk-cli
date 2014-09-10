var port = process.env.PORT || 3000,
    http = require("http"),
    fs = require("fs"),
    html = fs.readFileSync("index.html");

var server = http.createServer(function (request, response) {
    if (request.method == 'POST') {
        request.on('data', function(chunk) {
            fs.appendFile("/tmp/sample-app.log", chunk.toString() + "\n", function (err) {});
        });
        
        request.on('end', function() {
            response.writeHead(200, "OK", {'Content-Type': 'text/html'});
            response.end();
        });
    } else {
        response.writeHead(200);
        response.write(html);
        response.end();
    }
});

// Listen on port 3000, IP defaults to 127.0.0.1
server.listen(port);

// Put a friendly message on the terminal
console.log("Server running at http://127.0.0.1:" + port + "/");
