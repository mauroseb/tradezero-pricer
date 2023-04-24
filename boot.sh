#!/bin/bash

gunicorn -w 4 -b :8080 'tradezero_pricer:create_app("container")'
