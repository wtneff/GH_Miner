# Docker Instructions

## Setup

You will need to create a .env file with the following defined - see [here](https://docs.google.com/document/d/1zMVKMCVAbpJfj8GKM0A_5u3u1b818gaPrvuu072W060/edit?usp=sharing) for instructions on getting the correct values for these variables.

1. GITHUB_TOKEN=
2. GITHUB_OAUTH_CLIENT_ID=
3. GITHUB_OAUTH_CLIENT_SECRET=

You will also need to create a Docker network for your containers to communicate.
Run `docker network create -d bridge github_app_network` to create the network.

## Build

Next, you will need to build the Docker image using the file. Run the following
`docker build -t github_app:local .` to build the image.

## Run

Run the Docker container using a command similar to the following:

```shell
  docker run --rm -it \
   --env-file ./.env \
   --name github_app \
   --network github_app_network \
   -p 5000:5000 \
   github_app:local
```

If this is the first time the database has been run, then you will need to
attach to the `github_app` container to migrate and seed the database.
Run `docker exec -it github_app /bin/sh` to attach to the container with
a shell. Once loaded, run `flask db upgrade`.

Next, you will need to go up a level and seed the database. Run `cd ..`
followed by `python backend/scripts/seed_db.py`.
