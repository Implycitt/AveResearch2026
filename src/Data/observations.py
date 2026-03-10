'''
    Gets observation data from the iNaturalist API for a specified project and saves it in JSONL format. 
    Also includes functionality to sync new observations since the last update and convert the collected data 
    into Parquet format for efficient storage and analysis.
    @file observations.py
    @author Quentin Bordelon
    <pre>
    Date: 10-03-2026

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

import compression
import requests, time, json, os, glob, math
import pandas as pd

def fetchProjectData(projectSlug: str, startId: str, endId: str, filename: str) -> None:
    baseUrl: str = "https://api.inaturalist.org/v1/observations"
    filepath: str = "Research/" + filename
    
    params = {
        "project_id": projectSlug,
        "per_page": 200,
        "order": "asc",
        "order_by": "id",
        "id_above": startId
    }

    with open(filepath, "w", encoding="utf-8") as file:
        currentId = startId
        count = 0
        
        while currentId < endId:
            try:
                response = requests.get(baseUrl, params=params)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])

                if not results:
                    break

                for observation in results:
                    currentId = observation['id']
                    if currentId > endId:
                        break
                    
                    flattened = {
                        "obs_id": observation.get("id"),
                        "timestamp": observation.get("time_observed_at"),
                        "observedDate": observation.get("observed_on"),
                        "taxonName": observation.get("taxon", {}).get("name") if observation.get("taxon") else None,
                        "commonName": observation.get("taxon", {}).get("preferred_common_name") if observation.get("taxon") else None,
                        "rank": observation.get("taxon", {}).get("rank") if observation.get("taxon") else None,
                        "latitude": observation.get("location", "").split(",")[0] if observation.get("location") else None,
                        "longitude": observation.get("location", "").split(",")[1] if observation.get("location") else None,
                        "userLogin": observation.get("user", {}).get("login"),
                        "quality": observation.get("quality_grade")
                    }
                    
                    file.write(json.dumps(flattened) + "\n")
                    count += 1

                params["id_above"] = currentId
                
                time.sleep(1.2) 

            except Exception as e:
                print(f"Error at ID {currentId}: {e}")
                break

def syncProject(projectSlug: str) -> None:
    baseUrl: str = "https://api.inaturalist.org/v1/observations"
    outputPath: str = "Research/observationsUpdates.jsonl"

    lastUpdate = getLatestUpdate()
    
    params = {
        "project_id": projectSlug,
        "per_page": 200,
        "order": "asc",
        "order_by": "updated_at",
    }

    if lastUpdate:
        params["updated_since"] = lastUpdate

    totalAdded: int = 0
    with open(outputPath, "a", encoding="utf-8") as file:
        page: int = 1
        while True:
            params["page"] = page
            try:
                response = requests.get(baseUrl, params=params)
                response.raise_for_status()
                results = response.json().get("results", [])

                if not results:
                    break

                for observation in results:
                    flattened = {
                        "obs_id": observation.get("id"),
                        "timestamp": observation.get("time_observed_at"),
                        "observedDate": observation.get("observed_on"),
                        "taxonName": observation.get("taxon", {}).get("name") if observation.get("taxon") else None,
                        "commonName": observation.get("taxon", {}).get("preferred_common_name") if observation.get("taxon") else None,
                        "rank": observation.get("taxon", {}).get("rank") if observation.get("taxon") else None,
                        "latitude": observation.get("location", "").split(",")[0] if observation.get("location") else None,
                        "longitude": observation.get("location", "").split(",")[1] if observation.get("location") else None,
                        "userLogin": observation.get("user", {}).get("login"),
                        "quality": observation.get("quality_grade")
                    }
                    file.write(json.dumps(flattened) + "\n")
                    totalAdded += 1

                if len(results) < 200: break
                page += 1
                time.sleep(1.2)
                
            except Exception as e:
                print(f"Sync interrupted: {e}")
                break

def getLatestUpdate(directory: str = "out") -> str:
    files = glob.glob(os.path.join(directory, "*.jsonl"))
    if not files:
        return None
    
    latestTime: str = None
    
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    obsTime = data.get("updated_at")
                    if not obsTime:
                        continue

                    if latestTime is None or obsTime > latestTime:
                        latestTime = obsTime
                except json.JSONDecodeError:
                    continue
                    
    return latestTime

def getIdBounds(projectSlug: str) -> tuple[str, str]:
    baseUrl: str = "https://api.inaturalist.org/v1/observations"

    paramsMin: dict[str, str] = {"project_id": projectSlug, "order": "asc", "order_by": "id", "per_page": 1}
    paramsMax: dict[str, str] = {"project_id": projectSlug, "order": "desc", "order_by": "id", "per_page": 1}

    resMin = requests.get(baseUrl, params=paramsMin).json()
    resMax = requests.get(baseUrl, params=paramsMax).json()

    minId: str = resMin['results'][0]['id']
    maxId: str = resMax['results'][0]['id']

    return minId, maxId

def optimizeConvertToParquet(inputDir="Research", outputFile="Research/observations.parquet") -> None:
    files = glob.glob(os.path.join(inputDir, "*.jsonl"))
    if not files:
        print("No files found in the output directory.")
        return

    df = pd.concat([pd.read_json(file, lines=True) for file in files])

    cat_columns = ['rank', 'quality', 'userLogin', 'taxonName', 'commonName']
    for col in cat_columns:
        if col in df.columns:
            df[col] = df[col].astype('category')
    df['latitude'] = pd.to_numeric(df['latitude'], downcast='float')
    df['longitude'] = pd.to_numeric(df['longitude'], downcast='float')
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

    df.to_parquet(outputFile, index=False, engine='pyarrow', compression='snappy')

def initData() -> None:
    project: str = "birds-in-urban-vs-non-urban-environments"
    minId, maxId = getIdBounds(project)

    totalRange: int = int(maxId) - int(minId)
    step: int = math.ceil(totalRange / 3)

    chunks = [
        (minId - 1, minId + step, "observations1.jsonl"),
        (minId + step, minId + (2 * step), "observations2.jsonl"),
        (minId + (2 * step), maxId, "observations3.jsonl")
    ]

    for start, end, name in chunks:
        fetchProjectData(project, start, end, name)

if __name__ == "__main__":
    #initData()
    #optimizeConvertToParquet()
    pass
