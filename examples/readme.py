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
        for dc in csv.read(SampleDC, f):
            print(dc)

    with open('nts.tsv', 'r') as f:
        for nt in tsv.read(SampleNT, f, header=False):
            print(nt)
