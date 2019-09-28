from antibiotics import Delimited

from sys import stdout, stderr
from typing import NamedTuple, Optional

from io import StringIO

class SampleRecord(NamedTuple):
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

    csv_str = '''w,x,y,z
0.0,0,False,"_"",\t_0"
,1,True,"_"",\t_1"
7.0,2,False,"_"",\t_2"
,3,True,"_"",\t_3"
14.0,4,False,"_"",\t_4"
,5,True,"_"",\t_5"
21.0,6,False,"_"",\t_6"
,7,True,"_"",\t_7"
28.0,8,False,"_"",\t_8"
,9,True,"_"",\t_9"
'''

    for r in csv.read(SampleRecord, StringIO(csv_str)):
        print(r)
