import pandas as pd

class Transformer:

    def __init__(self, data: str, saving_path: str):
        """
        - data: Path of your csv file.
        - saving_path: Path to save the csv file.
        """

        self.data = data
        self.saving_path = saving_path
        try:
            self.df = pd.read_csv(self.data)
        except:
            raise FileNotFoundError(f"The path {data} does not exist. Check the string typed.")

    def drop_columns(self):

        df_copy = self.df.copy()

        new_df = df_copy.drop(columns=['routes_alt', 'routes_vayven','alt_fare_amount', 'passenger_count'])
        return new_df

    def duplicates(self, df: pd.DataFrame):
        df = df
        print(f'The dataset has {df.duplicated(subset=["transaction_id"]).sum()} duplicates.')

        df_2 = df.drop_duplicates(subset=['transaction_id'])
        return df_2

    def missing_values(self, df: pd.DataFrame):
        df = df
        print(f'The dataset contains {df.isna().sum().sum()} missing values.')

        df_3 = df.dropna()
        return df_3
    
    def convert_dtypes(self, df: pd.DataFrame):
        df_4 = df
        df_4['transaction_time'] = pd.to_datetime(df_4['transaction_time'], format='%H:%M:%S')
        df_4['trip_duration_minutes'] = pd.to_timedelta(df_4['trip_duration_minutes'], unit='m')
        df_4['transaction_date'] = pd.to_datetime(df_4['transaction_date'], format='%Y/%m/%d')
        print(f"Data types converted successfully.\n{df.info()}")
        return df_4

    def aggregations(self, df: pd.DataFrame):
        df = df
        df = df.sort_values(by=['transaction_date', 'transaction_time']).reset_index(drop=True)
        df['descending_time'] = pd.to_datetime(df['transaction_time'] + df['trip_duration_minutes'])
        df['passenger_count'] = 0
        previous_time = pd.to_datetime("4:59:59", format= "%H:%M:%S")
        previous_date = pd.to_datetime("2020/1/1", format="%Y/%m/%d")
        for index_number in range(len(df)):
            if previous_date < df['transaction_date'].iloc[index_number]:
                passenger_bording = 0
                previous_time = pd.to_datetime("4:59:59", format= "%H:%M:%S")
            current = df['transaction_time'].iloc[index_number]
            if current < previous_time or passenger_bording == 0:
                passenger_bording = passenger_bording + 1
            elif current >= previous_time:
                passenger_bording = passenger_bording - 1
            df.loc[index_number, 'passenger_count'] = passenger_bording
            previous_time = df['descending_time'].iloc[index_number]
            previous_date = df['transaction_date'].iloc[index_number]
        df.replace({'passenger_count': {0: 1}}, inplace=True)
        return df
    
    def transformation(self):
        df_1 = self.drop_columns()
        df_2 = self.duplicates(df_1)
        df_3 = self.missing_values(df_2)
        df_4 = self.convert_dtypes(df_3)
        df_list = []
        for route in list(df_4['route_type'].unique()):
            df_route = df_4[df_4['route_type'] == route]
            df_temp = self.aggregations(df_route)
            df_list.append(df_temp)
        df_final = pd.concat(df_list).reset_index(drop=True)
        return df_final

    def loader(self, df_processed: pd.DataFrame):
        df_processed.to_csv(f'{self.saving_path}', index= False)
        return print(f'Processed dataset successfully saved in {self.saving_path}.')
    
if __name__ == '__main__':
    
    import os

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.abspath(os.path.join(BASE_PATH, "..", "data"))
    cleaning = Transformer(f'{FILE_PATH}/transportation.csv', f'{FILE_PATH}/processed.csv')
    cleaning.transformation()