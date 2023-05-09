# Copyright 2023. Mauro Oddi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Build the guestbook-go example

# Usage:
#   [VERSION=0.1.4] [REGISTRY="quay.io"] make build
VERSION?=0.1.5
REGISTRY?=quay.io
REG_NAMESPACE := uar_openshift
PODMAN_ARGS := "--layers=false"

.PHONY: all
all: clean build push clean

.PHONY: build
build: ## Build container
	podman build ${PODMAN_ARGS} --build-arg=IMAGE_VERSION=${VERSION} \
             --build-arg=IMAGE_CREATE_DATE=$$(date +%F) \
             --build-arg=IMAGE_VERSION_COMMIT=$$(git rev-parse --short HEAD) \
 			 -t ${REGISTRY}/${REG_NAMESPACE}/tradezero-pricer:${VERSION} .

.PHONY: push
push: ## Push container to defined registry
	podman push ${REGISTRY}/${REG_NAMESPACE}/tradezero-pricer:${VERSION}

.PHONY: clean
clean: ## Clean container images locally
	podman rm -f ${REGISTRY}/${REG_NAMESPACE}/tradezero-pricer:${VERSION} 2> /dev/null || true

