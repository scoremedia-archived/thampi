---
id: installation
title: Installation
sidebar_label: Installation
---

## Installation
```python
pip install thampi
```
## Prerequisites
* [Setup AWS Credentials](https://docs.aws.amazon.com/sdk-for-java/v2/developer-guide/setup-credentials.html)
* Install Docker(e.g for [Mac](https://docs.docker.com/docker-for-mac/install/))
* Ensure that the user which calls thampi has *admin* access
* For now, only python 3.6 is supported

# Important
* Do not install `zappa` or `flask` for your environment for serving models. If you have to use `zappa` or `flask`, consider creating another environment(and it's corresponding `requirements.txt` file)
* Do not upgrade `zappa` or `flask` if asked to do so. The latest version of `zappa(0.46.1)` does not work for our use case so it's at `0.45.1`. As a `thampi` user, you should not be much affected by that.