'''
    Provides functions to create various graphs and visualizations based on the observation data.
    @file graphing.py
    @author Quentin Bordelon
    <pre>
    Date: 12-04-2026

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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import gaussian_kde

import analysis

URBAN_THRESHOLD = 1500

def observationsByDensity(dataFrame, file='observationsByDensity', bins=150):
    plt.clf()
    data = dataFrame['populationDensity'].dropna()
    data = data[data >= 0]
 
    _, ax = plt.subplots(figsize=(10, 6))
 
    data = data[data > 0]
    ax.set_xscale('log')
    binEdge = np.logspace(np.log10(data.min()), np.log10(data.max()), bins+1)
    ax.hist(data, bins=binEdge, color='#666666', edgecolor='white', linewidth=0.5, alpha=0.85)
    ax.axvline(URBAN_THRESHOLD, color='black', linestyle='--', linewidth=1.5, label=f'Urban threshold ({URBAN_THRESHOLD})')
    ax.legend(fontsize=9)

    ax.set_xlabel('Population Density')
    ax.set_ylabel('Number of Observations')
    ax.set_title('Observation Counts by Population Density')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()
 
def observationsByInverseDensity(dataFrame, file='observationsByInverseDensity', bins=30):
    plt.clf()
    data = dataFrame['nearbyPopulation'].dropna()
    zeroes = (data < 1).sum()
    data = data[data >= 1]
    inverseDensity = 1.0 / data
 
    _, ax = plt.subplots(figsize=(10, 6))

    binEdge = np.logspace(np.log10(inverseDensity.min()), np.log10(inverseDensity.max()), bins + 1)
    ax.set_xscale('log')
    ax.hist(inverseDensity, bins=binEdge, color='#666666', edgecolor='white', linewidth=0.5, alpha=0.85)
    if zeroes > 0:
        ax.axhline(zeroes, color='black', linestyle=':', linewidth=1.5, label=f'Zero population (n={zeroes:,})')
    inverseThreshold = 1.0 / URBAN_THRESHOLD
    ax.axvline(inverseThreshold, color='black', linestyle='--', linewidth=1.5, label=f'Urban threshold (1/{URBAN_THRESHOLD})')
    ax.legend(fontsize=9)
 
    ax.set_xlabel('Inverse Population')
    ax.set_ylabel('Number of Observations')
    ax.set_title('Observation Counts by Inverse Population')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()

def speciesDensityScatter(dataFrame, significantSpecies=None, file='speciesDensityScatter'):
    grouped = dataFrame.groupby('taxonName').agg(
        obsCount=('taxonName', 'count'),
        meanDensity=('populationDensity', 'mean'),
        meanPop=('nearbyPopulation', 'mean')
    ).reset_index().dropna()
    grouped = grouped[(grouped['meanDensity'] > 0) & (grouped['meanPop'] > 0)]
    grouped['obsPerPop'] = grouped['obsCount'] / grouped['meanPop']
    grouped = grouped[grouped['obsPerPop'] > 0]
 
    sigTaxa = set(significantSpecies['taxonName']) if significantSpecies is not None and not significantSpecies.empty else set()
 
    _, ax = plt.subplots(figsize=(12, 7))
 
    base = grouped[~grouped['taxonName'].isin(sigTaxa)]
    ax.scatter(base['meanDensity'], base['obsPerPop'],
               color='#aaaaaa', alpha=0.8, s=14, linewidths=0,
               marker='o', label='All species')
 
    if sigTaxa:
        sig = grouped[grouped['taxonName'].isin(sigTaxa)]
        ax.scatter(sig['meanDensity'], sig['obsPerPop'],
            color='black', alpha=0.75, s=28, linewidths=0,
            marker='^', label=f'Chi-sq significant (n={len(sig)})')
 
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Mean Population Density (people/km2)')
    ax.set_ylabel('Observations per Capita')
    ax.set_title('Observations per Capita vs Mean Population Density per Species')
    ax.axvline(URBAN_THRESHOLD, color='black', linestyle='--', linewidth=1.2, label=f'Urban threshold ({URBAN_THRESHOLD})')
    ax.legend(fontsize=9, framealpha=0.9)
    ax.grid(axis='both', linestyle='--', alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()

def observationsByYear(dataFrame, significantSpecies=None, file='observationsByYear'):
    df = dataFrame.dropna(subset=['year'])
    df = df[df['year'] > 2014]
    years = sorted(df['year'].unique())
    yearTotals = df.groupby('year').size()
    allByYear = df.groupby('year').size().reindex(years, fill_value=0)
 
    _, ax = plt.subplots(figsize=(12, 6))
 
    ax.bar(years, allByYear, color='#888888', alpha=0.85, hatch='//', edgecolor='white', label='All species')
 
    if significantSpecies is not None and not significantSpecies.empty:
        sigTaxa = set(significantSpecies['taxonName'])
        dfSig = df[df['taxonName'].isin(sigTaxa)]
        sigByYear = dfSig.groupby('year').size().reindex(years, fill_value=0)
        ax2 = ax.twinx()
        ax2.plot(years, sigByYear / yearTotals,
            color='black', linewidth=2.0, marker='s', markersize=5,
            linestyle='--', label=f'Chi-sq significant (n={len(sigTaxa)} species)')
        ax2.set_ylabel('Significant species obs / total obs that year')
        ax2.legend(loc='upper left', fontsize=9)
 
    ax.set_xlabel('Year')
    ax.set_ylabel('Total observations')
    ax.set_title('Observations per Year')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close() 
 
def oddsRatioDistribution(dataFrame, significantSpecies, file='oddsRatioDistribution'):
    sigTaxa = set(significantSpecies['taxonName'])
    species = dataFrame['taxonName'].dropna().unique()
 
    def computeLogOddsRatio(taxon):
        isSpecies = dataFrame['taxonName'] == taxon
        a = int(( isSpecies &  dataFrame['isUrban']).sum())  
        b = int(( isSpecies & ~dataFrame['isUrban']).sum())  
        c = int((~isSpecies &  dataFrame['isUrban']).sum())  
        d = int((~isSpecies & ~dataFrame['isUrban']).sum())  

        # Haldane-Anscombe correction
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        return float(np.log((a * d) / (b * c)))
 
    rows = [(t, computeLogOddsRatio(t)) for t in species]
 
    lAll   = np.array([v for _, v in rows])
    lSig   = np.array([v for t, v in rows if t in sigTaxa])
    lOther = np.array([v for t, v in rows if t not in sigTaxa])
 
    xMin = np.percentile(lAll, 1)
    xMax = np.percentile(lAll, 99)
    xGrid = np.linspace(xMin, xMax, 500)
 
    _, ax = plt.subplots(figsize=(11, 6))
 
    styles = [
        (lAll,   'black', '-',  '////', f'All species (n={len(lAll)})'),
        (lOther, '#666666', '--', '\\\\\\\\', f'Non-significant (n={len(lOther)})'),
        (lSig,   '#111111', ':',  '....', f'Significant (n={len(lSig)})'),
    ]
    for vals, color, ls, _, label in styles:
        if len(vals) >= 2:
            kde = gaussian_kde(vals, bw_method=0.3)
            ax.plot(xGrid, kde(xGrid), linewidth=2.0, color=color, linestyle=ls, label=label)
            ax.fill_between(xGrid, kde(xGrid), alpha=0.10, color=color)
 
    ax.axvline(0, color='black', linestyle='-', linewidth=1.5, label='Neutral (OR=1)')
 
    ax.set_xlabel('Odds Ratio')
    ax.set_ylabel('Population Density')
    ax.set_title('Odds Ratio Distribution by Species Group')
    ax.legend(fontsize=9)
    ax.grid(axis='both', linestyle='--', alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()
 
def speciesDiversityByYear(dataFrame, file='speciesDiversityByYear'):
    df = dataFrame.dropna(subset=['year', 'taxonName', 'isUrban'])
    df = df[df['year'] > 0]
 
    urban    = df[df['isUrban']].groupby('year')['taxonName'].nunique()
    nonUrban = df[~df['isUrban']].groupby('year')['taxonName'].nunique()
    years = sorted(df['year'].unique())
 
    _, ax = plt.subplots(figsize=(12, 6))
 
    ax.plot(years, urban.reindex(years), color='black', linewidth=2.0, marker='^', markersize=5, linestyle='--', label='Urban')
    ax.plot(years, nonUrban.reindex(years), color='#555555', linewidth=2.0, marker='o', markersize=5, linestyle='-', label='Non-urban')
 
    ax.set_xlabel('Year')
    ax.set_ylabel('Unique Species Count')
    ax.set_title('Species Diversity per Year for Urban and Non-Urban')
    ax.legend(fontsize=9)
    ax.grid(axis='both', linestyle='--', alpha=0.4)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()

def main():
    os.makedirs('./Research/Graphs', exist_ok=True)

    dataFrame = pd.read_parquet("./Research/processedObservations.parquet")
    significant = analysis.chiSquaredPerSpecies(dataFrame)

    observationsByDensity(dataFrame)
    observationsByInverseDensity(dataFrame)
    observationsByYear(dataFrame, significant)
    oddsRatioDistribution(dataFrame, significant)
    speciesDiversityByYear(dataFrame)
    speciesDensityScatter(dataFrame, significant)
 
if __name__ == "__main__":
    dataFrame = pd.read_parquet("./Research/processedObservations.parquet")
    significant = analysis.chiSquaredPerSpecies(dataFrame)
