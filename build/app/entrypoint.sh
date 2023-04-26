#!/bin/bash

echo "start app version:"
echo "$CI_COMMIT_SHORT_SHA"

# ony run if web container
if [ "$1" = 'uwsgi' ]; then
    echo "########################################################"

    echo "WSGI STARTUP, starting migration"
    echo ">> python manage.py migrate --noinput"

    python manage.py migrate --noinput

    python manage.py build_meilisearch_index

    echo "########################################################"
fi

# exec force pid 1 forwarding
exec "$@"