#!/bin/bash
NAME=tradezero-pricer
VERSION=0.1.3
TAG=devel

podman build --build-arg=IMAGE_VERSION=${VERSION} --build-arg=IMAGE_CREATE_DATE=`date +%F` --build-arg=IMAGE_CREATE_COMMIT=`git rev-parse --short HEAD` -t ${NAME}:${TAG} .

