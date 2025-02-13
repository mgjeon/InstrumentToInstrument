from pathlib import Path
from dl_utils import download_url

root_url = 'http://kanzelhohe.uni-graz.at/iti/'

# model_path = Path('iti-model')
model_path = Path('iti-dataset/models')
model_path.mkdir(exist_ok=True, parents=True)

name_list = [
    'soho_to_sdo_v0_2.pt',
    'soho_to_sdo_euv_v0_1.pt',
    'stereo_to_sdo_v0_2.pt',
    'stereo_to_sdo_mag_v0_2.pt',
    'kso_low_to_high_v0_2.pt',
    'kso_film_to_ccd_v0_1.pt',
    'hmi_to_hinode_v0_2.pt',
    # 'swap_to_aia_v0_2.pt', -> iti-dataset/models/swap_to_aia_v0_4.pt
    # 'fsi_to_aia_v0_3.pt',  -> iti-dataset/models/fsi_to_aia_v0_3.pt
    # 'aia_to_hri_v0_1.pt'   -> iti-dataset/models/aia_to_hri_v0_1.pt
]

for model_name in name_list:
    print(f'Downloading {model_name}...')
    filename = model_path / model_name
    if not filename.exists():
        try:
            download_url(root_url + model_name, filename)
        except Exception as e:
            print(e)
            continue
    print('Done!')
