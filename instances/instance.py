import os
import pandas as pd
import numpy as np

class Instance():
    def __init__(self, dataset_name):
        self.name = dataset_name
        self.df_items = pd.read_csv(
            os.path.join('.', 'datasets', self.name, 'items.csv'),
            index_col = 0,
            dtype={"allowedRotations": str}
        )
        self.df_vehicles = pd.read_csv(
            os.path.join('.', 'datasets', self.name, 'vehicles.csv'),
            index_col = 0
        )
    
    def __repr__(self):
        output = ''
        output += f'--- ITEMS ---\n{self.df_items}\n'
        output += f'--- VEHICLES ---\n{self.df_vehicles}\n'
        return output
    
    def transform(self):

        # Build transformed DataFrame
        df_new = pd.DataFrame({
            'id': self.df_items.index,
            'width': self.df_items['width'],
            'depth': self.df_items['length'],   # assuming length = depth
            'height': self.df_items['height'],
            'weight': self.df_items['weight'],
            'value': self.df_items['weight'],   # value = weight
            'allowedRotations': ['012345'] * len(self.df_items)
        })

        # Save to new CSV
        df_new.to_csv(os.path.join('.', 'datasets', self.name, 'items.csv'), index=False)