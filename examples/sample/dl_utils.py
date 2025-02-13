from urllib import request
from tqdm import tqdm
# https://github.com/tqdm/tqdm?tab=readme-ov-file#hooks-and-callbacks
class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize
    
def download_url(url, filename):
    with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                  desc=url.split('/')[-1]) as t:  # all optional kwargs
        request.urlretrieve(url, filename=filename,
                            reporthook=t.update_to, data=None)
        t.total = t.n