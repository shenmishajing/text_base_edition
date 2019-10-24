import os
import subprocess
import cv2
import math
import utils
from config import Config as cfg

from gentle.gentle.transcriber import do_transcription


@utils.traverser
@utils.log_process
def do_video_alignment(**kwargs):
    source_file, file_name, kwargs = utils.extra_path(**kwargs)
    words = do_transcription(kwargs['source_path'] + source_file, kwargs['wav_path'] + file_name + '.wav',
                             kwargs['transcription_and_phone_path'] + file_name + '.json')
    with open(kwargs['transcription_path'] + file_name + '.txt', 'w') as transcription_file:
        for item in words:
            if not item.word.startswith('<'):
                transcription_file.write(item.word + ' ')
            if not os.path.exists(kwargs['img_path'] + file_name):
                try:
                    os.makedirs(kwargs['img_path'] + file_name)
                except FileExistsError:
                    pass
            if item.word == cfg.trigger_word:
                cap = cv2.VideoCapture(kwargs['source_path'] + source_file)
                fps = cap.get(cv2.CAP_PROP_FPS)
                cap.set(cv2.CAP_PROP_POS_FRAMES, math.floor(item.start * fps))
                for i in range(math.ceil(item.end * fps) - math.floor(item.start * fps) + 1):
                    success, frame = cap.read()
                    if success:
                        cv2.imwrite(kwargs['img_path'] + file_name + '/' + str(i) + '.jpg', frame)
                command = cfg.FFMPEG + '  -loglevel quiet -y -ss ' + str(item.start) + ' -to ' + str(
                    item.end) + ' -accurate_seek -i ' + kwargs['source_path'] + source_file + ' -c copy ' + kwargs[
                              'video_path'] + file_name + '_cut.mp4'
                subprocess.call(command, shell = True)


def main():
    do_video_alignment(**cfg.param)


if __name__ == '__main__':
    main()
