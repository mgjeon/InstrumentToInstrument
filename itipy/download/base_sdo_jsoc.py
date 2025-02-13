import logging

import pandas as pd
from astropy.io import fits
from sunpy.io._fits import header_to_fits
from sunpy.util import MetaDict

from itipy.download.util import download_url


class BaseSDOJSOCDownloader:
    """
    Base Class to download SDO data from JSOC.
    """

    def __init__(self):
        pass

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler("{0}/{1}.log".format(self.ds_path, "info_log"))
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger  
    
    def download(self, sample):
        """
        Download the data from JSOC.

        Args:
            sample (tuple): Tuple containing the header, segment and time information.

        Returns:
            str: Path to the downloaded file.
        """
        self.sample = sample    
        header, segment, t = sample
        dir, desc = self.set_dir_desc()
        try:
            tt = t.isoformat('T', timespec='seconds').replace(':', '')
            map_path = dir / ('%s.fits' % tt)
            if map_path.exists():
                return map_path
            # load map
            url = 'http://jsoc.stanford.edu' + segment
            download_url(url, filename=map_path, desc=desc)

            header['DATE_OBS'] = header['DATE__OBS']
            header = header_to_fits(MetaDict(header))
            with fits.open(map_path, 'update') as f:
                hdr = f[1].header
                for k, v in header.items():
                    if pd.isna(v):
                        continue
                    hdr[k] = v
                f.verify('silentfix')

            return map_path
        except Exception as ex:
            self.logger.info('Download failed: %s (requeue)' % header['DATE__OBS'])
            self.logger.info(ex)
            raise ex
        
