import pandas as pd
import numpy as np

class Transformer:

    def __init__(self, data: str, saving_path: str):
        """
        - data: Path of your csv file.
        - saving_path: Path to save the csv file.
        """

        self.data = data
        self.saving_path = saving_path
        
        # --- START OF FIX ---
        if self.data is not None:
            try:
                self.df = pd.read_csv(self.data)
            except Exception:
                # Catch any error during read and raise a FileNotFoundError (or the specific error if desired)
                raise FileNotFoundError(f"The path {data} does not exist or file is unreadable. Check the string typed.")
        else:
            # If data is None, we skip reading the file. This instance is for saving/loading only.
            self.df = None

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
        if self.data == None:
            df_processed.to_csv(f'{self.saving_path}', index= False)
            return print(f'Processed dataset successfully saved in {self.saving_path}.')
        else:
            return print(f'Processed dataset successfully saved in {self.saving_path}.')
        
# ============================================================
#               NEW URBAN SENSOR TRANSFORMATION
# ============================================================

class UrbanSensorTransformer:

    def __init__(self, data: str, saving_path: str):
        """
        - data: Path of `urban-sensors.csv`
        - saving_path: Path to save processed file.
        """
        self.data = data
        self.saving_path = saving_path

        try:
            self.df = pd.read_csv(self.data)
        except Exception:
            raise FileNotFoundError(
                f"Urban-sensor file {data} not found or unreadable."
            )

    # ------------------------------------------------------------
    # Step 1 — Cleaning missing values
    # ------------------------------------------------------------
    def clean_missing(self, df: pd.DataFrame):
        print(f"Missing values before cleaning: {df.isna().sum().sum()}")

        # Strategy:
        # - Drop rows missing sensor_id or timestamp (critical)
        df = df.dropna(subset=["sensor_id", "ts"])

        # - Fill numeric missing values with median
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            df[col] = df[col].fillna(df[col].median())

        # - Fill categorical with mode
        cat_cols = df.select_dtypes(include=["object"]).columns
        for col in cat_cols:
            df[col] = df[col].fillna(df[col].mode()[0])

        print(f"Missing values after cleaning: {df.isna().sum().sum()}")
        return df

    # ------------------------------------------------------------
    # Step 2 — Fixing data types
    # ------------------------------------------------------------
    def fix_types(self, df: pd.DataFrame):
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

        df["vehicle_count"] = df["vehicle_count"].astype(int)
        df["avg_speed_kmh"] = df["avg_speed_kmh"].astype(float)
        df["noise_db"] = df["noise_db"].astype(float)
        df["pm25"] = df["pm25"].astype(float)
        df["pm10"] = df["pm10"].astype(float)

        return df

    # ------------------------------------------------------------
    # Step 3 — Feature engineering
    # ------------------------------------------------------------
    def create_features(self, df: pd.DataFrame):
        # Extract time components
        df["hour"] = df["ts"].dt.hour
        df["day"] = df["ts"].dt.date
        df["is_peak_hour"] = df["hour"].isin([7, 8, 9, 17, 18, 19]).astype(int)

        # Pollution index
        df["pollution_idx"] = df["pm25"] * 0.6 + df["pm10"] * 0.4

        # Noise class
        df["noise_level"] = pd.cut(
            df["noise_db"],
            bins=[0, 40, 70, 120],
            labels=["Low", "Moderate", "High"]
        )

        return df

    # ------------------------------------------------------------
    # Step 4 — Aggregations (for dashboards)
    # ------------------------------------------------------------
    def build_aggregations(self, df: pd.DataFrame):
        agg_hourly = (
            df.groupby(["location", "day", "hour"])
            .agg({
                "vehicle_count": "mean",
                "avg_speed_kmh": "mean",
                "pm25": "mean",
                "pm10": "mean",
                "pollution_idx": "mean",
                "noise_db": "mean"
            })
            .reset_index()
        )

        # Save aggregated file
        hourly_path = self.saving_path.replace(".csv", "_aggregated.csv")
        agg_hourly.to_csv(hourly_path, index=False)
        print(f"Aggregated dashboard file saved at {hourly_path}")

        return df, agg_hourly

    # ------------------------------------------------------------
    # Master transformation pipeline
    # ------------------------------------------------------------
    def transform(self):
        df = self.df.copy()
        df = self.clean_missing(df)
        df = self.fix_types(df)
        df = self.create_features(df)
        df, agg = self.build_aggregations(df)
        return df

    # ------------------------------------------------------------
    # Save processed dataset
    # ------------------------------------------------------------
    def save(self):
        df_processed = self.transform()
        df_processed.to_csv(self.saving_path, index=False)
        print(f"Urban-sensor processed dataset saved at {self.saving_path}")

# ============================================================
#               PRODUCT EVENT TRANSFORMATION
# ============================================================

class ProductEventTransformer:

    def __init__(self, data: str, saving_path: str):
        """
        - data: Path of raw `product-events` csv
        - saving_path: Path to save processed file.
        """
        self.data = data
        self.saving_path = saving_path

        try:
            self.df = pd.read_csv(self.data)
        except Exception:
            # Create an empty DF if file is missing to avoid crashing
            self.df = pd.DataFrame(columns=[
                "event_id", "timestamp", "user_id", "session_id", "event_type", 
                "product_id", "category", "price", "platform"
            ])

    def clean_and_format(self, df: pd.DataFrame):
        # Ensure timestamp is datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        
        # Fill optional fields for non-purchase events
        if "purchase_amount" not in df.columns:
            df["purchase_amount"] = 0.0
        else:
            df["purchase_amount"] = df["purchase_amount"].fillna(0.0)
            
        return df

    def generate_kpis(self, df: pd.DataFrame):
        """
        Generates two aggregated datasets:
        1. Category Performance (Views vs Revenue)
        2. Funnel Analysis (View -> Cart -> Purchase counts)
        """
        if df.empty:
            return None, None

        # --- KPI 1: Category Performance ---
        cat_stats = df.groupby("category").agg(
            total_views=('event_type', lambda x: (x == 'product_view').sum()),
            total_purchases=('event_type', lambda x: (x == 'purchase').sum()),
            total_revenue=('purchase_amount', 'sum')
        ).reset_index()
        
        # --- KPI 2: Overall Funnel ---
        funnel_counts = df['event_type'].value_counts().reset_index()
        funnel_counts.columns = ['stage', 'count']
        
        return cat_stats, funnel_counts

    def transform(self):
        df = self.df.copy()
        df = self.clean_and_format(df)
        
        # Save the detailed processed data
        df.to_csv(self.saving_path, index=False)
        print(f"Processed product events saved at {self.saving_path}")

        # Generate and save KPI dashboards
        cat_stats, funnel = self.generate_kpis(df)
        
        if cat_stats is not None:
            kpi_path_cat = self.saving_path.replace(".csv", "_kpi_category.csv")
            cat_stats.to_csv(kpi_path_cat, index=False)
            print(f"Category KPI saved at {kpi_path_cat}")

        if funnel is not None:
            kpi_path_funnel = self.saving_path.replace(".csv", "_kpi_funnel.csv")
            funnel.to_csv(kpi_path_funnel, index=False)
            print(f"Funnel KPI saved at {kpi_path_funnel}")
            
        return df

    def save(self):
        self.transform()
    
if __name__ == '__main__':
    
    import os

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.abspath(os.path.join(BASE_PATH, "..", "data"))
    cleaning = Transformer(f'{FILE_PATH}/transportation.csv', f'{FILE_PATH}/processed.csv')
    cleaning.transformation()