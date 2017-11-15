Run the script with the command for the artificial dataset:

    python -m scripts.runnerB


Run the script with the command for the real dataset:

    python -m scripts.runnerC


To run tensorboard server:

    tensorboard --logdir=${PWD}/out/deep/RUN_NAME/logs


To generate a video from the crops outpus:

    ffmpeg -framerate 4 -i %0d.png -pix_fmt yuv420p output.mp4


To count files:

    cloc  $(git ls-files | grep -v data/)


To package and run the factor models:

    cd java/ocr
    mvn scala:run -DmainClass=io.owna.ocr.App


To train and run the labeller:

    python -m table.training.generator
    python -m table.training.train


Server How to
-------------

To install the first time:

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    python manage.py migrate auth
    python manage.py migrate --run-syncdb
    python manage.py nltk_download

To create the admin user:

    python manage.py create_admin_token $OCR_SERVER_PASSWORD

To create migrations:

    python manage.py makemigrations api
    python manage.py migrate


To run the server:

    python manage.py runserver 192.168.1.101:8000


To run the celery worker:

    celery -A ocrapi worker -l info


To process an image from the pending uploaded images:

    python manage.py process_image 1

To extract a structure from the pending uploaded structures:

    python manage.py extract_structure 1


Tests How to
------------

To run the tests:

    python -m tests.image_regression
    python -m tests.structure_regression


Deployment How to
-----------------

To start supervisor:

    supervisord -c supervisor.conf
    supervisorctl -c supervisor.conf status

To collect the static files:

    python manage.py collectstatic
