'''
    Provides functions to create various graphs and visualizations based on the observation data.
    @file graphing.py
    @author Quentin Bordelon
    <pre>
    Date: 13-03-2026

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
import seaborn as sns
import numpy as np
import os

URBAN_THRESHOLD = 1500

def observationsByDensity(dataFrame, file='observationsByDensity', bins=30):
    plt.clf()
    data = dataFrame['populationDensity'].dropna()
    data = data[data >= 0]
 
    _, ax = plt.subplots(figsize=(10, 6))
 
    ax.hist(data, bins=bins, color='steelblue', edgecolor='white', linewidth=0.5, alpha=0.85)
 
    ax.axvline(URBAN_THRESHOLD, color='crimson', linestyle='--', linewidth=1.2, label=f'Urban threshold ({URBAN_THRESHOLD})')
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
    data = dataFrame['populationDensity'].dropna()
    data = data[data >= 0]
    data = data.clip(lower=1)  
    inverseDensity = 1.0 / data
 
    _, ax = plt.subplots(figsize=(10, 6))
 
    ax.hist(inverseDensity, bins=bins, color='steelblue', edgecolor='white', linewidth=0.5, alpha=0.85)
 
    inverseThreshold = 1.0 / URBAN_THRESHOLD
    ax.axvline(inverseThreshold, color='crimson', linestyle='--', linewidth=1.2, label=f'Urban threshold (1/{URBAN_THRESHOLD} = {inverseThreshold:.6f})')
    ax.legend(fontsize=9)
 
    ax.set_xlabel('Inverse Population Density')
    ax.set_ylabel('Number of Observations')
    ax.set_title('Observation Counts by Inverse Population Density')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
 
    plt.tight_layout()
    plt.savefig(f'./Research/Graphs/{file}.png', dpi=150)
    plt.close()

def main():
    os.makedirs('./Research/Graphs', exist_ok=True)
 