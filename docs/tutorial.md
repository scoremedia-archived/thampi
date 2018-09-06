---
id: tutorial
title: Tutorial
sidebar_label: Tutorial
---

# Prerequisites
* First ensure you have gone through all the [prerequisites](installation.md#prerequisites)
* Your python installation should be 3.6, since AWS Lambda supports 3.6 as of now

Let's create a new project `myproject`. We'll use `scikit-learn` as an example but you could use any framework.

## Dummy Project
### Setup(Pip)

```bash
mkdir myproject && cd myproject
virtualenv -p python3 venv
source ./venv/bin/activate
pip install thampi
pip install scikit-learn
pip install numpy
pip install scipy
pip freeze > requirements.txt
```


### Initialization
* Run `thampi init` and you should see something similar to the terminal output below. 

    *  For the s3 bucket, you can choose to have one bucket for all your thampi applications. Each project(model) is at a different prefix so as long as the projects have unique names, they won't overwrite each other. If you aren't confident of that, you could just give a different bucket for each thampi project.
    * Choose `pip` or `conda` according to your preference.
```bash
thampi init
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

* It has created a file called `zappa_settings.json`. This file is used to by the Zappa framework. You'll note that some defaults have been filled up which are suitable for machine learning projects. For more details on how you can customize `zappa_settings.json`, check out [zappa docs](https://github.com/Miserlou/Zappa#advanced-settings)

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

    def initialize(self, context) -> None:
        self.sklearn_model.initialize()
        pass

    def predict(self, args: Dict, context) -> Dict:
        original_input = [args.get('input')]

        return self.sklearn_model.predict(np.array(original_input))


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

* The above code first trains the `sklearn` model as `knn`. To make the `thampi` web framework send the request data to the model, we wrap `knn` in `ThampiWrapper`, a class which implements the `Model` interface. The data sent to the serving endpoint will be passed by `thampi` to the `predict` method as `args`. Likewise, one can wrap models of other libraries as well.


And then at the terminal run
```bash
python train.py
```

In thampi, like `mlflow`, the model artifacts are stored in a directory(i.e. `iris-sklearn`). Storing it in `models` is just arbitrary convention.


## Serving the model

```bash
thampi serve staging --model_dir=./models/iris-sklearn --dependency_file=./requirements.txt
```
The `serve` command will use `zappa` to create or update a server endpoint

## Predict

```bash
```