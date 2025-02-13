import re
import logging
import argparse
import multiprocessing
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from astropy.io import fits

from itipy.download.util import download_url, round_hour, get_bs

class SOHOEITDownloader:
    """
    Class to download SOTO/EIT data from SDAC

    Products:
        EUVI 171 Å, 195 Å, 284 Å, 304 Å
        https://umbra.nascom.nasa.gov/eit/

    Args:
        ds_path (str): Path to the directory where the downloaded data should be stored.
        n_workers (int): Number of worker threads for parallel download.
        wavelengths (list): List of wavelengths to download.
        quality_check (bool): Perform quality check on the downloaded files.
        level (str): L0 for level 0 data, L1 for level 1 data
    """
    def __init__(self, ds_path, n_workers=4,
                wavelengths=[171, 195, 284, 304],
                quality_check=True,
                level='L1'):
        assert level in ['L0', 'L1'], 'level must be either L0 or L1'
        self.level = level
        self.ds_path = ds_path
        self.n_workers = n_workers
        self.quality_check = quality_check

        self.wavelengths = wavelengths
        dirs = [str(wl) for wl in self.wavelengths]
        [(Path(ds_path) / wl).mkdir(parents=True, exist_ok=True) for wl in dirs]

        self.logger = self.get_logger('SOHOEITDownloader')

        if level == 'L0':
            self.root = "https://umbra.nascom.nasa.gov/pub/eit/lz/"
        if level == 'L1':
            self.root = "https://umbra.nascom.nasa.gov/pub/eit/l1/"
    
    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler("{0}/{1}.log".format(self.ds_path, "info_log"))
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger
    
    def download(self, sample):
        """
        Download the data from SDAC.

        Args:
            sample (pandas Series): pandas Series containing the obstime, wavelength, and url.

        Returns:
            str: Path to the downloaded file.
        """
        dir = Path(self.ds_path) / str(sample.wavelength)
        # t = round_hour(sample.obstime) if self.round else sample.obstime
        # tt = t.isoformat('T', timespec='seconds').replace(':', '')
        tt = sample.dateobs
        fits_path = dir / f"{tt}.fits"
        if fits_path.exists():
            return fits_path
        download_url(sample.url, filename=fits_path, desc=str(sample.wavelength))
        return fits_path
    
    @staticmethod
    def get_idx(file_list, date):
        # find the first index of the file that has the same hour as the date
        for i, f in enumerate(file_list):
            obstime = datetime.strptime(f.get('href')[3:], "%Y%m%d.%H%M%S")
            if obstime.hour == date.hour:
                return i
            
    def get_data_level0(self, soho_url, fts_list):
        # Create url list until all possible wavelengths are found.
        possible_values = set(self.wavelengths)
        seen_values = set()

        data = []
        for f in fts_list:
            url = soho_url + f.get('href')
            header = fits.getheader(url)
            if header['NAXIS1'] != 1024 or header['NAXIS2'] != 1024 or \
                'N_MISSING_BLOCKS =    0' not in header['COMMENT'][-1]:
                print("Invalid file:", f.get('href'))
                continue
            
            info = {}
            info['obstime'] = datetime.strptime(f.get('href')[3:], "%Y%m%d.%H%M%S")
            info['dateobs'] = datetime.strptime(header['DATE-OBS'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y%m%d_%H%M%S")
            info['wavelength'] = header['WAVELNTH']
            info['url'] = url
            data.append(info)

            seen_values.add(int(header['WAVELNTH']))
            if seen_values == possible_values:
                break

        df = pd.DataFrame(data)
        df_171 = df[df['wavelength'] == 171].sort_values(by='obstime').reset_index(drop=True)
        df_195 = df[df['wavelength'] == 195].sort_values(by='obstime').reset_index(drop=True)
        df_284 = df[df['wavelength'] == 284].sort_values(by='obstime').reset_index(drop=True)
        df_304 = df[df['wavelength'] == 304].sort_values(by='obstime').reset_index(drop=True)
        
        queue = []
        queue.append(df_171.iloc[0])
        queue.append(df_195.iloc[0])
        queue.append(df_284.iloc[0])
        queue.append(df_304.iloc[0])
        return queue
    
    @staticmethod
    def get_sample(df, date):
        check = True
        while check:
            sample = df.iloc[(df['obstime'] - date).abs().idxmin()]
            header = fits.getheader(sample.url)
            if header['NAXIS1'] != 1024 or header['NAXIS2'] != 1024 or header['MSBLOCKS'] != 0:
                df.drop(sample.name, inplace=True)
            else:
                check = False
        sample = sample.copy()
        sample['dateobs'] = datetime.strptime(header['DATE-OBS'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d_%H%M%S")
        return sample
    
    def get_data_level1(self, soho_url, file_list, date):
        data = []
        for f in file_list:
            url = soho_url + f.get('href')
            info = {}
            info['obstime'] = datetime.strptime(f.get('href')[13:-8], "%Y%m%dT%H%M%S")
            info['wavelength'] = int(f.get('href')[9:12])
            info['url'] = url
            data.append(info)

        df = pd.DataFrame(data)
        df_171 = df[df['wavelength'] == 171].sort_values(by='obstime').reset_index(drop=True)
        df_195 = df[df['wavelength'] == 195].sort_values(by='obstime').reset_index(drop=True)
        df_284 = df[df['wavelength'] == 284].sort_values(by='obstime').reset_index(drop=True)
        df_304 = df[df['wavelength'] == 304].sort_values(by='obstime').reset_index(drop=True)

        sample_171 = self.get_sample(df_171, date)
        sample_195 = self.get_sample(df_195, date)
        sample_284 = self.get_sample(df_284, date)
        sample_304 = self.get_sample(df_304, date)

        queue = []
        queue.append(sample_171)
        queue.append(sample_195)
        queue.append(sample_284)
        queue.append(sample_304)
        return queue
    
    def get_queue(self, date):
        queue = []

        if self.level == 'L0':
            d = datetime.strftime(date, "%Y/%m/")
            soho_url = self.root + d
        if self.level == 'L1':
            d = datetime.strftime(date, "%Y/%m/%d/")
            soho_url = self.root + d
        
        bs = get_bs(soho_url)
        if bs:
            if self.level == 'L0':
                file_re = re.compile("efz"+datetime.strftime(date, "%Y%m%d") + ".*")
            if self.level == 'L1':
                file_re = re.compile("SOHO_EIT"+".*"+datetime.strftime(date, "%Y%m%d") + ".*.fits")
            file_list = bs.find_all('a', {'href': file_re})
            if len(file_list) > 0:
                if self.level == 'L0':
                    i = self.get_idx(file_list, date)
                    file_list = file_list[i:]
                    queue = self.get_data_level0(soho_url, file_list)
                if self.level == 'L1':
                    queue = self.get_data_level1(soho_url, file_list, date)
        else:
            self.logger.info(f"No files found")
            return queue
        return queue
    
    def downloadDate(self, date):
        """
        Download the data for the given date.

        Args:
            date (datetime): The date for which the data should be downloaded.

        Returns:
            list: List of paths to the downloaded files.
        """
        t = date.isoformat()
        self.logger.info(f"Start download: {t}")

        queue = self.get_queue(date)

        with multiprocessing.Pool(self.n_workers) as p:
            files = p.map(self.download, queue)
        self.logger.info(f"Finished: {t}")
        return files
    

if __name__ == '__main__':
    from itipy.download.util import get_timedelta

    parser = argparse.ArgumentParser(description='Download SOHO/EIT data from SDAC with quality check')
    parser.add_argument('--ds_path', type=str, help='path to the download directory.')
    parser.add_argument('--n_workers', type=str, help='number of parallel threads.', required=False, default=4)
    parser.add_argument('--start_date', type=str, help='start date in format YYYY-MM-DD.')
    parser.add_argument('--end_date', type=str, help='end date in format YYYY-MM-DD.', required=False, default=str(datetime.now()).split(' ')[0])
    parser.add_argument('--cadence', type=str, help='cadence for the download.', required=False, default="1days")

    args = parser.parse_args()

    downloader = SOHOEITDownloader(ds_path=args.ds_path, n_workers=args.n_workers)

    t_start = datetime.strptime(args.start_date, "%Y-%m-%d")
    t_end = datetime.strptime(args.end_date, "%Y-%m-%d")
    td = get_timedelta(args.cadence)
    date_list = [t_start + i * td for i in range((t_end - t_start) // td)]

    import warnings; warnings.filterwarnings("ignore")
    for d in date_list:
        downloader.downloadDate(d)