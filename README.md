# ml4trade

This repository provides an implementation of a [gym](https://github.com/Farama-Foundation/Gymnasium) environment where a prosumer (entity which can both produce and consume energy) can interact with energy day-ahead market.
You might want to check out [ml4trade-rl](https://github.com/skalermo/ml4trade-rl) repository, which uses reinforcement learning to solve this environment.

An agent represents the prosumer and must schedule the next day market transactions through its actions. 

The environment generates states by utilising historical data of weather conditions and market prices. Bridge between the data and the environment is enabled by *DataStrategies*.

### DataStrategy

DataStrategies follow [Strategy pattern](https://refactoring.guru/design-patterns/strategy) and provide functionality for processing raw historical data.

During construction a DataStrategy expects argument for data in form of Pandas DataFrame. Also a DataStrategy must implement following functions:

```python
def process(idx: int) -> float: ...

def observation(idx: int) -> list[float]: ...
```

The `process()` function is internally used by the environment for action processing and state generation, while the `observation()` returns values seen by the agent. 
The passed argument `idx` determines what part of historical data should be used. For example, by `idx` we could select a row in historical data.

DataStrategies allow for data customization. We provide default implementations in [`data_strategies`](ml4trade/data_strategies) directory. 

## Setup

To install run:

```
pip install git+https://github.com/skalermo/ml4trade.git
```
If you want to use the default data you will have to download it via `data/download_all.sh` script.

## Testing

You can run the tests by:
```
python -m unittest discover test
```
