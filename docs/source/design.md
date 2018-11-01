# Design
`thampi` being on AWS Lambda comes with constraints

## Model Size

If your model is too big and serving it takes a lot of time, consider
    
   * Pushing the model weights to a database. The author of [lightfm](https://github.com/lyst/lightfm) has had success in that direction.      