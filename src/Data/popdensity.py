'''
    fetches population density maps from worldpop, gets population density at given latitude and longitude
    @file popdensity.py
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

import requests, os, rasterio, pycountry, math, zipfile, io
import reverse_geocoder as rg
from rasterio.windows import Window
import numpy as np

countryCache: dict = {}

session = requests.Session()

US_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

def buildUrl(iso: str, year: int, stateCode: str) -> str:
    if year >= 2015:
        base = f"https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/{year}"
        if iso == "USA" and stateCode:
            return f"{base}/USA_States/{stateCode}/v1/100m/constrained/{stateCode.lower()}_pop_{year}_CN_100m_R2025A_v1.tif"
        else:
            return f"{base}/{iso.upper()}/v1/100m/constrained/{iso.lower()}_pop_{year}_CN_100m_R2025A_v1.tif"
    elif year >= 2000:
        targetYear = max(2000, year)
        base = "https://data.worldpop.org/GIS/Population/Global_2000_2020"
        return f"{base}/{targetYear}/{iso.upper()}/{iso.lower()}_ppp_{targetYear}.tif"
    else:
        if year < 1950 and year % 10 != 0:
            year = (year // 10) * 10
        return f"https://geo.public.data.uu.nl/vault-hyde/hyde35_c9_apr2025%5B1749214444%5D/original/gbc2025_7apr_upper/zip/{year}AD_pop.zip"

def buildPath(latitude: float, longitude: float, year: int) -> str:
    isoCode, _, stateCode, _ = getCountry(latitude, longitude)
    if stateCode and year > 2014:
        return f'./Research/Countries/{isoCode}/{stateCode}/{year}/'
    else:
        return f'./Research/Countries/{isoCode}/{year}/'

def downloadCountryMap(url: str, downloadPath: str, filePath: str) -> None:
    os.makedirs(downloadPath, exist_ok=True)  

    with session.get(url, stream=True, timeout=120) as request:
        if request.status_code != 200:
            raise Exception(f"failed to download {url}: HTTP {request.status_code}")
        request.raise_for_status()
        with open(filePath, 'wb') as file:
            for chunk in request.iter_content(10 * 1024 * 1024):
                file.write(chunk)

def downloadIfMissing(row):
    lat, lon, year = float(row['latitude']), float(row['longitude']), int(row['year'])
    isoCode, _, stateCode, _ = getCountry(lat, lon)
    url = buildUrl(isoCode, year, stateCode)
    storage_path = buildPath(lat, lon, year)
    filePath = os.path.join(storage_path, "populationDensity.tif")
    if not os.path.exists(filePath):
        try:
            downloadCountryMap(url, storage_path, filePath)
        except Exception as e:
            print(f"Failed download for {url}: {e}")

def extractFromZip(url, file, extractPath):
    os.makedirs(extractPath, exist_ok=True)
    with session.get(url, stream=True, timeout=120) as request:
        with zipfile.ZipFile(io.BytesIO(request.content)) as z:
            z.extract(file, extractPath)

def resolveCountryResult(result: dict, stateName: str):
    iso2 = result['cc']
    country = pycountry.countries.get(alpha_2=iso2)
    if country:
        iso3 = country.alpha_3
        countryName = country.name.replace(' ', '_')
    else:
        iso3 = "USA"
        countryName = "United_States_of_America"
    stateCode = US_STATES.get(stateName) if iso3 == "USA" else None
    return iso3, countryName, stateCode, stateName

def prewarmGeocodeCache(coords: list) -> None:
    uncached = [
        c for c in coords
        if c not in countryCache
        and math.isfinite(c[0]) and math.isfinite(c[1])
    ]
    if not uncached:
        return
    results = rg.search(uncached, mode=1)  # mode 1 single-process, mode 2 spawns workers bad
    for coord, result in zip(uncached, results):
        stateName = result['admin1']
        countryCache[coord] = resolveCountryResult(result, stateName)

def getCountry(latitude: float, longitude: float):
    key = (latitude, longitude)
    if key not in countryCache:
        results = rg.search([key], mode=1)
        stateName = results[0]['admin1']
        countryCache[key] = resolveCountryResult(results[0], stateName)
    return countryCache[key]

def clean(data, noData):
    MAX= 1000000
    if noData is not None:
        data = np.where(np.isclose(data, noData, rtol=1e-3, atol=1.0), 0.0, data)
    return np.where((data < 0) | (data > MAX), 0.0, data)


def windowMetrics(source, latitude: float, longitude: float):
    radius = 0.56418958  # inverse sqrt(pi) — gives circle of area 1 km2
    pixelWidth = source.res[0]
    pixelDistance = pixelWidth * getRadius()
    pixelRadius = int(math.ceil(radius / pixelDistance))

    rcenter, ccenter = source.index(longitude, latitude)
    searchWindow = Window(
        ccenter - pixelRadius,
        rcenter - pixelRadius,
        (pixelRadius * 2) + 1,
        (pixelRadius * 2) + 1
    )
    data = source.read(1, window=searchWindow, boundless=True, fill_value=0)
    data = clean(data, source.nodata)

    y, x = np.ogrid[-pixelRadius:pixelRadius + 1, -pixelRadius:pixelRadius + 1]
    mask = x * x + y * y <= pixelRadius ** 2

    if np.any(mask):
        totalPop = float(np.sum(data[mask]))
        maxDensity = float(np.max(data[mask])) / getArea(latitude, 3)
    else:
        totalPop, maxDensity = 0.0, 0.0

    return totalPop, maxDensity

def getAllMetricsBatch(filePath: str, coords: list) -> list:
    try:
        with rasterio.open(filePath) as source:
            noData = source.nodata
            xy = [(lon, lat) for lat, lon in coords]

            raw = np.array([float(v[0]) for v in source.sample(xy)], dtype=np.float64)
            raw = clean(raw.reshape(-1, 1), noData).flatten()

            results = []
            for i, (lat, lon) in enumerate(coords):
                ppp = raw[i]

                pixelAreaKm2 = getArea(lat, 3)
                populationDensity = ppp / pixelAreaKm2 if pixelAreaKm2 > 0 else 0.0

                totalPop, maxDensity = windowMetrics(source, lat, lon)
                results.append((totalPop, maxDensity, populationDensity))
            return results
    except Exception:
        return [(0.0, 0.0, 0.0)] * len(coords)

def getAllMetricsBatchASC(year: int, coords: list) -> list:
    path = f'./Research/Historic/{year}/'
    file = f"popc_{year}AD.asc"
    filePath = path + file
    url = buildUrl("", year, "")
    if not os.path.isfile(filePath):
        extractFromZip(url, file, path)
    try:
        with rasterio.open(filePath) as source:
            xy = [(lon, lat) for lat, lon in coords]
            samples = list(source.sample(xy))
            return [(0.0, 0.0, max(0.0, float(s[0]))) for s in samples]
    except Exception:
        return [(0.0, 0.0, 0.0)] * len(coords)

def getArea(latitude: float, arcSeconds: int) -> float:
    radiusEarth = 6371.0008
    deltaPhi = math.radians(arcSeconds / 3600)
    baseArea = radiusEarth ** 2 * deltaPhi ** 2
    area = baseArea * max(math.cos(math.radians(latitude)), 1e-10)
    return area

def getRadius():
    radiusEarth = 6371.0008
    EarthsCircumference = 2 * math.pi * radiusEarth
    return EarthsCircumference / 360
