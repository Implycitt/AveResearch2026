# Aves and the Effects of Urbanization
Authors: Quentin Bordelon, Conny Horton III, Sophia Iacono, Julia Zimmermann

---

## Table of Contents

---

<ol>
  <li><a href="#About">About</a></li>
  <li>
    <a href="#How to Navigate This Repo">How to Navigate This Repo</a>
    <ul>
      <li><a href="#Research">Research</a></li>
      <li><a href="#Code">Code</a></li>
      <li><a href="#Data">Data</a></li>
    </ul>
  </li>
  <li><a href="#How to Contribute">How to Contribute</a></li>
  <li><a href="#Contact">Contact</a></li>
  <li><a href="#Acknowledgements">Acknowledgements</a></li>
  <li><a href="#License">License</a></li>
</ol>

## About

---

Hello! We are an undergraduate group at Louisiana State University conducting research on aves. Our research is focused on the effects of urbanization on bird count, frequency, and diversity. To conduct our study we are using data collected by citizen scientists on the [iNaturalist](https://inaturalist.org) platform. More information on our question, hypothesis, methodology and results can be found in the research via our slides or paper in the corresponding folder. Please consider helping out the research by reading the "How to Contribute" section.

## How to Navigate This Repo

---

The project is structured as pictured below:

```structure
.
├──in/
├──Research/
│   ├──Papers/
├──slides/
├──src
│   ├──Acquisition/
│   └──Data/
└──requirements.txt
```

There are various markdown files in some of the folders for further documentation.
Each main folder contains a certain part of the research which is described in the following way:

* in -> input files used in the code
* [research](https://github.com/Implycitt/AveResearch2026/blob/main/Research/README.md) -> research paper in various formats, graphs, worldpop maps
* slides -> notes and slides for presentation
* [src](https://github.com/Implycitt/AveResearch2026/blob/main/src/README.md) -> all code used described in the Code section

### Research

---

The papers will be uploaded inside the Research folder under the Papers folder: ```./Research/Papers/```

They will be available in LaTeX, pdf, and plaintext.

The data used in this research was graciously granted by the citizen science community at [iNaturalist](https://inaturalist.org). All data used in the research is available for viewing and to download in the Research folder but is still subject to the Data User Agreement as detailed by [GBIF](https://www.gbif.org/terms/data-user) and the [iNaturalist](https://inaturalist.org) platform. These observations are not owned by the members of this project and should be [properly cited](https://help.inaturalist.org/en/support/solutions/articles/151000170344-how-should-i-cite-inaturalist-) when relevant.

The data is chunked into sections for disk space reasons as well as api limits. The data is also available in json and in a parquet format.

Additionally, all population density data used for the analysis comes from [WorldPop](https://data.worldpop.org/GIS/Population/). The files used for the analysis will not be pushed to this repository so that cloning it does not take a couple hours. More information on the files will be detailed in the data folder readme.

### Code

---

The code used in this project and research is broken up based on the problem that was attempted to be solved:

* [Acquisition phase](https://github.com/Implycitt/AveResearch2026/blob/main/src/README.md)
* [Data Collection and Analysis phase](https://github.com/Implycitt/AveResearch2026/blob/main/src/Data/README.md)

The code sections and their respective markdown files document the goal of each file/function and how they work.\
All code was authored entirely by Quentin Bordelon and any further inquiries should be forwarded to the email listed in the <a href="#Contact"> contact </a> section.\
If there are any errors or issues in the code or any documentation please refer to the <a href="#How to Contribute"> how to contribute </a> section for how to submit pull requests to this repository.\
Anyone is free to use and distribute this code freely as part of the MIT license which you can refer to in the <a href="#License"> license </a> section. All code will, additionally, contain a header with the license.

## How to Contribute

---

If you wish to contribute to our research you may do so by:

* Joining the [project group on iNaturalist](https://www.inaturalist.org/projects/birds-in-urban-vs-non-urban-environments) and submitting observations\
or
* Submitting a pull request for any errors, issues, or mistakes you see in the code or documentation or open an issue with the corresponding tag via github

To submit a pull request:

1. Fork The project
2. Create your change within your fork
3. Commit your changes using appropriate [commit convention](https://www.conventionalcommits.org/en/v1.0.0/): ```git commit -m "docs: fixed spelling in FILENAME"```
4. Create your pull request and include an explanation for the changes you are submitting.

Similarly, you may [open an issue](https://github.com/Implycitt/AveResearch2026/issues) which will be reviewed as soon as possible.

## Contact

---

For any questions, concerns, or inquiries regarding the project or the research, please contact my email - qborde1@lsu.edu\
You can also reach me through my [iNaturalist account](https://www.inaturalist.org/people/10074635)

## Ackowledgements

---

Thank you to all of those who have contributed to this project either through iNaturalist observations or through submitted pull requests. This project would not be possible without the citizen science community and their efforts to document our natural environment.

## License

---

Distributed under the MIT License. See [`LICENSE`](./LICENSE) for more information.
