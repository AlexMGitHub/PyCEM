FROM ubuntu:22.04 as base
# The Python 3.7 Docker image uses glibc v2.31; need v2.34 or higher.
# Ubuntu 22.04 image has glibc v2.35
LABEL maintainer="AlexMGitHub@gmail.com"
WORKDIR /pycem
# Copy over minimum required files to install PyCEM package
COPY setup.py  ./
COPY src/__init__.py ./src/__init__.py
COPY src/C/ ./src/C/
# Compile C shared libraries
RUN apt-get update
RUN apt-get install make gcc -y
WORKDIR /pycem/src/C/makefiles/
RUN make -f MakeFDTD_TMz.mk clean
RUN make -f MakeFDTD_TMz.mk
WORKDIR /pycem
# Need Python 3.7 for VTK compatibility, link below describes how to install proper version of pip as well
# https://stackoverflow.com/questions/54633657/how-to-install-pip-for-python-3-7-on-ubuntu-18
RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.7 -y
RUN apt-get install python3-pip -y
# Have to manually install distutils module per link below
# https://github.com/pypa/get-pip/issues/124
RUN apt-get install --reinstall python3.7-distutils -y
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
# Install cv2 dependencies needed for PyVista
# https://itsmycode.com/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directory/
RUN apt-get install ffmpeg libsm6 libxext6 -y
# Copy the requirements.txt separately so build cache only busts if requirements.txt changes
COPY docker/webapp_requirements.txt ./
# Reduce image size by not caching .whl files
RUN python3.7 -m pip install --no-cache-dir -r webapp_requirements.txt
# Add and run as non-root user for security reasons (after installation)
RUN useradd -ms /bin/bash webapp
RUN chown webapp src/
USER webapp
# Expose webapp port
EXPOSE 8050


FROM base as development
# Development webserver
LABEL build="development"
ENV SERVER_DEBUG_MODE=debug
ENTRYPOINT ["python3.7", "/pycem/src/webapp/pycem_app.py"]


FROM base as production
# Copy entire application to Docker image
COPY . ./
# Production webserver
LABEL build="production"
ENV SERVER_DEBUG_MODE=production
ENTRYPOINT ["python3.7", "/pycem/src/webapp/pycem_app.py"]