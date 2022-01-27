#! /bin/bash

docker build -t wikipedia_section_recommendation .
chmod +x ../mongodb/import.sh
docker-compose up