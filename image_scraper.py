from multiprocessing import Process, Manager
import urllib
import os
import pandas as pd
import time
import http

root = 'Data/Input/ufo-stalker-images'

def _wrapper(id_val, df, sleep):
    for j, r in df.iterrows():
        base_path = os.path.join(root, r['shape'])
        # create directory if it does not already exist
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        # get image extension
        ext = r['urls'].rsplit('.', 1)[-1]
        try:
            full_path = os.path.join(base_path, '{}.{}'.format(r['event_id'], ext))
            urllib.request.urlretrieve(r['urls'], full_path)
        except (
            urllib.request.HTTPError, 
            UnicodeEncodeError, 
            urllib.error.URLError, 
            http.client.RemoteDisconnected):
            continue

        print('<Process {:2d}>\t{}'.format(id_val, full_path))

    print('<Process {:2d}>\tCompleted'.format(id_val))


def dispatch_job(df, nproc=8, sleep=0):
    with Manager() as manager:
        q = manager.Queue()

        processes = []
        for i, g in enumerate(pd.np.array_split(df, max(1, nproc)), 1):
            p = Process(target=_wrapper, args=(i, g, sleep))
            processes.append(p)

            p.daemon = True
            p.start()
            
        for p in processes:
            p.join()

if __name__ == '__main__':    
    df = pd.read_csv('Data/ufo_stalker_image_data.csv', index_col=[0])
    dispatch_job(df, nproc=8, sleep=0)


