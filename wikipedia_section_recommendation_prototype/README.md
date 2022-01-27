# Requirements
- docker compose
- port 80 available (or change it in `./server/docker-compose.yml` on line 15)

# Installation and launching the web app
- Before being able to use the prototype, you must download the mongodb dump from here: https://drive.switch.ch/index.php/s/ioirxaIFarFCTwC and then extract the `dump` folder from the zip archive in the `./mongodb` folder (i.e. `./mongodb/dump`)
- change directory to `./server`
- run `build_and_launch_containers.sh`
- wait for the mongodb import to finish in the console before using the web app
- the web app is running on port 80, visit http://127.0.0.1 to access it