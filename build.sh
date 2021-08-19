# CLEAN ENVIRONMENT
rm -rf dist/
# RUN BUILD
build_platforms_name=(amd64 arm64v8)
build_platforms_arch=(linux/amd64 linux/arm64/v8)
build_plat_name=(manylinux2014_x86_64 manylinux2014_aarch64)
python_versions=("3.6" "3.7" "3.8" "3.9")

for i2 in "${!build_platforms_name[@]}";
do
  pl_dname="${build_platforms_name[$i2]}"
  pl_arch="${build_platforms_arch[$i2]}"
  pl_pname="${build_plat_name[$i2]}"
  for i in "${!python_versions[@]}";
  do
    p_version="${python_versions[$i]}"
    docker buildx build --build-arg pname="$pl_pname" --build-arg dname="$pl_dname" --build-arg python_version="$p_version" --platform "$pl_arch" -t pytgcalls_p"$p_version":"$pl_dname" . -f platforms/linux/Dockerfile
    docker run --platform "$pl_arch" -v "$PWD":/usr/src/mnt pytgcalls_p"$p_version":"$pl_dname" ./linux_mount.sh
  done
done
