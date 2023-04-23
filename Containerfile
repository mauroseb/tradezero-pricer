FROM registry.access.redhat.com/ubi8/python-39:latest

ARG IMAGE_CREATE_DATE
ARG IMAGE_VERSION
ARG IMAGE_VERSION_COMMIT

ENV USER_ID=1001 \
    TRADEZERO_HOME=/opt/tradezero_pricer \
    FLASK_APP=${TRADEZERO_HOME}/tradezero_pricer.py \
    TZP_VERSION=$IMAGE_VERSION \
    TZP_COMMIT=$IMAGE_VERSION_COMMIT

LABEL maintainer="mauro.oddi@gmail.com" name="tradezero_pricer" build-date=$IMAGE_CREATE_DATE version=$IMAGE_VERSION
LABEL commit=$IMAGE_VERSION_COMMIT

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

RUN mkdir $TRADEZERO_HOME && \
    chown $USER_ID:0 $TRADEZERO_HOME

WORKDIR $TRADEZERO_HOME

USER $USER_ID
#RUN yum install --setopt=tsflags=nodocs -y -e 0 python3 python3-pip && \
#    yum clean all

ADD . .

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 8080

CMD [ "flask", "run", "--host=0.0.0.0", "--port=8080" ]
