###WEBSOCKET BASED REAL TIME FILE STREAMING


####How to use:
1. Clone this repo.
2. Run `cd logstream` to switch to directory.
3. Build the docker image using `docker build -t logstream .`.
4. Run `bash deploy.sh` to run the container.
5. vist `http://localhost:8888/tail?f=<the_filename>&l=<num_of_lines>`.

####Configuration:
Before running the docker container, application settings can be changed by chnaging the environment variable value passed. Below are the deatils of these variables:
1. `LOGDIR` : directory of logfile
2. `LOGBUFFER` : application will wait these many seconds let the new accumulate before sending it forward
3. `PINGINTERVAL` : websocket ping interval in second
4. `PINGTIMEOUT` : websocket timeout duration in second
5. `PORT` : webserver port