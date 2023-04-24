# Use regular UBI base image
FROM registry.access.redhat.com/ubi8/ubi:latest

# Arguments passed to the build
ARG IMAGE_CREATE_DATE
ARG IMAGE_VERSION
ARG IMAGE_VERSION_COMMIT

# Environment variables

ENV USER_ID=1001 \
    TRADEZERO_HOME=/opt/tradezero_pricer \
    APP=tradezero_pricer.py \
    FLASK_APP=${TRADEZERO_HOME}/${APP} \
    TZP_VERSION=$IMAGE_VERSION \
    TZP_COMMIT=$IMAGE_VERSION_COMMIT

ENV SUMMARY="TradeZero Pricer is a backend microservice for the Tradezero application."

# Labels
LABEL maintainer="mauro.oddi@gmail.com" name="tradezero_pricer" build-date=$IMAGE_CREATE_DATE version=$IMAGE_VERSION
LABEL summary="$SUMMARY" \
	  io.k8s.description="$SUMMARY" io.k8s.display-name="tradezero-pricer" \
	  usage="podman run -d --name tradezero-pricer-1 -e TZP_DB_HOST=192.168.0.1 -e TZP_DB_USERNAME=tradezero -e TZP_DB_PASSWORD=verysecret -p 8080:8080 tradezero-pricer:latest" \
      commit="$IMAGE_VERSION_COMMIT"

# OCI Image Spec Labels [ https://github.com/opencontainers/image-spec/blob/master/annotations.md ]
LABEL org.opencontainers.image.title="Trade Zero - Pricer" \
      org.opencontainers.image.description="TradeZero Pricer Backend Microservice." \
      org.opencontainers.image.authors="Mauro S. Oddi" \
      org.opencontainers.image.created=$IMAGE_CREATE_DATE \
      org.opencontainers.image.version=$IMAGE_VERSION \
      org.opencontainers.image.url="https://github.com/mauroseb/tradezero-pricer/Containerfile" \
      org.opencontainers.image.soruce="https://github.com/mauroseb/tradezero-pricer.git" \
      org.opencontainers.image.vendor="Up and Running with Red Hat Openshift" \
      org.opencontainers.image.licenses="MIT"

USER 0

# Install python 3.9 and pip 3.9
RUN dnf install --setopt=tsflags=nodocs -y -e 0 python39 python39-pip && \
    dnf clean all

# Create application homedir
RUN mkdir $TRADEZERO_HOME

WORKDIR $TRADEZERO_HOME

# Copy application bits
ADD . .

# Install application requirements
RUN pip3 --no-cache-dir install --upgrade pip && \
    pip3 --no-cache-dir install -r requirements.txt

RUN useradd -d $TRADEZERO_HOME -M -r -s /sbin/nologin -c "TrazeZero Pricer" -u ${USER_ID} tzpricer && \
    chown -R ${USER_ID}:0 $TRADEZERO_HOME

USER 1001

EXPOSE 8080

# Run app
CMD [ "sh", "-c", "./boot.sh" ]

