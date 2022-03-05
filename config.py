from pathlib import Path

reset_db = False
migrage = False

db_params = {'dbname': 'dsdb',
            'user': 'postgres',
            'password': 'hHce3me47fipkFe',
            'host': '10.0.40.21'
            }

DATASET_DIR = Path(r'/data/datasets/ds.med/ECG/NPY')