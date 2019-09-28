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

###### a [dwt](https://github.com/derrickturk) / [terminus data science, LLC](https://www.terminusdatascience.com) joint
