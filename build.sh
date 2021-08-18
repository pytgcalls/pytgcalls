# CLEAN ENVIRONMENT
rm -rf dist/
rm -rf py_tgcalls.egg-info/

# RUN BUILD
rm -rf build/
python3.8 setup.py sdist bdist_wheel --plat-name manylinux2014_x86_64
rm -rf build/
python3.8 setup.py sdist bdist_wheel --plat-name manylinux2014_aarch64
