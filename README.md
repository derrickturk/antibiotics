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

Out of the box, it only knows about Python scalar types and `typing.Union`s
of them (including `typing.Optional`), but an extension mechanism for
arbitrary type-directed serialization and deserialization is provided
through the `type_serde_ext` argument to the `Delimited` constructor - see
`examples/advanced.py`.

For `Union` types, serialization is driven by the runtime type,
and deserialization is attempted in the order of declaration of the
`Union` arguments - except that `NoneType` is tried first if present,
to preserve the expected behavior when deserializing null/missing values
of types whose deserializers do not throw when receiving `''` as an argument.

A type `ExternalName` is also provided which may be used with `typing.Annotated`
to specify the name which should be used for a member when serializing or
deserializing (e.g. to match CSV headers).

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

### Example with custom external names
```python
from antibiotics import Delimited, ExternalName
from dataclasses import dataclass
from typing import Annotated, Optional

@dataclass
class SampleDC():
    w: Annotated[Optional[float], ExternalName('BigW')]
    x: Annotated[int, ExternalName('Fancy X')]
    y: bool
    z: str

if __name__ == '__main__':
    dcs = list()
    for i in range(10):
        even = i % 2 == 0
        dcs.append(SampleDC(
            i * 3.5 if even else None,
            i,
            not even,
            f'_",\t_{i}'
        ))

    csv = Delimited()
    with open('dcs.csv', 'w') as f:
        csv.write(SampleDC, dcs, f)

    with open('dcs.csv', 'r') as f:
        for dc in csv.read(SampleDC, f):
            print(dc)
```

### Documentation

Documentation strings and type annotations are provided for public types and
functions. We recommend viewing "nice" documentation pages using
[`pdoc`](https://pdoc.dev/docs/pdoc.html); e.g. in the same environment as the
`antibiotics` package is installed, install `pdoc` with `pip install pdoc`,
then run `pdoc antibiotics`.

---

Install with:

    pip install antibiotics

Or download directly [from PyPI](https://pypi.org/project/antibiotics/).

#### (c) 2023 dwt | terminus data science, LLC
#### available under the Apache License 2.0
