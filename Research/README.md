# Research

---

The Research is structured as pictured below:

```structure
.
├──countries/
├──Documents/
│   ├──images/
│   ├──references.bib
│   ├──main.txt
│   ├──main.pdf
│   └──main.tex
├──Graphs/
├──Historic/*
├──observations#.jsonl
├──observations.parquet
└──processedObservations.parquet
```

Most of these are fairly unimportant but are necessary for the code to be able to access data. The historic and countries folder will not be present if freshly cloning the project but those directories are where the code downloads the country population density data for the analysis. The historic folder is also mostly unimportant as only data from 2015 onwards is used for the analysis. If running the analysis for ALL observations, ensure a decent amount of disk space as well as an afternoon free for the downloads to complete.