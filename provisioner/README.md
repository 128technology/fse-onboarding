# Building a new container


If you don't have the repo cloned,

`git clone ssh://git@bitbucket.128technology.com:7000/t128/fse-onboarding.git`

Else,

## Full workflow

```
cd fse-onboarding
git checkout master
git pull

export PROVISIONER_CONTAINER_VERSION=v0.0.1
docker build --no-cache -t fse-provisioner:v0.0.1 fse-prov/
docker-compose up -d

docker ps

docker image ls
```

### Saving image

`docker save fse-provisioner:v0.0.1 | gzip > ~/Sandbox/fse-provisioner:v0.0.1.tar.gz`

# Bringing up a new container

```
gunzip /tmp/fse-provisioner:v0.0.1.tar.gz
docker load -i /tmp/fse-provisioner\:v0.0.1.tar
docker tag fse_prov:v0.0.1 fse-provisioner:v0.0.1
docker image ls

export PROVISIONER_CONTAINER_VERSION=v0.0.1
docker-compose up -d
```

# User guide

## Logging into the container

`docker exec -it root_PROV_1 bash`

## Config templates

Resides in the directory `/usr/share/128T-provisioner/config_templates/`

## Local DB

Running as a screen session

If there's a screen session already running,
`screen -r`

Else, start a new screen session and the local server

```
screen
cd /var/www/fse-db/
./server
```

Once the server is up and running switch to the main screen without killing it `Ctrl+A+D`
