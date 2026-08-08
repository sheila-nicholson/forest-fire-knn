# BC Forest Fire Size Classification

This project uses historical British Columbia wildfire, weather station and municipality data to classify forest fires as either:

- **Small fire:** less than 100 hectares
- **Large fire:** 100 hectares or greater

Three machine learning models are compared:

- K-Nearest Neighbours (KNN)
- Random Forest
- XGBoost

The models use nearby weather observations and municipality characteristics to predict whether a wildfire will grow to 100 hectares or greater. The analysis focuses on wildfires occurring between 2019 and 2023.
## Setup

This project was developed using Python 3.12. The following additional Python packages are required:

- pandas
- numpy
- geopandas
- matplotlib
- scikit-learn
- xgboost
- requests

These packages can be installed using:

```bash
pip install pandas numpy geopandas matplotlib scikit-learn xgboost requests
```
## Running the Project

The scripts are designed to be run individually from the root directory of the repository. They should be run in the following order:

#### 1. Download the historical wildfire data

```bash
python import_data_fires.py
```

#### 2. Download the municipality boundary data

```bash
python import_data_municipalities.py
```

#### 3. Process the historical wildfire datasets

```bash
python process_data_fires.py
```

#### 4. Process the municipality boundary and population datasets

```bash
python process_data_municipalities.py
```

#### 5. Process the weather observation and weather station datasets

```bash
python process_data_weather.py
```

The BC Wildfire Service weather data must be downloaded manually before running this script. Weather observation and station files for each year from 2019 to 2023 should be placed in the appropriate `raw_data/weather` directory.

#### 6. Calculate geographical distances

Calculate the distance from each fire to its nearest weather station and municipality:

```bash
python compute_distances.py
```

#### 7. Generate the model features

```bash
python feature_engineering.py
```

This step creates the final dataset used by the machine learning models.

#### 8. Generate the exploratory analysis plots

```bash
python exploratory_analysis.py
```

Generated figures are saved in the `plots` directory.

#### 9. Train and evaluate the models

```bash
python model.py
```

This script trains and evaluates the K-Nearest Neighbours, Random Forest and XGBoost models using 5-fold stratified cross-validation.

The primary performance metrics are:

- Balanced accuracy
- ROC AUC
- Large-fire F1 score

All scripts should be run from the root `forest-fire-knn` directory since relative paths are used to access the `raw_data`, `intermediate_data` and `plots` directories.