# Data

---

This file will change and be fixed later. I would rather not focus on writing readmes for now

Please ensure that you have followed the prerequisites described in the [src directory readme](https://github.com/Implycitt/AveResearch2026/blob/main/src/README.md) to be able to run this part of the code.

## Files

---

### analysis.py

---

I'm going to cross reference the files so it might get a little confusing. TL;DR: settling on 1.500 people within a 1 $km^2$ area because of [OECD](https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html). See more in the popdensity.

We are going to first run a chi squared test for independence for each taxon and if it is considered urban or not. This will allow us to see which taxon are not independent of urbanization. This will then allow us to narrow in on taxa to run the correlation coefficient and regression test and see how those compare to the entire sample space of observations.

### graphing.py

---

TODO

### observations.py

---

TODO

### popdensity.py

---

Im going to detail the math before I forget, this will be tidied in the future

In the getArea function you may see some funky math with some trig. The reason for this is because the earth is a sphere and the fact that our population density data can only be 2 dimensional. Longitudinal lines are parallel and are equidistant no matter where you are on the earth. The same is not true for the latitude. As you get further up or down the equator, the area created by two longitudinal and latitudinal lines shrinks and is actually modeled by a cosine function. In other words, the area of the pixel that we are using to grab the data needs to be modified so that we get a consistent population density no matter where we are on earth. To be able to do this we need two things: a base area and the cosine of our latitude.

$Area = R^2 \cdot cos(lat) \cdot \Delta\phi \cdot\ \Delta\lambda$

where, $R$ is the radius of the earth\
$lat$ is our latitude at the given point\
$\Delta\phi$ is the height of the pixel\
$\Delta\lambda$ is the width of the pixel

since the data is taken at 3 arc second pixels, we'll have to convert that to radians

$\Delta\phi, \space \Delta\lambda = \frac{3}{3600} \cdot \frac{\pi}{180}$

this translated into code is
```python
deltaPhi, deltaLambda = math.radians(3/3600)
```

then since the Radius of the earth is a known physical quantity ($R = 6371.0008$), we can square both quantities and multiply together:

```
baseArea = R**2 * deltaPhi * deltaLambda
```

this will give us the base area in kilometers squared for a pixel.

Finally, we multiply the base area by the cosine of the latitude to get the area in kilometers squared of the pixel at that latitude.

$Area = baseArea \cdot cos(latitude)$

```
pixelAreaKm2 = baseArea * math.cos(math.radians(latitude))
```

Then of course our quantity given from that pixel can be divided by our new area to get our population density at a given point.

To aid in the analysis there are two functions: getPopulation() and getMaxDensityInArea(). These two are here to normalize the score that we will be plotting and truly determine whether or not an observation is urban or not, respectively. To accomplish both, I get use the latitude and longitude of the point as a center and create a circle of radius 1km to either find the max density within it or sum up all the point within the circle to get a localized population. Since the [OECD](https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html) defines an urban area as 1.500 people/sqkm, we can find the total number of people inside this "circle" to check against; if the number of people within the circle is greater than the threshold then we can safely say the area is urban and so our observation was done in an urban area.