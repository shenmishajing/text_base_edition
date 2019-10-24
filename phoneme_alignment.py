import json
import utils
from config import Config as cfg

from gentle.gentle.transcriber import do_transcription
from p2fa_vislab.text_to_transcript import text_to_transcript
from p2fa_vislab.align import do_alignment


def extra_phoneme(transcription_and_phoneme_path, phoneme_path):
    json_obj = json.load(open(transcription_and_phoneme_path, 'r'))
    obj = [phoneme[0] for word in json_obj['words'] if 'phonemes' in word for phoneme in word['phonemes']]
    json.dump(obj, open(phoneme_path, 'w'))


@utils.traverser
@utils.log_process
def do_phoneme_alignment(**kwargs):
    source_file, file_name, kwargs = utils.extra_path(**kwargs)
    words = do_transcription(kwargs['source_path'] + source_file, kwargs['wav_path'] + file_name + '.wav',
                             kwargs['transcription_and_phone_path'] + file_name + '.json')
    with open(kwargs['transcription_path'] + file_name + '.txt', 'w') as transcription_file:
        for item in words:
            if not item.word.startswith('<'):
                transcription_file.write(item.word + ' ')
    text_to_transcript(kwargs['transcription_path'] + file_name + '.txt',
                       kwargs['transcription_json_path'] + file_name + '.json')
    do_alignment(kwargs['wav_path'] + file_name + '.wav', kwargs['transcription_json_path'] + file_name + '.json',
                 kwargs['transcription_and_phoneme_path'] + file_name + '.json', phonemes = True)
    extra_phoneme(kwargs['transcription_and_phoneme_path'] + file_name + '.json',
                  kwargs['phoneme_path'] + file_name + '.json')


def main():
    do_phoneme_alignment(**cfg.param)


if __name__ == '__main__':
    main()
