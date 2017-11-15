from fabric.api import env, run, cd, require, task

env.user = 'ubuntu'

env.shell_env = {
    'TERM': 'xterm'
}
env.shell = "/bin/bash -l -i -c"

@task
def staging():
    env.hosts = ['52.52.252.152']
    env.branch_name = 'master'

@task
def restart_apps():
    run('supervisorctl -c supervisor.conf reread'.format(env))
    run('supervisorctl -c supervisor.conf update'.format(env))
    run('supervisorctl -c supervisor.conf restart all'.format(env))

@task
def update_codebase():
    run('git fetch origin'.format(env))
    run('git checkout -q -f {0.branch_name}'.format(env))
    run('git pull origin {0.branch_name}'.format(env))

@task
def migrate():
    run('python manage.py migrate')

@task
def install_requirements():
    packages = ['default-jre']
    for package in packages:
        run('sudo apt-get -y install {}'.format(package))
    run('pip install -r requirements.txt')

@task
def init_db():
    run('python manage.py migrate auth'.format(env))
    run('python manage.py migrate --run-syncdb'.format(env))
    run('python manage.py loaddata ocrapi/fixtures/fixture.json'.format(env))


@task
def collect_statics():
    run('python manage.py collectstatic --noinput'.format(env))


def run_tests():
    run('python -m tests.image_regression')
    run('python -m tests.structure_regression')
    run('python -m tests.assignment_cost')
    run('python -m tests.parser')


@task
def deploy():
    require('hosts', provided_by=[staging,])
    update_codebase()
    install_requirements()
    run_tests()
    migrate()
    restart_apps()
    collect_statics()


@task
def status():
    run('supervisorctl -c supervisor.conf status'.format(env))

@task
def htop():
    run('htop'.format(env))

@task
def connect_db():
    run('python manage.py dbshell'.format(env))

@task
def log_tail_server():
    run('tail -f var/log/supervisor/ocr_server.log'.format(env))

@task
def log_tail_celery():
    run('tail -f var/log/supervisor/celery_worker.log'.format(env))

@task
def clean_pyc():
    run('find . -name "*.pyc" -delete'.format(env))

@task
def nltk_download():
    run('python manage.py nltk_download'.format(env))

@task
def process_image(image_id):
    run('python manage.py process_image {0}'.format(image_id))
