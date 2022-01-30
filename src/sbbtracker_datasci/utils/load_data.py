import json
from dataclasses import dataclass
import gzip
import boto3
import os
import logging
import datetime
import tarfile
from sbbtracker_datasci import MATCH_DATA_DIR
from sbbbattlesim.board import Board

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    filename: str
    token: str
    datestr: str


class GlobalData:
    pass


GLOBAL_DATA = GlobalData()


def walk_data_dir():
    """
    Go through the downloaded data and return relevant data, split into its useful components
    """

    for root_dir, _, files in os.walk(MATCH_DATA_DIR):
        for f in files:
            full_path = os.path.join(root_dir, f)

            path, filename = os.path.split(full_path)
            path, token = os.path.split(path)
            path, datestr = os.path.split(path)

            yield FileInfo(filename=full_path, token=token, datestr=datestr)
            

def load_data():
    # TODO: Add the ability to filter on patches & such


    for fi in walk_data_dir():
        data = json.load(open(fi.filename))





