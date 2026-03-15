'''
    Gets observation data from the iNaturalist API for a specified project and saves it in JSONL format. 
    Also includes functionality to sync new observations since the last update and convert the collected data 
    into Parquet format for efficient storage and analysis.
    @file observations.py
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

import requests, time, json, os, glob
import pandas as pd

def fetchProjectData(projectSlug: str, outputDir: str = "./Research") -> None:
    os.makedirs(outputDir, exist_ok=True)
    baseUrl = "https://api.inaturalist.org/v1/observations"
    
    lastId = 0
    totalDownloaded = 0
    fileIndex = 1
    recordsPerFile = 250000 
    
    currentFilePath = os.path.join(outputDir, f"observations{fileIndex}.jsonl")
    currentFile = open(currentFilePath, "w", encoding="utf-8")
    
    while True:
        params = {
            "project_id": projectSlug,
            "order_by": "id",
            "order": "asc",
            "per_page": 200,
            "id_above": lastId
        }
        
        try:
            response = requests.get(baseUrl, params=params, timeout=15)
            
            if response.status_code != 200:
                time.sleep(10)
                continue
                
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
                
            for observation in results:
                totalDownloaded += 1
                
                if observation["id"] > lastId:
                    lastId = observation["id"]

                flattened = {
                    "id": observation.get("id"),
                    "observedDate": observation.get("observed_on"),
                    "taxonName": observation.get("taxon", {}).get("name") if observation.get("taxon") else None,
                    "rank": observation.get("taxon", {}).get("rank") if observation.get("taxon") else None,
                    "latitude": observation.get("location", "").split(",")[0] if observation.get("location") else None,
                    "longitude": observation.get("location", "").split(",")[1] if observation.get("location") else None,
                    "quality": observation.get("quality_grade")
                }

                currentFile.write(json.dumps(flattened) + "\n")
                    
                if totalDownloaded % recordsPerFile == 0:
                    currentFile.close()
                    fileIndex += 1
                    currentFilePath = os.path.join(outputDir, f"observations{fileIndex}.jsonl")
                    currentFile = open(currentFilePath, "w", encoding="utf-8")
            
            time.sleep(1.2) 
            
        except:
            time.sleep(10)
            
    currentFile.close()

def syncProjectData(projectSlug: str, outputDir: str = "./Research") -> None:
    os.makedirs(outputDir, exist_ok=True)
    
    lastId = 0
    fileIndex = 1
    
    existingFiles = glob.glob(os.path.join(outputDir, "observations*.jsonl"))
    
    if existingFiles:
        indices = [int(f.split('observations')[-1].split('.jsonl')[0]) for f in existingFiles]
        fileIndex = max(indices)
        
        lastFile = os.path.join(outputDir, f"observations{fileIndex}.jsonl")
        recordCount = 0

        if os.path.exists(lastFile) and os.path.getsize(lastFile) > 0:
            with open(lastFile, 'r', encoding='utf-8') as f:
                for line in f:
                    recordCount += 1
                    stripped = line.strip()
                    if stripped:
                        lastValidLine = stripped
            if lastValidLine:
                try:
                    obs = json.loads(lastValidLine)
                    lastId = obs['id']
                except:
                    return
        
        if recordCount >= 250000:
            fileIndex += 1
            mode = 'w'
        else:
            mode = 'a'
    else:
        mode = 'w'

    baseUrl = "https://api.inaturalist.org/v1/observations"
    totalInCurrentFile = 0 if mode == 'w' else recordCount
    
    currentFilePath = os.path.join(outputDir, f"observations{fileIndex}.jsonl")
    currentFile = open(currentFilePath, mode, encoding="utf-8")
    
    while True:
        params = {
            "project_id": projectSlug,
            "order_by": "id",
            "order": "asc",
            "per_page": 200,
            "id_above": lastId
        }
        
        try:
            response = requests.get(baseUrl, params=params, timeout=15)
            if response.status_code != 200:
                time.sleep(10)
                continue
                
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
                
            for observation in results:
                if observation["id"] > lastId:
                    lastId = observation["id"]

                flattened = {
                    "id": observation.get("id"),
                    "observedDate": observation.get("observed_on"),
                    "taxonName": observation.get("taxon", {}).get("name") if observation.get("taxon") else None,
                    "rank": observation.get("taxon", {}).get("rank") if observation.get("taxon") else None,
                    "latitude": observation.get("location", "").split(",")[0] if observation.get("location") else None,
                    "longitude": observation.get("location", "").split(",")[1] if observation.get("location") else None,
                    "quality": observation.get("quality_grade")
                }

                currentFile.write(json.dumps(flattened) + "\n")
                totalInCurrentFile += 1
                    
                if totalInCurrentFile >= 250000:
                    currentFile.close()
                    fileIndex += 1
                    totalInCurrentFile = 0
                    currentFilePath = os.path.join(outputDir, f"observations{fileIndex}.jsonl")
                    currentFile = open(currentFilePath, "w", encoding="utf-8")
            
            time.sleep(1.2) 
            
        except Exception as e:
            print(f"Error encountered: {e}")
            time.sleep(10)
            
    currentFile.close()

def optimizeConvertToParquet(inputDir="Research", outputFile="Research/observations.parquet") -> None:
    files = glob.glob(os.path.join(inputDir, "*.jsonl"))

    if not files:
        return

    df = pd.concat([pd.read_json(file, lines=True) for file in files], ignore_index=True)
    df['observedDate'] = pd.to_datetime(df['observedDate'], errors='coerce')

    df = df.drop_duplicates(subset=['id'], keep='last')

    catColumns = ['rank', 'quality', 'taxonName']
    for col in catColumns:
        if col in df.columns:
            df[col] = df[col].astype('category')
    df['latitude'] = pd.to_numeric(df['latitude'], downcast='float')
    df['longitude'] = pd.to_numeric(df['longitude'], downcast='float')
    df['year'] = df['observedDate'].dt.year.fillna(0).astype(int)

    df.to_parquet(outputFile, index=False, engine='pyarrow', compression='snappy')

def main():
    slug = "birds-in-urban-vs-non-urban-environments"

    syncProjectData(slug)
    optimizeConvertToParquet()

    df = pd.read_parquet("./Research/observations.parquet")
    print("number of observations: ", len(df))

if __name__ == "__main__":
    slug = "birds-in-urban-vs-non-urban-environments"
    optimizeConvertToParquet()

    df = pd.read_parquet("./Research/observations.parquet")
    print("number of observations: ", len(df))
