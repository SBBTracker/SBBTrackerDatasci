import requests
import gzip
import boto3
import os
import logging
import datetime
import tarfile
from sbbtracker_datasci import MATCH_DOWNLOADS_DIR, MATCH_DATA_DIR, PATCH_INFO, TEMPLATEID_SUBDIR, DATAFILE_VERSION

logger = logging.getLogger(__name__)

EARLIEST_DATE = datetime.datetime(year=2022, month=1, day=25)


def _list_desired_files(existing_files, data_range):
    """
    Generate a set of files we want to download, based on the date and what we have downloaded.

    Arguments:
      existing_files: iterable
      - Each element should be of the format YYYY-MM-DD.tar.gz

      data_range: integer
      - How many days' data we want to download

    Returns:
      desired_files: The files we still need to download
    """
    offset = 1
    now = datetime.datetime.utcnow()
    if now.hour == 0 and now.minute < 30:
        offset += 1

    all_files = set()
    for incremental_offset in range(offset, offset+data_range):
        calculated_date = now - datetime.timedelta(days=incremental_offset)
        if calculated_date < EARLIEST_DATE:
            break

        all_files.add(calculated_date.strftime('%Y-%m-%d.tar.gz'))

    return all_files - set(existing_files)


def download_data(data_range=60):
    """
    Download recent SBBTracker data from s3 to your local disk.

    Arguments:
      data_range: integer
      - How many days' data we want to download

    """

    # Create the directory the data will be in
    try:
        os.makedirs(MATCH_DOWNLOADS_DIR)
    except FileExistsError:
        pass
    
    try:
        os.makedirs(MATCH_DATA_DIR)
    except FileExistsError:
        pass

    try:
        os.makedirs(TEMPLATEID_SUBDIR)
    except FileExistsError:
        pass

    # Find out which files need to be downloaded
    downloaded_rollups = os.listdir(MATCH_DOWNLOADS_DIR)
    desired_files = _list_desired_files(downloaded_rollups, data_range)

    # Download the new files
    client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='')
    client._request_signer.sign = (lambda *args, **kwargs: None)
    for f in desired_files:
        logger.info(f'Downloading file {f} from s3')
        try:
            data = client.get_object(Bucket='h8baw3zjca2jdtyhzv4t724tmzurimtp', Key=f'match-history/rollups/{DATAFILE_VERSION}/{f}'))['Body'].read()
        except client.exceptions.NoSuchKey:
            logger.error(f'File {f} could not be found in s3')
            continue
        except:
            logger.exception(f'File {f} could not be downloaded')
            continue

        output_filename = os.path.join(MATCH_DOWNLOADS_DIR, f)
        try:
            with open(output_filename, 'wb') as ofs:
                ofs.write(data)
        except:
            logger.exception(f'File {f} could not be written to {output_filename}')

    # Unzip only the files that need to be unzipped
    downloaded_rollups = os.listdir(MATCH_DOWNLOADS_DIR)
    output_dirnames = {dr.split('.')[0] for dr in downloaded_rollups}
    existing_output_dirs = [os.path.join(MATCH_DATA_DIR, i) for i in os.listdir(MATCH_DATA_DIR)]
    output_dirs_with_data = { os.path.split(i)[-1] for i in existing_output_dirs if os.listdir(i) }

    tarballs_to_unzip = [i + '.tar.gz' for i in output_dirnames - output_dirs_with_data]

    for tb in tarballs_to_unzip:
        logger.info(f'Unzipping tarball {tb}')
        input_file = os.path.join(MATCH_DOWNLOADS_DIR, tb)
        tf = tarfile.TarFile(fileobj=gzip.open(input_file), mode='r')

        output_dirname = os.path.join(MATCH_DATA_DIR, tb.split('.')[0])
        try:
            os.mkdir(output_dirname)
        except FileExistsError:
            pass

        tf.extractall(path=output_dirname)

    # Download the template-id files we need
    downloaded_templateids = {i for i in os.listdir(TEMPLATEID_SUBDIR) if os.stat(os.path.join(TEMPLATEID_SUBDIR, i)).st_size}
    desired_templateids = {pi.templateid_tag: pi.produce_filename() for pi in PATCH_INFO if pi.produce_filename() not in downloaded_templateids}

    for templateid_tag in desired_templateids:
        logger.info(f'Downloading templateid file {desired_templateids[templateid_tag]}')
        response = requests.get(f'https://raw.githubusercontent.com/SBBTracker/SBBTracker/{templateid_tag}/assets/template-ids.json')
        with open(os.path.join(TEMPLATEID_SUBDIR, desired_templateids[templateid_tag]), 'w') as ofs:
            ofs.write(response.text)


if __name__ == '__main__':
    download_data()
    
