from antibiotics import Delimited

from sys import stdout, stderr
from dataclasses import dataclass
from typing import Optional, Union

from io import StringIO

class FlubBlub():
    def __init__(self, flub: bool):
        self.flub = flub

    def __str__(self):
        if self.flub:
            return 'Flub'
        else:
            return 'Blub'

    @classmethod
    def from_string(cls, s: str):
        if s == 'Flub':
            return FlubBlub(True)
        if s == 'Blub':
            return FlubBlub(False)
        raise ValueError('neither Flub nor Blub!')

@dataclass
class TrickyRecord():
    w: Optional[float]
    x: Union[int, complex]
    y: bytes
    z: FlubBlub

if __name__ == '__main__':
    recs = list()
    for i in range(10):
        even = i % 2 == 0
        recs.append(TrickyRecord(
            i * 3.5 if even else None,
            i if not even else complex(i * 2.1, -i * 1.5),
            'Eyjafjallajökull'.encode('utf8'),
            FlubBlub(even)
        ))

    csv = Delimited(type_serde={
        FlubBlub: (str, FlubBlub.from_string),
    })
    csv.write(TrickyRecord, recs, stdout)

    with StringIO() as stream:
        csv.write(TrickyRecord, recs, stream)
        stream.seek(0)
        for r in csv.read(TrickyRecord, stream):
            print(r)
