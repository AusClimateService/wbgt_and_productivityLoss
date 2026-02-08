# WBGT and Productivity Loss

Fit-for-purpose code collection for calculating Wet Bulb Globe Temperature (WBGT),
performing quality control and evaluation, and estimating labour productivity loss.
Developed to support the Australian Climate Service delivery to Treasury.

## Contents

## - compute_labour_productivity_loss.py

Computes gridded hourly labour productivity loss from hourly WBGT for three
physical intensity classes (low, medium, high).

Outputs are provided as **fractional loss (0..1)**, where:
- `0` indicates no productivity loss
- `1` indicates complete productivity loss

This code is **fit-for-purpose** and project-specific, intended to meet defined
analytical requirements for Treasury delivery. It is not designed to function as
a general-purpose or production-grade software library.

### - job-run_compute_labour_productivity_loss.pbs

Execute `compute_labour_productivity_loss.py` on NCI's megamem node.

### - evaluate_labour_productivity_loss_script1.ipynb

Evaluate productivity loss data generated using `compute_labour_productivity_loss.py` (NCI ARE: megamembw node).