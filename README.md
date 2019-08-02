###WEBSOCKET BASED REAL TIME FILE STREAMING


####How to use:
1. Clone this repo.
2. Run `cd logstream` to switch to directory.
3. Build the docker image using `docker build -t logstream .`.
4. Run `bash deploy.sh` to run the container.
5. Visit `http://localhost:8888/tail?f=<the_filename>&l=<num_of_lines>`.

####Configuration:
Before running the docker container, application settings can be changed by changing the environment variable value passed. Below are the details of these variables:
1. `LOGDIR` : directory of logfile
2. `LOGBUFFER` : application will wait these many seconds let the new accumulate before sending it forward
3. `PINGINTERVAL` : websocket ping interval in second
4. `PINGTIMEOUT` : websocket timeout duration in second
5. `PORT` : webserver port


####Flow:
1. User agent(javascript enabled) sends HTTP GET request on `/tail`
2. User agent is served with a blank html along with a javascript code 
3. Javascript code running at client side sends websocket open request at `/ws`
4. Application opens a websocket
5. Javascript code sends `start_sending` message
6. Application attaches a asynchronous file reading script, which uses event loop once after every buffer period(`LOGBUFFER`) releases the event loop while buffering
7. Ping-Pong healthcheck mechanism takes care of closing stale connections asynchronously
