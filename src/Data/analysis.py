'''
    Provides functions to analyze the observation data, including statistical analysis and data summarization.
    @file analysis.py
    @author Quentin Bordelon
    <pre>
    Date: 14-03-2026

    MIT License

    Contact Information: qborde1@lsu.edu
    Copyright (c) 2026 Quentin Bordelon

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    </pre>
''' 

import numpy as np
import math
import pandas as pd
from scipy.stats import chi2_contingency
import os, concurrent.futures
from tqdm import tqdm

import popdensity, observations

def getFilePath(lat: float, lon: float, year: int) -> str:
    if year > 2000:
        path = popdensity.buildPath(lat, lon, year)
        return path + "populationDensity.tif"
    else:
        return f'./Research/Historic/{year}/popc_{year}AD.asc'

def processGroup(args) -> list:
    filePath, indices, coords, year, progress = args
    if year > 2000:
        metrics = popdensity.getAllMetricsBatch(filePath, coords)
    else:
        metrics = popdensity.getAllMetricsBatchASC(year, coords)

    progress.update(len(coords))
    return [(idx, *m) for idx, m in zip(indices, metrics)]

def processParquetData(inputParquet, outputParquet):
    # https://www2.census.gov/geo/pdfs/reference/ua/Census_UA_CritDiff_2010_2020.pdf
    # https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html

    URBAN_THRESHOLD = 1500

    dataFrame = pd.read_parquet(inputParquet)

    before = len(dataFrame)
    dataFrame = dataFrame.dropna()

    dataFrame = dataFrame[dataFrame["year"] >= 2015]
    dataFrame = dataFrame[dataFrame["quality"] == "research"]

    downloadTasks = []
    uniqueCombos = dataFrame[['latitude', 'longitude', 'year']].drop_duplicates()

    badCoords = uniqueCombos[
        ~uniqueCombos['latitude'].apply(lambda v: math.isfinite(float(v))) |
        ~uniqueCombos['longitude'].apply(lambda v: math.isfinite(float(v)))
    ]
    if not badCoords.empty:
        uniqueCombos = uniqueCombos.drop(badCoords.index)

    uniqueCoords = [
        (float(r.latitude), float(r.longitude))
        for r in uniqueCombos.itertuples(index=False)
    ]
    popdensity.prewarmGeocodeCache(uniqueCoords)

    #tqdm just tells me when I should start worrying about my analysis not working
    seen_tiles = set()
    for _, row in tqdm(uniqueCombos.iterrows(), total=len(uniqueCombos), desc="Building download list", unit="coord", dynamic_ncols=True):
        lat, lon, year = float(row['latitude']), float(row['longitude']), int(row['year'])
        path = popdensity.buildPath(lat, lon, year)
        iso, _, state, _ = popdensity.getCountry(lat, lon)
        url = popdensity.buildUrl(iso, year, state)
        filePath = path + "populationDensity.tif"
        if filePath not in seen_tiles:
            seen_tiles.add(filePath)
            downloadTasks.append((url, path, filePath))

    def safeDownload(task):
        url, path, filePath = task
        if not os.path.exists(filePath):
            try:
                popdensity.downloadCountryMap(url, path, filePath)
            except Exception as e:
                print(f"Download failed for {url}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        list(tqdm(executor.map(safeDownload, downloadTasks), total=len(downloadTasks)))

    tqdm.pandas(desc="Assigning tile paths", unit="row", dynamic_ncols=True)
    dataFrame['_filePath'] = dataFrame.progress_apply(
        lambda r: getFilePath(float(r['latitude']), float(r['longitude']), int(r['year'])),
        axis=1
    )

    tasks = []
    totalRows = len(dataFrame)
    for filePath, group in dataFrame.groupby('_filePath'):
        year = int(group['year'].iloc[0])
        indices = list(group.index)
        coords = list(zip(group['latitude'].astype(float), group['longitude'].astype(float)))
        tasks.append((filePath, indices, coords, year)) 

    results = {} 

    with tqdm(total=totalRows, unit="obs", desc="Spatial metrics", dynamic_ncols=True) as progress:
        tasksWithProgress = [(fp, idx, coords, yr, progress) for fp, idx, coords, yr in tasks]
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for batch in executor.map(processGroup, tasksWithProgress):
                for idx, totalPop, maxDensity, populationDensity in batch:
                    results[idx] = (totalPop, maxDensity, populationDensity)
                progress.update(len(batch))

    dataFrame['nearbyPopulation'] = [results[i][0] for i in dataFrame.index]
    dataFrame['maxDensity'] = [results[i][1] for i in dataFrame.index]
    dataFrame['populationDensity'] = [results[i][2] for i in dataFrame.index]
    dataFrame = dataFrame.drop(columns=['_filePath'])

    dataFrame['isUrban'] = dataFrame['nearbyPopulation'] >= URBAN_THRESHOLD
    dataFrame.to_parquet(outputParquet, index=False, compression='snappy')

def calculateCramersV(contingencyTable, chi2):
    n = contingencyTable.sum().sum()
    phi2 = chi2 / n
    r, k = contingencyTable.shape
    phi2Corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rCorr = r - ((r-1)**2)/(n-1)
    kCorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2Corr / min((kCorr-1), (rCorr-1)))

def chiSquaredPerSpecies(dataFrame, alpha=0.05):
    species = dataFrame['taxonName'].dropna().unique()

    # here I get to talk about the bonferroni correction and its fancy math
    correctedAlpha = alpha / len(species)  
 
    rows = []
    for taxon in species:
        isSpecies = dataFrame['taxonName'] == taxon
 
        a = (isSpecies  &  dataFrame['isUrban']).sum()
        b = (isSpecies  & ~dataFrame['isUrban']).sum()
        c = (~isSpecies &  dataFrame['isUrban']).sum()
        d = (~isSpecies & ~dataFrame['isUrban']).sum()
 
        contingencyTable = np.array([[a, b], [c, d]])
 
        if contingencyTable.min() == 0:
            continue
 
        chi, p, _, _ = chi2_contingency(contingencyTable)
        cramersV = calculateCramersV(contingencyTable, chi)
        rows.append({
            'taxonName': taxon,
            'chi2': chi,
            'pValue': p,
            'cramersV': cramersV,
            'urbanCount': int(a),
            'nonUrbanCount': int(b),
        })
 
    results = pd.DataFrame(rows).sort_values('pValue')
 
    significant = results[results['pValue'] < correctedAlpha].copy()
 
    return significant

if __name__ == "__main__":
    observations.main()
    processParquetData("./Research/observations.parquet", "./Research/processedObservations.parquet")
