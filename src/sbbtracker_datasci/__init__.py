import datetime
from dataclasses import dataclass
import os
import logging.config

DATAFILE_VERSION = 'v2'

fileconf = os.getenv('LOGGING_CONF')
if fileconf:
    logging.config.fileConfig(fileconf)


@dataclass
class PatchInfo:
    patch: str
    date: datetime.datetime
    templateid_tag: str

    def produce_filename(self):
        return f'template-id-{self.templateid_tag}.json'


def generate_directory_names():
    windows_env_var = 'APPDATA'
    linux_env_var = 'HOME'
    dirname = 'SBBTrackerDatasci'

    if windows_env_var in os.environ:
        data_dir = os.path.join(os.environ[windows_env_var], dirname)
    elif linux_env_var in os.environ:
        data_dir = os.path.join(os.environ[linux_env_var], dirname)
    else:
        data_dir = os.getcwd()

    download_subdir = os.path.join(data_dir, 'downloads', 'SBBTrackerMatchData', DATAFILE_VERSION)
    data_subdir = os.path.join(data_dir, 'data', 'SBBTrackerMatchData', DATAFILE_VERSION)
    templateid_subdir = os.path.join(data_dir, 'data', 'SBBTrackerTemplateIds')

    return download_subdir, data_subdir, templateid_subdir


MATCH_DOWNLOADS_DIR, MATCH_DATA_DIR, TEMPLATEID_SUBDIR = generate_directory_names()

PATCH_INFO = [
    PatchInfo(
        patch='67.4',
        date=datetime.datetime(year=2022, month=1, day=25),
        templateid_tag='v4.0.4'
    )
]

