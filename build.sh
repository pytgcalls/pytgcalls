# CLEAN ENVIRONMENT
rm -rf dist/
# RUN BUILD

# ARM64V8 BUILD
docker buildx build -t pytgcalls:arm64 . -f platforms/arm64v8/Dockerfile
docker run --platform linux/arm64/v8 -v "$PWD":/usr/src/mnt pytgcalls:arm64 ./install_platform.sh

# AMD64 BUILD
docker buildx build -t pytgcalls:amd64 . -f platforms/amd64/Dockerfile
docker run --platform linux/amd64 -v "$PWD":/usr/src/mnt pytgcalls:amd64 ./install_platform.sh

# WINDOWS_AMD64 BUILD
# if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null ; then
#  docker buildx build --platform windows/amd64 -t pytgcalls:windows_amd64 . -f platforms/windows_amd64/Dockerfile
# @fi;
# NOT SUPPORTED TO RUN WINDOWS DOCKER ON LINUX
# ABOUT THIS https://stackoverflow.com/questions/42158596/can-windows-containers-be-hosted-on-linux