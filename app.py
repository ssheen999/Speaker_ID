import torchaudio
import time
import warnings
import ffmpeg
import os
from flask import Flask, request, render_template
from pydub import AudioSegment
from flasgger import Swagger
from speechbrain.pretrained import EncoderClassifier, SpeakerRecognition
from src.utils import get_random_flac,get_speaker_name

warnings.filterwarnings("ignore")

app = Flask(__name__)

@app.route("/speaker_test", methods=["POST"])
def speaker_test():
    try:
        start_time = time.time()
        
        audio_file = request.files['audio']
        audio_name = audio_file.filename
        print(audio_name)


        
        # Convert to FLAC format
        if not audio_name.endswith('.flac'):
            audio = AudioSegment.from_file(audio_file)
            audio.export('uploads/audio.flac', format='flac')
        else:
            file_path = os.path.join("uploads", audio_name)
            audio_file.save(file_path)

            new_file_name = 'audio.flac'
            new_file_path = os.path.join('uploads', new_file_name)

            #new_file_path = os.path.join("uploads", "audio.flac")
            #new_file_path = os.path.join("uploads", audio_name)
            os.rename(file_path, new_file_path)
            

        # Load speaker classifier
        speaker_classifier = EncoderClassifier.from_hparams(source="best_model/",
                                                            hparams_file='hparams_inference.yaml', 
                                                            savedir="best_model/")

        # Classify speaker
        signal, fs = torchaudio.load('uploads/audio.flac')
        output_probs, score, index, text_lab = speaker_classifier.classify_batch(signal)
        print()

        # Load verification model
        verification = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb")

        # Verify speaker
        verify_audio_file = get_random_flac(f"data/Openslr/{text_lab[0]}")
        print(verify_audio_file)
        score, prediction = verification.verify_files(verify_audio_file, "uploads/audio.flac")
        

        end_time = time.time()
        respond_time = round(end_time - start_time, 2)

        speaker_name = get_speaker_name(text_lab[0])
        speaker_pred = prediction[0].item()

        result_json = {
            "most_similar_speaker": speaker_name,
            "prediction": speaker_pred,
            "respond_time": f"{respond_time} seconds"
        }

        return render_template('template.html', result=result_json)

    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET"])
def index():
    return render_template('template.html')

if __name__ == '__main__':
    #if not os.path.exists('audios'):
    #    os.makedirs('audios')
        
    app.run(host='0.0.0.0', port=8080, threaded=True)

