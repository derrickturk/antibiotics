from antibiotics import Delimited
from typing import NamedTuple, Optional

if __name__ == '__main__':
    bad = list()
    for i in range(10):
        bad.append(i)

    csv = Delimited()
    with open('dcs.csv', 'w', newline='') as f:
        csv.write(int, bad, f)
