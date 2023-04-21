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
    with open('dcs.csv', 'w', newline='') as f:
        csv.write(SampleDC, dcs, f)

    with open('dcs.csv', 'r', newline='') as f:
        for dc in csv.read(SampleDC, f):
            print(dc)
