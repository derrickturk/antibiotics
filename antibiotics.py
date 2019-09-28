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

from dataclasses import dataclass

_T = TypeVar('_T')
_U = TypeVar('_U')

@dataclass
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
            if _is_optional(ty) and v is None:
                elems.append('')
            else:
                elems.append(str(v))
        return elems

def _field_names(cls: Type) -> List[str]:
    # TODO: dataclass case
    try:
        return cls._fields
    except:
        raise ValueError("This type is not a NamedTuple or @dataclass.")

def _field_types(cls: Type) -> List[Type]:
    # TODO: dataclass case
    try:
        return [ty for _, ty in cls._field_types.items()]
    except:
        raise ValueError("This type is not a NamedTuple or @dataclass.")

def _field_vals(cls: Type[_U], rec: _U) -> List[Any]:
    # TODO: dataclass case
    try:
        return list(rec)
    except:
        raise ValueError("This type is not a NamedTuple or @dataclass.")

def _is_optional(ty: Type) -> bool:
    # see: https://stackoverflow.com/questions/49171189/whats-the-correct-way-to-check-if-an-object-is-a-typing-generic
    try:
        return ty.__origin__ == Union and type(None) in ty.__args__
    except:
        return False
