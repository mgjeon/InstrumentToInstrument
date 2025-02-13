"""
python dl_sample.py

=> amples/soho,stereo & iti-dataset/soho,stereo are the same
"""

import shutil
import os
from dl_utils import download_url

dl_path = "samples"

if not os.path.exists(dl_path):
    os.makedirs(dl_path)
    # Download the samples.zip file from the server
    url = "http://kanzelhohe.uni-graz.at/iti/samples.zip"
    filename = "samples.zip"
    download_url(url, filename)

    # Unpack the samples.zip file and remove it
    shutil.unpack_archive(filename, dl_path)
    os.remove(filename)
else:
    print("Samples already downloaded.")