---
id: overview
title: Overview
sidebar_label: Overview
---

## Introduction
Thampi creates a serverless machine learning prediction system using [Zappa](https://github.com/Miserlou/Zappa) 

## Benefits
* All the benefits of [AWS Lambda](https://aws.amazon.com/lambda/).
* Work on Mac(and Windows?) and still deploy to AWS Lambda(which is Linux).
* Pip and limited Conda support(See Limitations).

## Limitations
* Max 1 GB model size.
* Max 500MB disk space. Ensure that your project with it's libraries is below this size. 
* Conda support is only for dependency files [crafted by hand](https://conda.io/docs/user-guide/tasks/manage-environments.html#create-env-file-manually)