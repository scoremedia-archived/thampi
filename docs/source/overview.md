# Overview
## Introduction
Thampi creates a serverless machine learning prediction system using [Zappa](https://github.com/Miserlou/Zappa). 

## Benefits
* **No Devops**. With a single command, create a web server that scales, is fault tolerant and zero maintenance(courtesy [AWS Lambda](https://aws.amazon.com/lambda/)).
* **Focus on your model**. Work in Python to train your model. Thampi provides all support for serving the model.

* __Work on any platform*__. Work on Mac(technically possible on other platforms but untested) and still deploy to AWS Lambda(which is Linux).

    Thampi does this by using Docker underneath so that you can work on a Mac(or Windows?). When serving the model, it recreates your machine learning project in the docker image(which is Linux) and compiles all the C libraries(e.g. numpy) for you to Linux binaries, which is then uploaded to AWS Lambda.


* Pip and Conda support(See Limitations below).

## Limitations
* Conda support is only for dependency files [crafted by hand](https://conda.io/docs/user-guide/tasks/manage-environments.html#create-env-file-manually)
* Max 500MB disk space. Ensure that your project with it's libraries is below this size. 
* **Max 900 MB model size**. This number was derived from a few live tests. We circumvent the 500 MB disk space limit by loading the model directly from S3 to memory. `thampi` tries to reduce repeated calls to S3 by using `zappa's` feature of pinging the lambda instance every 4 mins or so(configurable). In that way, the model will stay on the lambda instance(unless it's a first time load or if AWS Lambda does decide to evict the instance for other reasons) 

    Based on feedback, an option could be added to package the model with the code but you'll then have to have a very small model size. It depends on what framework you use but generally you may have 100-250 MB space for your model as machine learning libraries take up a lot of space. Also look at the section `Design`
    




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

[Algorithmia](https://algorithmia.com/) is a commercial alternative to Thampi. I'm not sure though how easy it is to deploy models on libraries not supported by Algorithmia(e.g. `lightfm`). Note: I haven't spend too much researching Algorithmia.
