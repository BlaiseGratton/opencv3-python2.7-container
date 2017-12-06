import os

from flask import Flask, request, Response, send_file

from video import init_logging, main


app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5300))
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


@app.route('/api/stream/')
def start_camera():
    camera_url = request.args.get('streamUrl')
    return Response(main(camera_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/cameras/')
def get_all_cameras():
    # headers = {'apiKey': os.environ.get('SMARTWAY_KEY')}
    # camera_url = 'https://dev.tdot.tn.gov/opendata/api/public/roadwaycameras'
    # req = requests.get(cameras_url, headers=headers)
    # return jsonify({'data': req.json()})
    return send_file('static/smartway_data.json')


@app.route('/')
def serve_index():
    return send_file('static/index.html')


if __name__ == '__main__':
    init_logging()
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True,
        threaded=True,
        use_reloader=False
    )
