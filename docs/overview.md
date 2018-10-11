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
* Max 900 MB model size.
* Max 500MB disk space. Ensure that your project with it's libraries is below this size. 
* Conda support is only for dependency files [crafted by hand](https://conda.io/docs/user-guide/tasks/manage-environments.html#create-env-file-manually)


## Alternatives
### Sagemaker
SageMaker has the following advantages(not exhaustive):
- If you have SLAs, then Sagemaker may be a good choice. As they are on demand instances, you won't have the cold start delays.
- GPU Inference available
- Can serve models bigger than 1 GB(upon filling a form)
- You can choose more powerful machines than what AWS Lambda can offer you.

Sagemaker has the following costs(correct me if I am wrong):
* If you have to deploy a model which is not supported by Sagemaker(e.g. `lightfm`), then you have to:
    * create your own docker image(manage your own OS updates e.g. security)
    * implement a web server which has to implement a few endpoints
    * manage auto scaling,
    * provide handlers to `SIGTERM` and `SIGKILL` events
    * manage some environment variables.

For more details, look [here](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html).
 
`thampi`(via AWS Lambda) abstracts all this away from you. Of course, one can build a library to do the above for Sagemaker for you. Let me know when you make that library!


### Algorithmia

[Algorithmia](https://algorithmia.com/) is a commercial alternative to Thampi. I'm not sure though how easy it is to deploy models on libraries not supported by Algorithmia(e.g. `lightfm`). Note: I haven't spend too much researching this.