import logging
from datetime import datetime

import soundfile
from flask import Flask, request
from flask import send_file
from flask_cors import CORS

from sovits import infer_tool

app = Flask(__name__)

CORS(app)

logging.getLogger('numba').setLevel(logging.WARNING)


def get_timestamp():
    timestamp = datetime.now()
    return timestamp.strftime("%Y%m%d_%H%M%S")


@app.route("/voiceChangeModel", methods=["POST"])
def voice_change_model():
    request_form = request.form
    wave_file = request.files.get("sample", None)
    # 变调信息
    f_pitch_change = int(float(request_form.get("fPitchChange", 0)))
    raw_sample = int(float(request_form.get("sampleRate", 0)))
    raw_wav_path = f"{http_temp_path}/http_in.wav"
    print(raw_sample, f_pitch_change)
    # http获得wav文件并转换
    w_file = wave_file.read()
    with open(raw_wav_path, 'wb') as fop:
        fop.write(w_file)
    infer_tool.format_wav(raw_wav_path, target_sample)
    out_audio, out_sr = infer_tool.infer(raw_wav_path, speaker_id, f_pitch_change, net_g_ms, hubert_soft,
                                         feature_input)
    out_wav_path = f"{http_temp_path}/http_out.wav"
    soundfile.write(out_wav_path, out_audio, target_sample)
    infer_tool.format_wav(out_wav_path, raw_sample)
    return send_file(out_wav_path, as_attachment=True)


if __name__ == '__main__':
    # 这个是人物音色id，发布模型的时候、发布人应注明
    speaker_id = 4
    # 每个模型和config是唯一对应的
    model_name = "152_epochs.pth"
    config_name = "nyarumul.json"
    # 建立缓存文件夹，并清理上次运行产生的音频文件
    http_temp_path = "./wav_temp"
    infer_tool.mkdir([http_temp_path])
    # 加载模型
    net_g_ms, hubert_soft, feature_input, hps_ms = infer_tool.load_model(f"pth/{model_name}", f"configs/{config_name}")
    target_sample = hps_ms.data.sampling_rate
    # 此处与vst插件对应，不建议更改
    app.run(port=6842, host="0.0.0.0", debug=False, threaded=False)
