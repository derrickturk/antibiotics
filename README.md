# antibiotics
### NamedTuple / dataclasses <-> delimited text

> "The best treatment for acute episodes of PANDAS is to treat the strep
infection causing the symptoms, if it is still present, with antibiotics."  
-- [National Institute of Mental Health](https://www.nimh.nih.gov/health/publications/pandas/index.shtml)

`antibiotics` is a minimalist type-driven serialization/deserialization library
inspired by [Serde](https://serde.rs/) and
[cassava](http://hackage.haskell.org/package/cassava).

It uses type annotations to automatically read and write `NamedTuple` or
`@dataclass` objects to or from delimited text files.

As of right now, it only knows about Python scalar types constructible from
strings (and a hack for `bool`) as well as `typing.Optional`.

### Basic example
```python
from antibiotics import Delimited
from dataclasses import dataclass
from typing import NamedTuple, Optional

@dataclass
class SampleDC():
    w: Optional[float]
    x: int
    y: bool
    z: str

class SampleNT(NamedTuple):
    w: Optional[float]
    x: int
    y: bool
    z: str

if __name__ == '__main__':
    dcs = list()
    nts = list()
    for i in range(10):
        even = i % 2 == 0
        dcs.append(SampleDC(
            i * 3.5 if even else None,
            i,
            not even,
            f'_",\t_{i}'
        ))
        nts.append(SampleNT(
            i * 3.5 if even else None,
            i,
            not even,
            f'_",\t_{i}'
        ))

    csv = Delimited()
    with open('dcs.csv', 'w') as f:
        csv.write(SampleDC, dcs, f)

    tsv = Delimited(sep='\t', escape='\\')
    with open('nts.tsv', 'w') as f:
        tsv.write(SampleNT, dcs, f, header=False)

    with open('dcs.csv', 'r') as f:
        for r in csv.read(SampleDC, f):
            print(r)

    with open('nts.tsv', 'r') as f:
        for r in tsv.read(SampleNT, f, header=False):
            print(r)
```

###### a [dwt](https://github.com/derrickturk) / [terminus data science, LLC](https://www.terminusdatascience.com) joint
