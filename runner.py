import atexit
import os
import subprocess
import time
import uuid
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, send_file

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def clean_up():
    print(time.strftime('%A, %d %B %Y %I:%M:%S %p'), 'clean up')
    t_now = time.time()
    for file_name in os.listdir('out'):
        file_path = os.path.join('out', file_name)
        if not os.path.isfile(file_path):
            continue
        if os.stat(file_path).st_mtime < t_now - 3600:
            os.remove(file_path)
            print(file_path, '\tremoved')


scheduler = BackgroundScheduler()
scheduler.add_job(func=clean_up, trigger='interval', seconds=60 * 30)
scheduler.start()

app = Flask(__name__, static_url_path='/static', static_folder='page/static')
lock_obj = Lock()


def mlpla_runner(root_name):
    mlpla_run = subprocess.run([
        'java',
        '-jar',
        'MLPLA/MLPLA.jar',
        '--process',
        'MLPLA/etc/languagepipe.conf',
        'MLPLA/models/ro',
        'out/{}.txt'.format(root_name),
    ], capture_output=True)
    return mlpla_run


def ssla_runner(root_name, model_name, use_gv):
    ssla_run = subprocess.run([
        'java',
        '-jar',
        'SSLA/SSLA.jar',
        '--synthesize',
        'SSLA/models/ro/{}'.format(model_name),
        'out/{}.lab'.format(root_name),
        'out/{}.wav'.format(root_name),
        use_gv
    ], capture_output=True)
    return ssla_run


def speak_it(input_text, model_name='anca', use_gv='false'):
    root_name = uuid.uuid4().hex

    with open('out/{}.txt'.format(root_name), 'w') as input_for_mlpla:
        input_for_mlpla.write(input_text)

    with lock_obj:
        mlpla_run = mlpla_runner(root_name)

    if mlpla_run.returncode != 0:
        return

    with open('out/{}.lab'.format(root_name), 'wb') as outf_mlpla, \
            open('out/{}_log.txt'.format(root_name), 'wb') as errf_mlpla:
        outf_mlpla.write(mlpla_run.stdout)
        errf_mlpla.write(mlpla_run.stderr)

    ssla_run = ssla_runner(root_name, model_name, use_gv)

    if ssla_run.returncode != 0:
        return

    return 'out/{}.wav'.format(root_name)


@app.route('/speak', methods=['POST', 'GET'])
def speak_route():
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        model_name = request.form.get('model_name')
        use_gv = request.form.get('use_gv')
    else:
        input_text = request.args.get('input_text')
        model_name = request.args.get('model_name')
        use_gv = request.args.get('use_gv')
    if input_text:
        if not model_name:
            model_name = 'anca'
        if not use_gv:
            use_gv = 'false'
        file_resp_path = speak_it(input_text, model_name, use_gv)
        if file_resp_path:
            return send_file(file_resp_path, as_attachment=True, attachment_filename='speak.wav')
    return 'error'


@app.route('/favicon.ico')
def favicon_route():
    return send_file('page/static/favicon.ico')


@app.route('/')
def root_route():
    return send_file('page/index.html')


atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
