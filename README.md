![Black](https://github.com/lpicci96/unesco_reader/actions/workflows/code_format.yml/badge.svg)
# UNESCO Institute for Statistics (UIS) Reader

A programmatic and pythonic way to extract data from UNESCO Institute of Statistics (UIS) [bulk download services](https://apiportal.uis.unesco.org/bdds). This package lets you extract bulk data, specific indicators, or metadata from all UIS datasets. This package is currently a beta version and could be unstable. No testing has been done yet.

## Motivation

Currently there is so API service to query UIS data (as of [23 June 2020](https://apiportal.uis.unesco.org/)). The only way to download UIS data is through their [bulk download services](https://apiportal.uis.unesco.org/bdds), by locally downloading a zipped folder for each dataset. This package removes the need to download files locally and lets you extract the data directly into a pandas dataframe. 

## Installation

unesco_reader is currently published on Test PYPI. 

```
pip install -i https://test.pypi.org/simple/ unesco-reader
```

The package depends on pandas and requests

## Usage

1. **Importing**

```
import unesco_reader as uis
```

2. **Extracting data**

Return a dataframe of available datasets to query. This will return a dataframe with dataset name, code, category, and a link to download the zipped folder

```
available_datasets = uis.datasets()
```

Return a list of available indicators (with their codes) for a specific dataset. Here we are returning a list of indicators for the SDG Education dataset.

```
indicators = uis.indicators('SDG')
```

extract all data for a specific dataset
```
df = uis.get_bulk('SDG')
```

Additionally, the geographical grouping can be specified as "NATIONAL" for country level grouping or "REGIONAL" for region level grouping. By default the grouping is set to "NATIONAL".

```
df = uis.get_bulk('SDG', grouping = 'REGIONAL')
```
A specific indicator for a dataset can be extracted along with the desired geographical grouping as above. Below the indicator "Adult literacy rate, population 15+ years, both sexes (%)" is extracted.

```
df = uis.get_indicator('LR.AG15T99', 'SDG')
```

3. Unzipping files

Additionally, the unzipping functionality can be using on other CSV files in a zipped folder, without needing to store the file locally. By speficying the downloadable link for the zipped folder and file name in the function below, the CSV will be read to a pandas dataframe

```
unzipped_df = read_zip(url, file.csv)
```

## License

[MIT](https://github.com/lpicci96/unesco_reader/blob/main/LICENSE)




