# Tutorial

## Prerequisites
* First ensure you have gone through all the [installation steps](installation.md)
* Your python installation should be 3.6, since AWS Lambda supports 3.6 as of now

Let's create a new project `myproject`. We'll use `scikit-learn` as an example but you could use any framework.

## Dummy Project
### Setup(Pip)

```console
mkdir myproject && cd myproject
virtualenv -p python3 venv
source ./venv/bin/activate
pip install thampi
pip install scikit-learn
pip install numpy
pip install scipy
pip freeze > requirements.txt
```

### Setup(Conda)
Note: This is one way of creating a conda environment. Please use the conventional way if you are comfortable in that style.

```console
mkdir myproject && cd myproject
# Create a  conda environment inside the directory myproject
conda create --prefix=venv python=3.6.7
pip install thampi
pip install scikit-learn
pip install numpy
pip install scipy
```

**IMPORTANT**: `thampi` only supports conda requirements files [crafted by hand](https://conda.io/docs/user-guide/tasks/manage-environments.html#create-env-file-manually). So, let's manually create a requirements file with the above dependencies as shown below and save it as `requirements.txt`. The versions will change but you get the idea.

```
name: thampi-tutorial
dependencies:
  - thampi=0.1.0
  - numpy=1.15.*
  - scikit-learn=0.20.0
  - scipy=1.1.0 
```


### Initialization
* Run `thampi init` and you should see something similar to the terminal output below. 

    *  For the s3 bucket, you can choose to have one bucket for all your thampi applications. Each project(model) is at a different prefix so as long as the projects have unique names, they won't overwrite each other. If you aren't confident of that, you could just give a different bucket for each thampi project.
    * Choose `pip` or `conda` according to your preference.

```sh
thampi init
```
```console

Welcome to Thampi!
-------------
Enter Model Name. If your model name is 'mymodel', the predict endpoint will be myendpoint.com/mymodel/predict
What do you want to call your model: mymodel
-----------------

AWS Lambda and API Gateway are only available in certain regions. Let's check to make sure you have a profile set up in one that will work.
We found the following profiles: analytics, and default. Which would you like us to use? (default 'default'): default
------------

Your Zappa deployments will need to be uploaded to a private S3 bucket.
If you don't have a bucket yet, we'll create one for you too.
What do you want to call your bucket? (default 'thampi-2i1zp4ura'): thampi-store
-----------------
Enter package manager:['conda', 'pip'](default: pip):pip
A file zappa_settings.json has been created. If you made a mistake, delete it and run `thampi init` again

```

* It has created a file called `zappa_settings.json`. This file is used by the Zappa framework. You'll note that some defaults have been filled up which are suitable for machine learning projects. A notable setting is `keep_warm` which prevents AWS Lambda from evicting the instance due to lack of use, by pinging the lambda(e.g. every 4 minutes). This is useful in the case when you have very large models. However, you could take it out if you feel that your model is small enough. For more details on how you can customize `zappa_settings.json`, check out [zappa docs](https://github.com/Miserlou/Zappa#advanced-settings)

* Within `zappa_settings.json`, thampi adds a key `thampi`. All thampi specific settings will go here. Note: `zappa` has no idea of `thampi`. It's just a convenient place to store the `thampi` relevant configuration.

## Training
Inside `myproject`, copy the following code into the file `train.py`

```python
import numpy as np
from sklearn import datasets
from typing import Dict
import thampi
from sklearn.neighbors import KNeighborsClassifier
from thampi.core.model import Model


class ThampiWrapper(Model):
    def __init__(self, sklearn_model):
        self.sklearn_model = sklearn_model
        super().__init__()

    
    def predict(self, args: Dict, context) -> Dict:
        original_input = [args.get('input')]
        result = self.sklearn_model.predict(np.array(original_input))
        return dict(result=list(result)[0])

def train_model():
    iris = datasets.load_iris()
    iris_X = iris.data
    iris_y = iris.target
    np.random.seed(0)
    indices = np.random.permutation(len(iris_X))
    iris_X_train = iris_X[indices[:-10]]
    iris_y_train = iris_y[indices[:-10]]

    knn = KNeighborsClassifier()
    knn.fit(iris_X_train, iris_y_train)
    return ThampiWrapper(knn)


if __name__ == '__main__':
    model = train_model()
    thampi.save(model, 'iris-sklearn', './models')


```

* The above code first trains the `sklearn` model as `knn`. To make the `thampi` web framework send the request data to the model, we wrap `knn` in `ThampiWrapper`, a class which implements the `Model` interface. The data sent to the serving endpoint will be passed by `thampi` to the `predict` method as `args`. Likewise, one can wrap models of other libraries as well. Ignore the `context` argument in the `predict` method for now. The `context` object sends in the `Flask` application object(and others in the future) which is probably not required for most of the use cases for now.
 


And then at the terminal run
```sh
python train.py
```

This will create the model. In thampi, like `mlflow`, the model artifacts are stored in a directory(i.e. `iris-sklearn`). Storing it in the `models` directory is just arbitrary convention.


## Serving the model

```sh
thampi serve staging --model_dir=./models/iris-sklearn --dependency_file=./requirements.txt
```
The `serve` command will use `zappa` to create or update a server endpoint. To see the endpoint,
do
```sh
thampi info staging
```

You'll see something similar to:
```sh
{'url': 'https://8i7a6qtlri.execute-api.us-east-1.amazonaws.com/staging/mymodel/predict'}
```
Let's hit the endpoint in the next section.

## Predict
You can do a curl like below where you replace `a_url` with the `url` that you receive from `thampi info staging` 
```sh
curl -d '{"data": {"input": [5.9, 3.2, 4.8, 1.8]}}' -H "Content-Type: application/json" -X POST a_url
```

Output:
```console
{
  "properties": {
    "instance_id": "9dbc56dd-936d-4dff-953c-8c22267ebe84",
    "served_time_utc": "2018-09-06T22:03:09.247038",
    "thampi_data_version": "0.1",
    "trained_time_utc": "2018-09-06T22:03:04.886644"
  },
  "result": {
    "result": 2
  }
}

```

For convenience, you can also do:
```sh
thampi predict staging --data='{"input": [5.9, 3.2, 4.8, 1.8]}'
```
where `data` is of `json` format.

The `properties` dictionary is meta-data associated with the model. Most of them are populated using the `save` command. If you want to add custom data (e.g `name` for your model and `version`, you can add it within `tags`)

## Undeploy
After you are done with your project, this will bring down the server endpoint permanently. Note, we are using a `zappa` command. Zappa offers other relevant commands as well. Refer to the zappa docs. 

```sh
zappa undeploy staging
```