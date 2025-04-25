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
   - If you are on Windows, you need to run the following command:
     ``` bash
     docker run -it -v ${PWD}:/app -w /app docker_example python3.13 docker_example.py
     ```
   - If you are on Linux, you need to run the following command:
     ``` bash
     docker run -it -v $(pwd):/app -w /app docker_example python3.13 docker_example.py
     ```
