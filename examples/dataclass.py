from antibiotics import Delimited

from sys import stdout, stderr
from dataclasses import dataclass
from typing import NamedTuple, Optional

@dataclass
class SampleRecord():
    w: Optional[float]
    x: int
    y: bool
    z: str

if __name__ == '__main__':
    recs = list()
    for i in range(10):
        even = i % 2 == 0
        recs.append(SampleRecord(
            i * 3.5 if even else None,
            i,
            not even, # as IF!
            f'_",\t_{i}'
        ))

    csv = Delimited()
    csv.write(SampleRecord, recs, stdout)

    tsv = Delimited(sep='\t', escape='\\')
    tsv.write(SampleRecord, recs, stderr)
