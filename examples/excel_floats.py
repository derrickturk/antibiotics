from antibiotics import Delimited

from sys import stdout
from typing import NamedTuple

from io import StringIO

class ExcelFloat(NamedTuple):
    value: float

    def to_string(self) -> str:
        s = str(self.value)
        whole, frac = s.split('.')
        if len(whole) > 3:
            new_whole = ''
            sep = ''
            while whole:
                new_whole = sep + new_whole
                new_whole = whole[-3:] + new_whole
                whole = whole[:-3]
                sep = ','
            return f'{new_whole}.{frac}'
        return s

    @classmethod
    def from_string(cls, s: str) -> 'ExcelFloat':
        return cls(float(s.replace(',', '')))

class ExcelRecord(NamedTuple):
    Time: int
    Rate: ExcelFloat

if __name__ == '__main__':
    csv = Delimited(type_serde_ext = {
        ExcelFloat: (ExcelFloat.to_string, ExcelFloat.from_string)
    })

    csv_str = '''Time,Rate
1,"2,000.00"
2,"1,800.00"
3,"1,600.00"
4,"1,400.00"
5,"1,200.00"
6,"1,000.00"
7,800.00
8,600.00
9,400.00
10,200.00
'''

    recs = list(csv.read(ExcelRecord, StringIO(csv_str)))
    for r in recs:
        print(r)
    print('\n')
    csv.write(ExcelRecord, recs, stdout)
