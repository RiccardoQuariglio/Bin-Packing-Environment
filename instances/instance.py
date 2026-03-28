import os
import pandas as pd

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
        self.transform_ivancic()
    
    def __repr__(self):
        output = ''
        output += f'--- ITEMS ---\n{self.df_items}\n'
        output += f'--- VEHICLES ---\n{self.df_vehicles}\n'
        return output
    
    def transform_datasets(self):
        N = {
            'DatasetA': 1300,
            'DatasetB': 1300,
            'DatasetC': 1300,
            'DatasetD': 500,
            'DatasetE': 500,
            'DatasetF': 50,
            'DatasetG': 800,
            'DatasetH': 1000,
            'DatasetI': 2000,
            'DatasetJ': 800
        }

        # Build transformed DataFrame
        rotation_map = {
            0: '0',
            1: '01',
            2: '012345'
        }

        df_items_new = pd.DataFrame({
            'id': self.df_items.index,
            'width': self.df_items['width'],
            'depth': self.df_items['length'],
            'height': self.df_items['height'],
            'weight': self.df_items['weight'],
            'value': round(self.df_items['weight'] * (0.5 + self.df_items['stackability_code'] / self.df_items['stackability_code'].max()),1),
            'allowedRotations': self.df_items['stackability_code'].mod(3).map(rotation_map)
        }).sample(n=N[self.name], random_state=42).reset_index(drop=True)

        df_items_new['id'] = df_items_new.index.map(lambda x: f'I{x:04d}')

        # Save to new CSV
        self.df_items = df_items_new
        self.df_items.to_csv(os.path.join('.', 'datasets', self.name, 'items.csv'), index=False)

        df_vehicles_new = pd.DataFrame({
            'type': self.df_vehicles.index,
            'width': self.df_vehicles['width'],
            'depth': self.df_vehicles['length'],
            'height': self.df_vehicles['height'],
            'maxWeight': self.df_vehicles['max_weight'],
            'cost': self.df_vehicles['cost'],
            'maxValue': self.df_vehicles['max_weight'],
            'gravityStrength': [0] * len(self.df_vehicles)
        })

        # Save to new CSV
        self.df_vehicles = df_vehicles_new
        self.df_vehicles.to_csv(os.path.join('.', 'datasets', self.name, 'vehicles.csv'), index=False)
    
    def transform_ivancic(self):
        N = {
            'DatasetA': 1300,
            'DatasetB': 1300,
            'DatasetC': 1300,
            'DatasetD': 500,
            'DatasetE': 500,
            'DatasetF': 50,
            'DatasetG': 800,
            'DatasetH': 1000,
            'DatasetI': 2000,
            'DatasetJ': 800
        }

        # Build transformed DataFrame
        rotation_map = {
            0: '0',
            1: '01',
            2: '012345'
        }

        df_items_new = pd.DataFrame({
            'id': self.df_items.index,
            'width': self.df_items['width'],
            'depth': self.df_items['length'],
            'height': self.df_items['height'],
            'weight': self.df_items['weight'],
            'value': round(self.df_items['weight'] * (0.5 + self.df_items['stackability_code'] / self.df_items['stackability_code'].max()),1),
            'allowedRotations': ['012345'] * len(self.df_items)
        }).reset_index(drop=True)

        df_items_new['id'] = df_items_new.index.map(lambda x: f'I{x:04d}')

        # Save to new CSV
        self.df_items = df_items_new
        self.df_items.to_csv(os.path.join('.', 'datasets', self.name, 'items.csv'), index=False)

        df_vehicles_new = pd.DataFrame({
            'type': self.df_vehicles.index,
            'width': self.df_vehicles['width'],
            'depth': self.df_vehicles['length'],
            'height': self.df_vehicles['height'],
            'maxWeight': self.df_vehicles['max_weight'],
            'cost': self.df_vehicles['cost'],
            'maxValue': self.df_vehicles['max_weight'],
            'gravityStrength': [75] * len(self.df_vehicles)
        })

        # Save to new CSV
        self.df_vehicles = df_vehicles_new
        self.df_vehicles.to_csv(os.path.join('.', 'datasets', self.name, 'vehicles.csv'), index=False)