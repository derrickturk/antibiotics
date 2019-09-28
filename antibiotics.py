#  Copyright 2019 terminus data science, LLC

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Any, Iterable, List, Optional, TextIO, Type, Union
from typing import Generic, TypeVar

import dataclasses as dc

_T = TypeVar('_T')

@dc.dataclass
class Delimited():
    sep: str = ','
    quote: Optional[str] = '"'
    escape: Optional[str] = '"'

    def write(self, cls: Type[_T], recs: Iterable[_T], stream: TextIO,
            header: bool = True) -> None:
        if header:
            self.write_header(cls, stream)
        for r in recs:
            self.write_record(r, stream)

    def write_header(self, cls: Type, stream: TextIO) -> None:
        stream.write(self._delimit(_field_names(cls)))
        stream.write('\n')

    def write_record(self, rec: _T, stream: TextIO) -> None:
        stream.write(self._delimit(self._render(rec)))
        stream.write('\n')

    def read_header(self, cls: Type, stream: TextIO) -> None:
        hdr = self._split(stream.readline().rstrip('\n'))
        if hdr != _field_names(cls):
            raise ValueError('Invalid header for provided type.')

    def read_record(self, cls: Type[_T], stream: TextIO) -> Optional[_T]:
        line = stream.readline()
        if line == '':
            return None
        return self._parse(cls, self._split(line.rstrip('\n')))

    def read(self, cls: Type[_T], stream: TextIO,
            header: bool = True) -> Iterable[_T]:
        if header:
            self.read_header(cls, stream)
        while True:
            rec = self.read_record(cls, stream)
            if rec is None:
                break
            yield rec

    def _delimit(self, elems: List[str]) -> str:
        quoted = list()
        for e in elems:
            if self.quote is not None and self.quote in e:
                if self.escape is not None:
                    e = e.replace(self.quote, self.escape + self.quote)
                else:
                    raise ValueError(
                        f'Quote {self.quote} appears in value "{e}" and no escape character is set.')

            if self.sep in e:
                if self.quote is not None:
                    quoted.append(f'{self.quote}{e}{self.quote}')
                else:
                    raise ValueError(
                        f'Separator {self.sep} appears in value "{e}" and no quote character is set.')
            else:
                quoted.append(e)

        return self.sep.join(quoted)

    def _render(self, rec: _T) -> List[str]:
        tys = _field_types(type(rec))
        vals = _field_vals(type(rec), rec)
        elems = list()
        for ty, v in zip(tys, vals):
            if _optional_type(ty) and v is None:
                elems.append('')
            else:
                elems.append(str(v))
        return elems

    def _split(self, line: str) -> List[str]:
        elems = list()
        this_elem = list()
        in_quote = False
        in_escape = False
        for c in line:
            if in_escape:
                this_elem.append(c)
                in_escape = False
                continue

            if in_quote:
                if c == self.escape:
                    in_escape = True
                    continue
                if c == self.quote:
                    in_quote = False
                    continue
                this_elem.append(c)
                continue

            if c == self.sep:
                elems.append(''.join(this_elem))
                this_elem = list()
            elif c == self.quote:
                in_quote = True
            else:
                this_elem.append(c)
        elems.append(''.join(this_elem))
        return elems

    def _parse(self, cls: Type[_T], elems: List[str]) -> _T:
        tys = _field_types(cls)
        if len(elems) != len(tys):
            print(elems)
            print(tys)
            raise ValueError(
                f'Record length {len(elems)} does not match required field count ({len(tys)}).')
        vals: List[Any] = list()
        for ty, e in zip(tys, elems):
            opt_ty = _optional_type(ty)
            if opt_ty:
                ty = opt_ty
                if e == '':
                    vals.append(None)
                    continue
            # argh, dumb special case
            if ty == bool:
                if e == 'False':
                    vals.append(False)
                elif e == 'True':
                    vals.append(True)
                else:
                    raise ValueError(f'Unrecognized boolean value "{e}".')
            else:
                vals.append(ty(e))
        return cls(*vals)

def _field_names(cls: Type) -> List[str]:
    try:
        return list(cls._fields)
    except:
        pass
    try:
        return [f.name for f in dc.fields(cls)]
    except:
        pass
    raise ValueError("This type is not a NamedTuple or @dataclass.")

def _field_types(cls: Type) -> List[Type]:
    try:
        return [ty for _, ty in cls._field_types.items()]
    except:
        pass
    try:
        return [f.type for f in dc.fields(cls)]
    except:
        pass
    raise ValueError("This type is not a NamedTuple or @dataclass.")

def _field_vals(cls: Type[_T], rec: _T) -> List[Any]:
    try:
        return list(rec)
    except:
        pass
    try:
        return list(dc.astuple(rec))
    except:
        pass
    raise ValueError("This type is not a NamedTuple or @dataclass.")

def _optional_type(ty: Type) -> Optional[Type]:
    # see: https://stackoverflow.com/questions/49171189/whats-the-correct-way-to-check-if-an-object-is-a-typing-generic
    try:
        if (ty.__origin__ == Union and type(None) in ty.__args__
                and len(ty.__args__) == 2):
            return [t for t in ty.__args__ if t != type(None)][0]
        else:
            return None
    except:
        return None
