# Docker Example

## What is it?
This is just a docker image (Pre-Built image), if you don't want to install
everything on your local machine.

## How to run this docker image?
Just follow these steps

1. Build the **Docker Image**
``` bash
docker build . -t docker_example
```
2. Run the **Docker Image**
``` bash
docker run -v "$PWD":/usr/src/mnt pytgcalls_machine ./linux_mount.sh
```

## What is it the supported OS?
This Docker Image can run only on Linux images
