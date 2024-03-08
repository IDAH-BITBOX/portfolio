from jina import Deployment
from executor import StableLM

dep = Deployment(uses=StableLM, timeout_ready=-1, port=9097)

with dep:
    dep.block()