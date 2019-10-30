# Minimal command line interface for manual perturbation of Quoref(-like) datapoints
This repository contains a simple script written in Python3 that takes a [Quoref](https://allennlp.org/quoref) data file with answers in the official json format, and provides an interactive tool to enter new question-answer pairs that are expected to be perturbations of the questions in the dataset.

## Usage
```python interface.py /path/to/data.json```
The output will be written in a new file in the current directory, and will contain a union of the instances in the original file, and the new QA pairs added in the current session. So you can provide as input the output from a previous session if you want to work in multiple sessions. The output file names will have timestamps appended to them.

## Interface
The interface shows a random paragraph from the dataset and iterate over each QA pair that the dataset has for that paragraph. For each QA pair, you have the option of entering a new perturbed question, and enter the corresponding answer.
