import numpy as np
import pandas as pd
from tqdm import tqdm

def is_in_poly(p, poly):
    """
    :param p: [x, y]
    :param poly: [[], [], [], [], ...]
    :return:
    """
    px, py = p
    is_in = False
    for i, corner in enumerate(poly):
        next_i = i + 1 if i + 1 < len(poly) else 0
        x1, y1 = corner
        x2, y2 = poly[next_i]
        if (x1 == px and y1 == py) or (x2 == px and y2 == py):  # if point is on vertex
            is_in = True
            break
        if min(y1, y2) < py <= max(y1, y2):  # find horizontal edges of polygon
            x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x == px:  # if point is on edge
                is_in = True
                break
            elif x > px:  # if point is on left-side of line
                is_in = not is_in
    return is_in

def remove_missing_lanes(df):
    # Find all lanes with missing edge information
    #missing_edges = df[df['edge'].isnull() | (df['edge'] == '')]['lane'].unique()
    # Remove all rows with missing edge information
    df = df.dropna(subset=['edge'])
    # Remove all rows with missing lane information for the previously identified lanes
    #df = df[~df['lane'].isin(missing_edges)]
    return df

if __name__ == "__main__":
    d = pd.read_csv("/media/ubuntu/ANL/Data3.csv")
    col_name = d.columns.tolist()
    col_name.insert(6, 'edge')
    col_name.insert(7, 'lane')

    net = np.load('net.npy', allow_pickle=True).item()

    with tqdm(total=len(d)) as pbar:
        for i, row in d.iterrows():
            for edge in net:
                for lane in net[edge]:
                    if is_in_poly([row['x_pix'], row['y_pix']], net[edge][lane]):
                        d.at[i, 'edge'] = edge
                        d.at[i, 'lane'] = lane
                        break
                else:
                    continue
                break
            pbar.update(1)
        #d[['edge', 'lane']] = np.array(d[['edge', 'lane']], dtype=str)
    pbar.close()

    d = remove_missing_lanes(d)
    d['lane'] = d['lane'].astype(int)
    d.to_csv(path_or_buf="/media/ubuntu/ANL/Data3_lane.csv", index=False)
