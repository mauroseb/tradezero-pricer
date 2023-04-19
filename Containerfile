FROM registry.access.redhat.com/ubi8/python-39:latest

ENV User_ID=1001 \
    TRADEZERO_HOME=/opt/tradezero_pricer \
    FLASK_APP=${TRADEZERO_HOME}/tradezero_pricer/tradezero_pricer.py \
    FLASK_ENV=production

LABEL maintainer="mauro.oddi@gmail.com" name="tradezero_pricer" build-date="13-04-2023" version="0.1.0"

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
