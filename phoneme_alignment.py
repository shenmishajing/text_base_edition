import os
import time
import json
import utils
from config import Config as cfg

from p2fa_vislab.text_to_transcript import text_to_transcript
from p2fa_vislab.align import do_alignment


def extra_phoneme(transcription_and_phoneme_path, phoneme_path):
    json_obj = json.load(open(transcription_and_phoneme_path, 'r'))
    obj = [phoneme[0] for word in json_obj['words'] if 'phonemes' in word for phoneme in word['phonemes']]
    json.dump(obj, open(phoneme_path, 'w'))


@utils.traverser
def do_phoneme_alignment(logger, **kwargs):
    start, source_file, file_name, kwargs, words = utils.prepare_and_do_transcription(logger, **kwargs)
    with open(kwargs['transcription_path'] + file_name + '.txt', 'w') as transcription_file:
        for item in words:
            transcription_file.write(item.word + ' ')
    text_to_transcript(kwargs['transcription_path'] + file_name + '.txt',
                       kwargs['transcription_json_path'] + file_name + '.json')
    do_alignment(kwargs['wav_path'] + file_name + '.wav', kwargs['transcription_json_path'] + file_name + '.json',
                 kwargs['transcription_and_phoneme_path'] + file_name + '.json', phonemes = True)
    extra_phoneme(kwargs['transcription_and_phoneme_path'] + file_name + '.json',
                  kwargs['phoneme_path'] + file_name + '.json')
    logger.debug('{} finished in {:.2f}s'.format(kwargs['source_path'] + source_file, time.time() - start))
    logger.info(kwargs['source_path'] + source_file)


def main():
    do_phoneme_alignment(**cfg.param)


if __name__ == '__main__':
    main()
