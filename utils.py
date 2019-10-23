import os
import logging
import time
from config import Config as cfg
from concurrent.futures import ThreadPoolExecutor, as_completed
from gentle.gentle.transcriber import do_transcription


class Log:
    # 第一步，创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Log等级总开关

    # 第二步，创建一个handler，用于写入日志文件
    last_slash = cfg.log_path.rfind('/')
    if not os.path.exists(cfg.log_path[:last_slash]):
        os.makedirs(cfg.log_path[:last_slash])
    fh = logging.FileHandler(cfg.log_path)
    fh.setLevel(logging.INFO)  # 输出到file的log等级的开关

    # 第三步，再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

    # 第四步，定义handler的输出格式
    fh_formatter = logging.Formatter("%(message)s")
    fh.setFormatter(fh_formatter)
    ch_formatter = logging.Formatter("%(asctime)s : %(message)s")
    ch.setFormatter(ch_formatter)

    # 第五步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)


def traverser(file_process_func):
    if cfg.max_thread > 1:
        executor = ThreadPoolExecutor(max_workers = cfg.max_thread)
        all_tasks = []

    def traversing_file_process_func(**kwargs):
        ignore_list = ['.DS_Store']
        if os.path.isdir(kwargs['source_path']):
            for source_file in sorted(os.listdir(kwargs['source_path'])):
                if os.path.isdir(kwargs['source_path'] + source_file):
                    param = {k: v + source_file + '/' for k, v in kwargs.items()}
                    traversing_file_process_func(**param)
                elif source_file not in ignore_list:
                    param = {k: v + source_file for k, v in kwargs.items()}
                    if cfg.max_thread > 1:
                        all_tasks.append(executor.submit(file_process_func, Log.logger, **param))
                    else:
                        file_process_func(Log.logger, **param)
        else:
            if cfg.max_thread > 1:
                all_tasks.append(executor.submit(file_process_func, Log.logger, **kwargs))
            else:
                file_process_func(Log.logger, **kwargs)
        if cfg.max_thread > 1:
            as_completed(all_tasks)

    return traversing_file_process_func


def extra_path(**kwargs):
    while not os.path.isfile(kwargs['source_path']):
        kwargs['source_path'] = kwargs['source_path'][:kwargs['source_path'].rfind('/')]
        if kwargs['source_path'] == '':
            raise ValueError('source_path is not a file')
    source_file = kwargs['source_path'][kwargs['source_path'].rfind('/') + 1:]
    file_name = source_file[:source_file.rfind('.')]
    for k in kwargs:
        if os.path.exists(kwargs[k]) and os.path.isfile(kwargs[k]):
            while not os.path.isdir(kwargs[k]):
                kwargs[k] = kwargs[k][:kwargs[k].rfind('/')]
            kwargs[k] += '/'
        elif not os.path.exists(kwargs[k]):
            if kwargs[k].endswith('/'):
                try:
                    os.makedirs(kwargs[k])
                except FileExistsError:
                    pass
            else:
                kwargs[k] = kwargs[k][:kwargs[k].rfind('/') + 1]
                if not os.path.exists(kwargs[k]):
                    try:
                        os.makedirs(kwargs[k])
                    except FileExistsError:
                        pass
    return source_file, file_name, kwargs


def prepare_and_do_transcription(logger, **kwargs):
    start = time.time()
    logger.debug('start process ' + kwargs['source_path'])
    source_file, file_name, kwargs = extra_path(**kwargs)
    words = do_transcription(kwargs['source_path'] + source_file, kwargs['wav_path'] + file_name + '.wav',
                             kwargs['transcription_and_phone_path'] + file_name + '.json')
    return start, source_file, file_name, kwargs, words
