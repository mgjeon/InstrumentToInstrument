# compare samples/soho,stereo & iti-dataset/soho,stereo
# => Same

from pathlib import Path
rootA = Path('samples')
rootB = Path('iti-dataset')

fitsA = list(rootA.glob('soho/**/*.fits')) + list(rootA.glob('stereo/**/*.fits'))
fitsA = sorted(fitsA)
fitsB = list(rootB.glob('soho/**/*.fits')) + list(rootB.glob('stereo/**/*.fits'))
fitsB = sorted(fitsB)

print(f'Number of files in {rootA}: {len(fitsA)}')
print(f'Number of files in {rootB}: {len(fitsB)}')

for i, (fA, fB) in enumerate(zip(fitsA, fitsB)):
    print(i, fA.name, fB.name)
    
    c_filename = fA.name == fB.name
    c_filesize = fA.stat().st_size == fB.stat().st_size
    c_content = fA.read_bytes() == fB.read_bytes()

    print("Same filename?", c_filename)
    print("Same filesize?", c_filesize)
    print("Same content?", c_content)

    c_whole = c_filename and c_filesize and c_content
    print("Whole comparison:", c_whole)

    if not c_whole:
        break

"""
Number of files in samples: 9
Number of files in iti-dataset: 9
0 2007-12-13T07:19:35.fits 2007-12-13T07:19:35.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
1 2007-12-13T07:19:35.fits 2007-12-13T07:19:35.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
2 2007-12-13T07:19:35.fits 2007-12-13T07:19:35.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
3 2007-12-13T07:19:35.fits 2007-12-13T07:19:35.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
4 2007-12-13T07:19:35.fits 2007-12-13T07:19:35.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
5 2016-12-28T00:14:00.fits 2016-12-28T00:14:00.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
6 2016-12-28T00:14:00.fits 2016-12-28T00:14:00.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
7 2016-12-28T00:14:00.fits 2016-12-28T00:14:00.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
8 2016-12-28T00:14:00.fits 2016-12-28T00:14:00.fits
Same filename? True
Same filesize? True
Same content? True
Whole comparison: True
"""