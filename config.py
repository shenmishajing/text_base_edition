import os


class Config:
    max_thread = 5

    FFMPEG = '/home/wenhao/.linuxbrew/bin/ffmpeg'

    trigger_word = 'absolutely'

    # base_path = os.path.expanduser('~/datasets/voice_trigger/')
    base_path = 'data/'
    log_path = base_path + 'log/log'
    record_path = base_path + 'log/record'
    path_list = ['source_path', 'wav_path', 'transcription_path', 'transcription_json_path',
                 'transcription_and_phone_path', 'transcription_and_phoneme_path',
                 'phoneme_path']
    # path_list = ['source_path', 'wav_path', 'transcription_path', 'transcription_and_phone_path', 'img_path',
    #              'video_path']


Config.param = {item: Config.base_path + item[:item.rfind('_')] + '/' for item in Config.path_list}
