from .alphahub import AlphaHub
from abc import ABC, abstractmethod
import numpy as np
from numbers import Number


NumberLike = Number | np.generic | int | float
class Runnable(ABC): 
  @abstractmethod
  def next(self, time:NumberLike): ...
  
  
__all__ = ['AlphaHub', 'Runnable']