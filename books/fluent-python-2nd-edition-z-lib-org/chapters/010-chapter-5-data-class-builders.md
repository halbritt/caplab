<span id="page-265-0"></span>
# Chapter 5: Data Class Builders

## A NOTE FOR EARLY RELEASE READERS

With Early Release ebooks, you get books in their earliest form—the author's raw and unedited content as they write—so you can take advantage of these technologies long before the official release of these titles.

This will be the 5th chapter of the final book. Please note that the GitHub repo will be made active later on.

If you have comments about how we might improve the content and/or examples in this book, or if you notice missing material within this chapter, please reach out to the author at [fluentpython2e@ramalho.org.](mailto:fluentpython2e@ramalho.org)

*Data classes are like children. They are okay as a starting point, but to participate as a grownup object, they need to take some responsibility. [1](#page-321-0)*

<span id="page-265-1"></span>—Martin Fowler and Kent Beck

Python offers a few ways to build a simple class that is just a collection of fields, with little or no extra functionality. That pattern is known as a "data class"—and dataclasses is one of the packages that supports this pattern. This chapter covers three different class builders that you may use as shortcuts to write data classes:

- collections.namedtuple: the simplest way—available since Python 2.6;
- typing.NamedTuple: an alternative that requires type hints on the fields—since Python 3.5, with class syntax added in 3.6;
- @dataclasses.dataclass: a class decorator that allows more customization than previous alternatives, adding lots of

options and potential complexity—since Python 3.7.

After covering those class builders, we will discuss why *Data Class* is also the name of a code smell: a coding pattern that may be a symptom of poor object-oriented design.

## NOTE

typing.TypedDict may seem like another data class builder. It uses similar syntax and is described right after typing.NamedTuple in the typing module [documentation for Python 3.9.](https://docs.python.org/3/library/typing.html#typing.TypedDict)

However, TypedDict does not build concrete classes that you can instantiate. It's just syntax to write type hints for function parameters and variables that will accept mapping values used as records, with keys as field names. We'll see them in [Chapter 15,](022-chapter-15-more-about-type-hints.md#page-738-0) ["TypedDict".](022-chapter-15-more-about-type-hints.md#page-746-0)

<span id="page-266-1"></span>
## What's new in this chapter

This chapter is new in *Fluent Python Second Edition*. The section "Classic [Named Tuples" appeared in chapter 2 of the](#page-276-0) *First Edition*, but the rest of the chapter is completely new.

We begin with a high level overview of the three class builders.

<span id="page-266-0"></span>
## Overview of data class builders

Consider a simple class to represent a geographic coordinate pair:

*Example 5-1. class/coordinates.py*

### **class Coordinate**:

```
 def __init__(self, lat, lon):
 self.lat = lat
 self.lon = lon
```

That Coordinate class does the job of holding latitude and longitude attributes. Writing the \_\_init\_\_ boilerplate becomes old real fast,

especially if your class has more than a couple of attributes: each of them is mentioned three times! And that boilerplate doesn't buy us basic features we'd expect from a Python object:

```
>>> from coordinates import Coordinate
>>> moscow = Coordinate(55.76, 37.62)
>>> moscow
<coordinates.Coordinate object at 0x107142f10> 
>>> location = Coordinate(55.76, 37.62)
>>> location == moscow 
False
>>> (location.lat, location.lon) == (moscow.lat, moscow.lon) 
True
```

- \_\_repr\_\_ inherited from object is not very helpful.
- Meaningless ==; the \_\_eq\_\_ method inherited from object compares object ids.
- Comparing two coordinates requires explicit comparison of each attribute.

The data class builders covered in this chapter provide the necessary \_\_init\_\_, \_\_repr\_\_, and \_\_eq\_\_ methods automatically, as well as other useful features.

## NOTE

None of the class builders discussed here depend on inheritance to do their work. Both collections.namedtuple and typing.NamedTuple build classes that are tuple subclasses. @dataclass is a class decorator that does not affect the class hierarchy in any way. Each of them uses different metaprogramming techniques to inject methods and data attributes into the class under construction.

Here is a Coordinate class built with namedtuple—a factory function that builds a subclass of tuple with the name and fields you specify:

```
>>> from collections import namedtuple
>>> Coordinate = namedtuple('Coordinate', 'lat lon')
>>> issubclass(Coordinate, tuple)
True
>>> moscow = Coordinate(55.756, 37.617)
>>> moscow
Coordinate(lat=55.756, lon=37.617) 
>>> moscow == Coordinate(lat=55.756, lon=37.617) 
True
```

- Useful \_\_repr\_\_.
- Meaningful \_\_eq\_\_.

The newer typing.NamedTuple provides the same functionality, adding a type annotation to each field:

```
>>> import typing
>>> Coordinate = typing.NamedTuple('Coordinate', [('lat', float),
('lon', float)])
>>> issubclass(Coordinate, tuple)
True
>>> typing.get_type_hints(Coordinate)
{'lat': <class 'float'>, 'lon': <class 'float'>}
```

## TIP

A typed named tuple can also be constructed with the fields given as keyword arguments, like this:

```
Coordinate = typing.NamedTuple('Coordinate', lat=float,
lon=float)
```

This is more readable, and also lets you provide the mapping of fields and types as \*\*fields\_and\_types.

Since Python 3.6, typing.NamedTuple can also be used in a class statement, with type annotations written as described in PEP 526—Syntax [for Variable Annotations. This is much more readable, and makes it easy to](https://www.python.org/dev/peps/pep-0526/) override methods or add new ones. [Example 5-2](#page-269-0) is the same Coordinate class, with a pair of float attributes and a custom \_\_str\_\_ to display a coordinate formatted like 55.8°N, 37.6°E:

<span id="page-269-0"></span>
## Example 5-2. typing\_namedtuple/coordinates.py

```
from typing import NamedTuple
class Coordinate(NamedTuple):
 lat: float
 lon: float
 def __str__(self):
 ns = 'N' if self.lat >= 0 else 'S'
 we = 'E' if self.lon >= 0 else 'W'
 return f'{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°
{we}'
```

<span id="page-269-2"></span>
## WARNING

Although NamedTuple appears in the class statement as a superclass, it's actually not. typing.NamedTuple uses the advanced functionality of a metaclass to customize the creation of the user's class. Check this out: [2](#page-321-1)

```
>>> issubclass(Coordinate, typing.NamedTuple)
False
>>> issubclass(Coordinate, tuple)
True
```

In the \_\_init\_\_ method generated by typing.NamedTuple, the fields appear as parameters in the same order they appear in the class statement.

Like typing.NamedTuple, the dataclass decorator supports PEP [526 syntax to declare instance attributes. The decorator reads the variable](https://www.python.org/dev/peps/pep-0526/) annotations and automatically generates methods for your class. For comparison, check out the equivalent Coordinate class written with the help of the dataclass decorator:

<span id="page-269-1"></span>
## Example 5-3. dataclass/coordinates.py

### **from dataclasses import** dataclass

```
@dataclass(frozen=True)
class Coordinate:
 lat: float
 lon: float
 def __str__(self):
 ns = 'N' if self.lat >= 0 else 'S'
 we = 'E' if self.lon >= 0 else 'W'
 return f'{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°
{we}'
```

Note that the body of the classes in [Example 5-2](#page-269-0) and [Example 5-3](#page-269-1) are identical—the difference is in the class statement itself. The @dataclass decorator does not depend on inheritance or a metaclass, so it should not interfere with your own use of these mechanisms. The Coordinate class in [Example 5-3](#page-269-1) is a subclass of object. [3](#page-321-2)

<span id="page-270-1"></span>
<span id="page-270-0"></span>
## Main features

The different data class builders have a lot in common. [Table 5-1](#page-271-0) summarizes.

<span id="page-271-0"></span>*Table5-1.Selectedfeaturescompareda*

C

C

r

0

S

S

t

h

e

t

h

r

e

e d

а

t

а

c l

а

S

S

b

u i

i l

d

e

r

S

X

S

t

а n

d

s f o

r

а

n i

n

S

t

а

n C

e

o f

а

d

а t

а

c l

а

S

S

0

f t h

а

t k

| namedtuple    | NamedTuple  | dataclass                                                                 |
|---------------|-------------|---------------------------------------------------------------------------|
|               |             | YES                                                                       |
| NO            | YES         | YES                                                                       |
| xasdict()     | xasdict()   | dataclasses.asdict(x)                                                     |
| xfields       | xfields     | [f.name for f in<br>dataclasses.fields(x)]                                |
|               |             | [f.default for f in<br>dataclasses.fields(x)]                             |
| N/A           |             | xannotations                                                              |
| xreplace(…)   | xreplace(…) | dataclasses.replace(x, …)                                                 |
| namedtuple(…) |             | dataclasses.make_dataclass(…<br>)                                         |
|               | NO          | NO<br>xfield_defaults<br>xfield_defaults<br>xannotations<br>NamedTuple(…) |

## WARNING

The classes built by typing.NamedTuple and @dataclass have an \_\_annotations\_\_ attribute holding the type hints for the fields. However, the best practice is not to read from \_\_annotations\_\_ directly, but use typing.get\_type\_hints(my\_data\_class) to obtain that information. That's because get\_type\_hints provides extra services, like resolving forward references [in type hints. We get back to this issue much later in the book, in "Problems with](022-chapter-15-more-about-type-hints.md#page-760-0) Annotations at Runtime".

Now let's discuss those main features.

## Mutable instances

A key difference between these class builders is that collections.namedtuple and typing.NamedTuple build tuple subclasses, therefore the instances are immutable. By default, @dataclass produces mutable classes. But the decorator accepts a keyword argument frozen—shown in [Example 5-3.](#page-269-1) When frozen=True, the class will raise an exception if you try to assign a value to a field after the instance is initialized.

<span id="page-275-0"></span>
## Class statement syntax

Only typing.NamedTuple and dataclass support the regular class statement syntax, making it easier to add methods and docstrings to the class you are creating.

## Construct dict

Both named tuple variants provide an instance method (.\_asdict) to construct a dict object from the fields in a data class instance. The dataclasses module provides a function to do it: dataclasses.asdict.

## Get field names and default values

All three class builders let you get the field names and default values that may be configured for them. In named tuple classes, that metadata is in the .\_fields and .\_fields\_defaults class attributes. You can get the same metadata from a dataclass decorated class using the fields function from the dataclasses module. It returns a tuple of Field objects which have several attributes, including name and default.

## Get field types

Classes defined with the help of typing.NamedTuple and @dataclass have a mapping of field names to type annotations the \_\_annotations\_\_ class attribute. As mentioned, use the

typing.get\_type\_hints function instead of readint \_\_annotations\_\_ directly.

## New instance with changes

Given a named tuple instance x, the call x.\_replace(\*\*kwargs) returns a new instance with some attribute values replaced according to the keyword arguments given. The dataclasses.replace(x, \*\*kwargs) module-level function does the same for an instance of a dataclass decorated class.

## New class at runtime

Although the class statement syntax is more readable, it is hard-coded. A framework may need to build data classes on the fly, at runtime. For that, you can use the default function call syntax of collections.namedtuple, which is likewise supported by typing.NamedTuple. The dataclasses module provides a make\_dataclass function for the same purpose.

After this overview of the main features of the data class builders, let's focus on each of them in turn, starting with the simplest.

<span id="page-276-0"></span>
## Classic Named Tuples

The collections.namedtuple function is a factory that builds subclasses of tuple enhanced with field names, a class name, and an informative \_\_repr\_\_. Classes built with namedtuple can be used anywhere where tuples are needed, and in fact many functions of the Python standard library that used to return tuples now return named tuples for convenience, without affecting user's code at all.

## TIP

Each instance of a class built by namedtuple takes exactly the same amount of memory as a tuple because the field names are stored in the class.

[Example 5-4](#page-277-0) shows how we could define a named tuple to hold information about a city.

<span id="page-277-0"></span>
## Example 5-4. Defining and using a named tuple type

```
>>> from collections import namedtuple
>>> City = namedtuple('City', 'name country population
coordinates') 
>>> tokyo = City('Tokyo', 'JP', 36.933, (35.689722, 139.691667)) 
>>> tokyo
City(name='Tokyo', country='JP', population=36.933, coordinates=
(35.689722,
139.691667))
>>> tokyo.population 
36.933
>>> tokyo.coordinates
(35.689722, 139.691667)
>>> tokyo[1]
'JP'
```

- Two parameters are required to create a named tuple: a class name and a list of field names, which can be given as an iterable of strings or as a single space-delimited string.
- Field values must be passed as separate positional arguments to the constructor (in contrast, the tuple constructor takes a single iterable).
- You can access the fields by name or position.

As a tuple subclass, City inherits useful methods such as \_\_eq\_\_ and the special methods for comparison operators—including \_\_lt\_\_ which allows sorting lists of City instances.

A named tuple offers a few attributes and methods in addition to those inherited from tuple. [Example 5-5](#page-278-0) shows the most useful: the \_fields class attribute, the class method \_make(iterable), and the \_asdict() instance method.

<span id="page-278-0"></span>
## Example 5-5. Named tuple attributes and methods (continued from the previous example)

```
>>> City._fields 
('name', 'country', 'population', 'location')
>>> Coordinate = namedtuple('Coordinate', 'lat lon')
>>> delhi_data = ('Delhi NCR', 'IN', 21.935, Coordinate(28.613889,
77.208889))
>>> delhi = City._make(delhi_data) 
>>> delhi._asdict() 
{'name': 'Delhi NCR', 'country': 'IN', 'population': 21.935,
'location': Coordinate(lat=28.613889, lon=77.208889)}
>>> import json
>>> json.dumps(delhi._asdict()) 
'{"name": "Delhi NCR", "country": "IN", "population": 21.935,
"location": [28.613889, 77.208889]}'
```

- .\_fields is a tuple with the field names of the class.
- .\_make() builds City from an iterable; City(\*delhi\_data) would do the same.
- .\_asdict() returns a dict built from the named tuple instance.
- .\_asdict() is useful to serialize the data in JSON format, for example.

## WARNING

The \_asdict method returned an OrderedDict until Python 3.7. Since Python 3.8, it returns a simple dict—which is OK now that we can rely on key insertion order. If you must have an OrderedDict, the \_asdict [documentation](https://docs.python.org/3.8/library/collections.html#collections.somenamedtuple._asdict) recommends building one from the result: OrderedDict(x.\_asdict()).

Since Python 3.7, namedtuple accepts the defaults keyword-only argument providing an iterable of N default values for each of the N

rightmost fields of the class. [Example 5-6](#page-279-0) shows how to define a Coordinate named tuple with a default value for a reference field:

<span id="page-279-0"></span>*Example 5-6. Named tuple attributes and methods, continued from [Example 5-5](#page-278-0).*

```
>>> Coordinate = namedtuple('Coordinate', 'lat lon reference',
defaults=['WGS84'])
>>> Coordinate(0, 0)
Coordinate(lat=0, lon=0, reference='WGS84')
>>> Coordinate._field_defaults
{'reference': 'WGS84'}
```

In ["Class statement syntax"](#page-275-0) I mentioned it's easier to code methods with the class syntax supported by typing.NamedTuple and @dataclass. You can also add methods to a namedtuple, but it's a hack. Skip the following box if you're not interested in hacks.

## HACKING A NAMEDTUPLE TO INJECT A METHOD

Recall how we built the Card class in [Example 1-1](005-chapter-1-the-python-data-model.md#page-23-0) in [Chapter 1](005-chapter-1-the-python-data-model.md#page-20-0):

```
Card = collections.namedtuple('Card', ['rank', 'suit'])
```

Later in [Chapter 1](005-chapter-1-the-python-data-model.md#page-20-0) I wrote a spades\_high function for sorting. It would be nice if that logic was encapsulated in a method of Card, but adding spades\_high to Card without the benefit of a class statement requires a quick hack: define the function and then assign it to a class attribute. [Example 5-7](#page-280-0) shows how.

<span id="page-280-0"></span>*Example 5-7. frenchdeck.doctest: Adding a class attribute and a method to Card, the [namedtuple](005-chapter-1-the-python-data-model.md#page-23-1) from "A Pythonic Card Deck"*

```
>>> Card.suit_values = dict(spades=3, hearts=2, diamonds=1,
clubs=0) 
>>> def spades_high(card): 
... rank_value = FrenchDeck.ranks.index(card.rank)
... suit_value = card.suit_values[card.suit]
... return rank_value * len(card.suit_values) + suit_value
...
>>> Card.overall_rank = spades_high 
>>> lowest_card = Card('2', 'clubs')
>>> highest_card = Card('A', 'spades')
>>> lowest_card.overall_rank() 
0
>>> highest_card.overall_rank()
51
```

- Attach a class attribute with values for each suit.
- spades\_high will become a method; the first argument doesn't need to be named self. Anyway, it will get the receiver when called as a method.

Attach the function to the Cards class as a method named overall\_rank.

It works!

For readability and future maintenance, it's much better to code methods inside a class statement. But it's good to know this hack is possible, because it may come in handy. [4](#page-321-3)

<span id="page-281-0"></span>This was a small detour to showcase the power of a dynamic language.

Now let's check out the typing.NamedTuple variation.

<span id="page-281-1"></span>
## Typed Named Tuples

The Coordinate class with a default field from [Example 5-6](#page-279-0) can be written like this using typing.NamedTuple:

*Example 5-8. typing\_namedtuple/coordinates2.py*

```
from typing import NamedTuple
class Coordinate(NamedTuple):
 lat: float 
 lon: float
 reference: str = 'WGS84'
```

- Every instance field must be annotated with a type.
- The reference instance field is annotated with a type and a default value

Classes built by typing.NamedTuple don't have any methods beyond those that collections.namedtuple also generates—and those that are inherited from tuple. The only difference is the presence of the \_\_annotations\_\_ class attribute—which Python completely ignores at runtime.

Given that the main feature of typing.NamedTuple are the type annotations, we'll take a brief look at them before resuming our exploration of data class builders.

<span id="page-282-2"></span>
## Type hints 101

Type hints—a.k.a. type annotations—are ways to declare the expected type of function arguments, return values, variables, and attributes.

## NOTE

This is a very brief introduction to type hints, just enough to make sense of the syntax and meaning of the annotations used typing.NamedTuple and @dataclass declarations. We will cover type hints for function signatures in [Chapter 8](014-chapter-8-type-hints-in-functions.md#page-388-0) and more advanced annotations in [Chapter 15.](022-chapter-15-more-about-type-hints.md#page-738-0) Here we'll mostly see hints with simple built-in types, such as str, int, and float, which are probably the most common types used to annotate fields of data classes.

The first thing you need to know about type hints is that they are not enforced at all by the Python bytecode compiler and interpreter.

<span id="page-282-1"></span>
## No runtime effect

A good way to understand Python type hints is to think of them as "documentation that can be verified by IDEs and type checkers."

That's because type hints have no impact on the runtime behavior of Python programs. Check this out:

<span id="page-282-0"></span>*Example 5-9. Python does not enforce type hints at runtime.*

```
>>> import typing
>>> class Coordinate(typing.NamedTuple):
... lat: float
... lon: float
...
>>> trash = Coordinate('Ni!', None)
>>> print(trash)
Coordinate(lat='Ni!', lon=None)
```

I told you: no type checking at runtime!

If you type the code of [Example 5-9](#page-282-0) in a Python module, it will run and display a meaningless Coordinate, with no error or warning:

```
$ python3 nocheck_demo.py
Coordinate(lat='Ni!', lon=None)
```

The type hints are intended primarily to support third-party type checkers, like [Mypy](http://mypy-lang.org/) or the [PyCharm IDE](https://www.jetbrains.com/pycharm/) built-in type checker. These are static analysis tools: they check Python source code "at rest", not running code.

To see the effect of type hints, you must run one of those tools on your code —like a linter. For instance, here is what Mypy has to say about the previous example:

```
$ mypy nocheck_demo.py
nocheck_demo.py:8: error: Argument 1 to "Coordinate" has
incompatible type "str"; expected "float"
nocheck_demo.py:8: error: Argument 2 to "Coordinate" has
incompatible type "None"; expected "float"
```

As you can see, given the definition of Coordinate, Mypy knows that both arguments to create an instance must be of type float, but the assignment to trash uses a str and None. [5](#page-321-4)

<span id="page-283-0"></span>Now let's talk about the syntax and meaning of type hints.

<span id="page-283-1"></span>
## Variable annotation syntax

Both typing.NamedTuple and @dataclass use the syntax of variable annotations defined in [PEP 526](https://www.python.org/dev/peps/pep-0526/). This is a quick introduction to that syntax in the context defining attributes in class statements.

The basic syntax of variable annotation is:

```
var_name: some_type
```

Section [Acceptable type hints](https://www.python.org/dev/peps/pep-0484/#acceptable-type-hints) in PEP 484 explains what are acceptable types, but in the context of defining a data class, these types are more likely to be useful:

- a concrete class, for example str or FrenchDeck;
- a parameterized collection type, like list[int], tuple[str, float] etc.
- typing.Optional, for example Optional[str]—to declare a field that can be a str or None.

You can also initialize the variable with a value. In a typing.NamedTuple or @dataclass declaration, that value will become the default for that attribute, if the corresponding argument is omitted in the constructor call.

```
var_name: some_type = a_value
```

<span id="page-284-1"></span>
## The meaning of variable annotations

We saw in ["No runtime effect"](#page-282-1) that type hints have no effect at runtime. But at import time—when a module is loaded—Python does read them to build the \_\_annotations\_\_ dictionary that typing.NamedTuple and @dataclass then use to enhance the class.

We'll start this exploration with a simple class, so that we can later see what extra features are added by typing.NamedTuple and @dataclass.

<span id="page-284-0"></span>*Example 5-10. meaning/demo\_plain.py: a plain class with type hints*

```
class DemoPlainClass:
 a: int 
 b: float = 1.1 
 c = 'spam'
```

a becomes an entry in \_\_annotations\_\_, but is otherwise discarded: no attribute named a is created in the class.

- b is saved as an annotation, and also becomes a class attribute with value 1.1.
- c is just a plain old class attribute, not an annotation.

We can verify that in the console, first reading the \_\_annotations\_\_ of the DemoPlainClass, then trying to get its attributes named a, b, and c:

```
>>> from demo_plain import DemoPlainClass
>>> DemoPlainClass.__annotations__
{'a': <class 'int'>, 'b': <class 'float'>}
>>> DemoPlainClass.a
Traceback (most recent call last):
 File "<stdin>", line 1, in <module>
AttributeError: type object 'DemoPlainClass' has no attribute 'a'
>>> DemoPlainClass.b
1.1
>>> DemoPlainClass.c
'spam'
```

Note that the \_\_annotations\_\_ special attribute is created by the interpreter to record the type hints that appear in the source code—even in a plain class.

<span id="page-285-0"></span>The a survives only as an annotation. It doesn't become a class attribute because no value is bound to it. The b and c are stored as class attributes because they are bound to values. [6](#page-321-5)

None of those three attributes will be in a new instance of DemoPlainClass. If you create an object o = DemoPlainClass(), o.a will raise AttributeError, while o.b and o.c will retrieve the class attributes with values 1.1 and 'spam'—that's just normal Python object behavior.

## Inspecting a typing.NamedTuple

Now let's examine a class built with typing.NamedTuple, using the [same attributes and annotations as](#page-284-0) DemoPlainClass from Example 5<span id="page-286-0"></span>*Example 5-11. meaning/demo\_nt.py: a class built with typing.NamedTuple.*

```
import typing
class DemoNTClass(typing.NamedTuple):
 a: int 
 b: float = 1.1 
 c = 'spam'
```

- a becomes an annotation and also an instance attribute.
- b is another annotation, and also becomes an instance attribute with default value 1.1.
- c is just a plain old class attribute; no annotation will refer to it.

Inspecting the DemoNTClass, we get:

```
>>> from demo_nt import DemoNTClass
>>> DemoNTClass.__annotations__
{'a': <class 'int'>, 'b': <class 'float'>}
>>> DemoNTClass.a
<_collections._tuplegetter object at 0x101f0f940>
>>> DemoNTClass.b
<_collections._tuplegetter object at 0x101f0f8b0>
>>> DemoNTClass.c
'spam'
```

Here we have the same annotations for a and b as we saw in [Example 5-10.](#page-284-0) But typing.NamedTuple creates a and b class attributes. The c attribute is just a plain class attribute with the value 'spam'.

The a and b class attributes are *descriptors*—an advanced feature covered in [Chapter 24.](031-chapter-24-attribute-descriptors.md#page-1258-0) For now, think of them as similar to property getters: methods that don't require the explicit call operator () to retrieve an instance attribute. In practice, this means a and b will work as read-only

instance attributes—which makes sense when we recall that DemoNTClass instances are just fancy tuples, and tuples are immutable.

DemoNTClass also gets a custom docstring:

```
>>> DemoNTClass.__doc__
'DemoNTClass(a, b)'
```

Let's inspect an instance of DemoNTClass:

```
>>> nt = DemoNTClass(8)
>>> nt.a
8
>>> nt.b
1.1
>>> nt.c
'spam'
```

To construct nt, we need to give at least the a argument to DemoNTClass. The constructor also takes a b argument, but it has a default value of 1.1, so it's optional. The nt object has the a and b attributes as expected; it doesn't have a c attribute, but Python retrieves it from the class, as usual.

If you try to assign values to nt.a, nt.b, nt.c or even nt.z you'll get AttributeError exceptions, with subtly different error messages. Try that and reflect on the messages.

<span id="page-287-1"></span>
## Inspecting a class decorated with dataclass

Now we'll examine [Example 5-12:](#page-287-0)

<span id="page-287-0"></span>*Example 5-12. meaning/demo\_dc.py: a class decorated with @dataclass* **from dataclasses import** dataclass

```
@dataclass
class DemoDataClass:
 a: int 
 b: float = 1.1 
 c = 'spam'
```

- a becomes an annotation and also an instance attribute controlled by a descriptor.
- b is another annotation, and also becomes an instance attribute with a descriptor and a default value 1.1.
- c is just a plain old class attribute; no annotation will refer to it.

Now let's check out \_\_annotations\_\_, \_\_doc\_\_, and the a, b, c attributes on DemoDataClass:

```
>>> from demo_dc import DemoDataClass
>>> DemoDataClass.__annotations__
{'a': <class 'int'>, 'b': <class 'float'>}
>>> DemoDataClass.__doc__
'DemoDataClass(a: int, b: float = 1.1)'
>>> DemoDataClass.a
Traceback (most recent call last):
 File "<stdin>", line 1, in <module>
AttributeError: type object 'DemoDataClass' has no attribute 'a'
>>> DemoDataClass.b
1.1
>>> DemoDataClass.c
'spam'
```

The \_\_annotations\_\_ and \_\_doc\_\_ are not surprising. However, there is no attribute named a in DemoDataClass—in contrast with DemoNTClass from [Example 5-11,](#page-286-0) which has a descriptor to get a from the instances as read-only attributes (that mysterious <\_collections.\_tuplegetter>). That's because the a attribute will only exist in instances of DemoDataClass. It will be a public attribute that we can get and set, unless the class is frozen. But b and c exist as class attributes, with b holding the default value for the b instance attribute, while c is just a class attribute that will not be bound to the instances.

Now let's see how a DemoDataClass instance looks like:

```
>>> dc = DemoDataClass(9)
>>> dc.a
9
>>> dc.b
1.1
>>> dc.c
'spam'
```

Again, a and b are instance attributes, and c is a class attribute we get via the instance.

As mentioned, DemoDataClass instances are mutable—and no type checking is done at runtime:

```
>>> dc.a = 10
>>> dc.b = 'oops'
```

We can do even sillier assignments:

```
>>> dc.c = 'whatever'
>>> dc.z = 'secret stash'
```

Now the dc instance has a c attribute—but that does not change the c class attribute. And we can add a new z attribute. This is normal Python behavior: regular instances can have their own attributes that don't appear in the class. [7](#page-322-0)

<span id="page-289-1"></span>
<span id="page-289-0"></span>
## More about @dataclass

We've only seen simple examples of @dataclass use so far. The decorator accepts several keyword arguments. This is its signature:

```
@dataclass(*, init=True, repr=True, eq=True, order=False,
 unsafe_hash=False, frozen=False)
```

The \* in the first position means the remaining parameters are keywordonly. [Table 5-2](#page-290-0) describes them.

<span id="page-290-0"></span>*Table5-2.Keywordparametersaccepte*

*d*

*b*

*y*

*t*

*h*

*e*

*@*

*d*

*a*

*t*

*a*

*c*

*l*

*a*

*s*

*s*

*d*

*e c*

*o*

*r*

*a*

*t*

*o*

*r*

| option | meaning            | default | notes                                     |
|--------|--------------------|---------|-------------------------------------------|
| init   | generateinit_<br>_ | True    | Ignored ifinit is<br>implemented by user. |
| repr   | generaterepr_<br>_ | True    | Ignored ifrepr is<br>implemented by user. |

| eq          | generate <u>eq</u>            | True  | Ignored ifeq is implemented by user.                                                                                           |
|-------------|-------------------------------|-------|--------------------------------------------------------------------------------------------------------------------------------|
| order       | generatelt,<br>le,gt,<br>ge   |       | If True, raises exceptions if eq=F alse, or if any of the comparison methods that would be generated are defined or inherited. |
| unsafe_hash | generatehash_<br>_            | False | Complex semantics and several caveats—see: dataclass documentation.                                                            |
| frozen      | make instances<br>"immutable" | False | instances will be reasonably safe<br>from accidental change, but not<br>really immutable. <sup>a</sup>                         |

<span id="page-292-1"></span><span id="page-292-0"></span>a @dataclass emulates immutability by generating \_\_setattr\_\_ and \_\_delattr\_\_ which raise dataclass.FrozenInstanceError—a subclass of AttributeError—when the user attempts to set or delete a field.

The defaults are really the most useful settings for common use cases. The options you are more likely to change from the defaults are:

- frozen=True: to protect against accidental changes to the class instances;
- order=True: to allow sorting of instances of the data class.

Given the dynamic nature of Python objects, it's not too hard for a nosy programmer to go around the protection afforded by frozen=True. But the necessary tricks should be easy to spot on a code review.

If the eq and frozen arguments are both True, @dataclass produces a suitable \_\_hash\_\_ method, so the instances will be hashable. The generated \_\_hash\_\_ will use data from all fields that are not individually excluded using a field option we'll see in "Field options". If frozen=False (the default), @dataclass will set \_\_hash\_\_ to None, signalling that the instances are unhashable, therefore overriding \_\_hash\_\_ from any superclass.

[PEP 557—Data Classes](https://www.python.org/dev/peps/pep-0557/) has this to say about unsafe\_hash:

*Although not recommended, you can force Data Classes to create a \_\_hash\_\_ method with unsafe\_hash=True. This might be the case if your class is logically immutable but can nonetheless be mutated. This is a specialized use case and should be considered carefully.*

I will leave unsafe\_hash at that. If you feel you must use that option, check the [dataclasses.dataclass](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) documentation.

Further customization of the generated data class can be done at a field level.

<span id="page-293-0"></span>
## Field options

We've already seen the most basic field option: providing or not a default value with the type hint. The instance fields you declare will become parameters in the generated \_\_init\_\_. Python does not allow parameters without defaults after parameters with defaults, therefore after you declare a field with a default value, all remaining fields must also have default values.

Mutable default values are a common source of bugs for beginning Python developers. In function definitions, a mutable default value is easily corrupted when one invocation of the function mutates the default, changing the behavior of further invocations—an issue we'll explore in ["Mutable Types as Parameter Defaults: Bad Idea"](011-chapter-6-object-references-mutability-and-recycling.md#page-340-0) ([Chapter 6](011-chapter-6-object-references-mutability-and-recycling.md#page-323-0)). Class attributes are often used as default attribute values for instances, including in data classes. And @dataclass uses the default values in the type hints to generate parameters with defaults for \_\_init\_\_. To prevent bugs, @dataclass rejects the class definition in [Example 5-13](#page-293-1).

<span id="page-293-1"></span>*Example 5-13. dataclass/club\_wrong.py: this class raises ValueError*

```
@dataclass
class ClubMember:
 name: str
 guests: list = []
```

If you load the module with that ClubMember class, this is what you get:

```
$ python3 club_wrong.py
Traceback (most recent call last):
 File "club_wrong.py", line 4, in <module>
 class ClubMember:
 ...several lines ommitted...
ValueError: mutable default <class 'list'> for field guests is
not allowed:
use default_factory
```

The ValueError message explains the problem and suggests a solution: use default\_factory. This is how to correct ClubMember:

<span id="page-294-0"></span>*Example 5-14. dataclass/club.py: this ClubMember definition works.*

```
from dataclasses import dataclass, field
```

```
@dataclass
class ClubMember:
 name: str
 guests: list = field(default_factory=list)
```

In the guests field of [Example 5-14](#page-294-0), instead of a literal list, the default value is set by calling the dataclasses.field function with default\_factory=list.

The default\_factory parameter lets you provide a function, class, or any other callable, which will be invoked with zero arguments to build a default value each time an instance of the data class is created. This way, each instance of ClubMember will have its own list—instead of all instances sharing the same list from the class, which is rarely what we want and is often a bug.

## WARNING

It's good that @dataclass rejects class definitions with a list default value in a field. However, be aware that it is a partial solution that only applies to list, dict and set. Other mutable values used as defaults will not be flagged by @dataclass. It's up to you to understand the problem and remember to use a default factory to set mutable default values.

If you browse the [dataclasses](https://docs.python.org/3/library/dataclasses.html) module documentation, you'll see a list field defined with a novel syntax, as in [Example 5-15](#page-295-0).

<span id="page-295-0"></span>*Example 5-15. dataclass/club\_generic.py: this ClubMember definition is more precise*

```
from dataclasses import dataclass, field
@dataclass
class ClubMember:
 name: str
 guests: list[str] = field(default_factory=list)
```

list[str] means "a list of str".

The new syntax list[str] is a parameterized generic type: since Python 3.9, the list built-in accepts that bracket notation to specify the type of the list items.

## WARNING

Prior to Python 3.9, the built-in collections did not support generic type notation. As a temporary workaround, there are corresponding collection types in the typing module. If you need a parameterized list type hint in Python 3.8 or earlier, you must import the List type from typing and use it: List[str]. For more about this issue, see ["Legacy Support and Deprecated Collection Types".](014-chapter-8-type-hints-in-functions.md#page-414-0)

We'll cover generics in [Chapter 8](014-chapter-8-type-hints-in-functions.md#page-388-0). For now, note that both [Example 5-14](#page-294-0) and [Example 5-15](#page-295-0) are correct, and the Mypy type checker does not

complain about either of those class definitions.

The difference is that guests: list means that guests can be a list of objects of any kind, while guests: list[str] says that guests must be a list in which every item is a str. This will allow the type checker to find (some) bugs in code that puts invalid items in the list, or that read items from it.

The default\_factory is likely to be the most common option of the field function, but there are several others, listed in [Table 5-3](#page-297-0).

<span id="page-297-0"></span>*Table5-3.Keywordargumentsaccepted*

*b y t h e f i e l d f u n c t i o n*

<span id="page-298-1"></span><span id="page-298-0"></span>

| option          | meaning<br>default                                            |                    |
|-----------------|---------------------------------------------------------------|--------------------|
| default         | default value for field                                       | _MISSING_TYPE<br>a |
| default_factory | 0-parameter function used to produce a default                | _MISSING_TYPE      |
| init            | include field in parameters toinit                            | True               |
| repr            | include field inrepr                                          | True               |
| compare         | use field in comparison methodseq,lt etc.                     | True               |
| hash            | include field inhash calculation                              | b<br>None          |
| metadata        | mapping with user-defined data; ignored by the @datac<br>lass | None               |

- <span id="page-299-0"></span>[a](#page-298-0) dataclass.\_MISSING\_TYPE is a sentinel value indicating the option was not provided. It exists so we can set None as an actual default value, a common use case.
- <span id="page-299-1"></span>[b](#page-298-1) The option hash=None means the field will be used in \_\_hash\_\_ only if compare=True.

The default option exists because the field call takes the place of the default value in the field annotation. If you want to create an athlete field with default value of False, and also omit that field from the \_\_repr\_\_ method, you'd write this:

```
@dataclass
class ClubMember:
 name: str
 guests: list = field(default_factory=list)
 athlete: bool = field(default=False, repr=False)
```

<span id="page-299-3"></span>
## Post-init processing

The \_\_init\_\_ method generated by @dataclass only takes the arguments passed and assigns them—or their default values, if missing—to the instance attributes that are instance fields. But you may need to do more than that to initialize the instance. If that's the case, you can provide a \_\_post\_init\_\_ method. When that method exists, @dataclass will add code to the generated \_\_init\_\_ to call \_\_post\_init\_\_ as the last step.

Common use cases for \_\_post\_init\_\_ are validation and computing field values based on other fields. We'll study a simple example that uses \_\_post\_init\_\_ for both of these reasons.

First, let's look at the expected behavior of a ClubMember subclass named HackerClubMember, as described by doctests in [Example 5-16](#page-299-2).

<span id="page-299-2"></span>*Example 5-16. dataclass/hackerclub.py: doctests for HackerClubMember*

*"""*

*<sup>``</sup>HackerClubMember`` objects accept an optional ``handle``*

```
argument::
 >>> anna = HackerClubMember('Anna Ravenscroft',
handle='AnnaRaven')
 >>> anna
 HackerClubMember(name='Anna Ravenscroft', guests=[],
handle='AnnaRaven')
If ``handle`` is ommitted, it's set to the first part of the
member's name::
 >>> leo = HackerClubMember('Leo Rochael')
 >>> leo
 HackerClubMember(name='Leo Rochael', guests=[], handle='Leo')
Members must have a unique handle. The following ``leo2`` will not
be created,
because its ``handle`` would be 'Leo', which was taken by ``leo``::
 >>> leo2 = HackerClubMember('Leo DaVinci')
 Traceback (most recent call last):
 ...
 ValueError: handle 'Leo' already exists.
To fix, ``leo2`` must be created with an explicit ``handle``::
 >>> leo2 = HackerClubMember('Leo DaVinci', handle='Neo')
 >>> leo2
 HackerClubMember(name='Leo DaVinci', guests=[], handle='Neo')
"""
```

Note that we must provide handle as a keyword argument, because HackerClubMember inherits name and guests from ClubMember, and adds the handle field. The generated docstring for HackerClubMember shows the order of the fields in the constructor call:

```
>>> HackerClubMember.__doc__
"HackerClubMember(name: str, guests: list = <factory>, handle:
str = '')"
```

Here, <factory> is a short way of saying that some callable will produce the default value for guests (in our case, the factory is the list class).

The point is: to provide a handle but no guests, we must pass handle as a keyword argument.

The [Inheritance](https://docs.python.org/3/library/dataclasses.html#inheritance) section of the dataclasses module documentation explains how the order of the fields is computed when there are several levels of inheritance.

## NOTE

In [Chapter 14](021-chapter-14-inheritance-for-good-or-for-worse.md#page-701-0) we'll talk about misusing inheritance, particularly when the superclasses are not abstract. Creating a hierarchy of data classes is usually a bad idea, but it served us well here to make [Example 5-17](#page-301-0) shorter, focusing on the handle field declaration and \_\_post\_init\_\_ validation.

## Example 5-17 is the implementation:

<span id="page-301-0"></span>*Example 5-17. dataclass/hackerclub.py: code for HackerClubMember.*

```
from dataclasses import dataclass
from club import ClubMember
@dataclass
class HackerClubMember(ClubMember): 
 all_handles = set() 
 handle: str = '' 
 def __post_init__(self):
 cls = self.__class__ 
 if self.handle == '': 
 self.handle = self.name.split()[0]
 if self.handle in cls.all_handles: 
 msg = f'handle {self.handle!r} already exists.'
 raise ValueError(msg)
 cls.all_handles.add(self.handle)
```

- HackerClubMember extends ClubMember.
- all\_handles is a class attribute.

handle is an instance field of type str with empty string as its default value; this makes it optional.

- Get the class of the instance.
- If self.handle is the empty string, set it to the first part of name.
- If self.handle is in cls.all\_handles, raise ValueError.
- Add the new handle to cls.all\_handles.

[Example 5-17](#page-301-0) works as intended, but is not satisfactory to a static type checker. Next, we'll see why, and how to fix it.

<span id="page-302-0"></span>
## Typed class attributes

If we typecheck [Example 5-17](#page-301-0) with Mypy, we are reprimanded:

```
$ mypy hackerclub.py
hackerclub.py:37: error: Need type annotation for "all_handles"
(hint: "all_handles: Set[<type>] = ...")
Found 1 error in 1 file (checked 1 source file)
```

Unfortunately, the hint provided by Mypy (version 0.910 as I review this) is not helpful in the context of @dataclass usage. First, it suggests using Set, but I am using Python 3.9 so I can use set—and avoid importing Set from typing. More importantly, if we add a type hint like set[…] to all\_handles, @dataclass will find that annotation and make all\_handles [an instance field. We saw this happening in "Inspecting a](#page-287-1) class decorated with dataclass".

The workaround defined in [PEP 526—Syntax for Variable Annotations](https://www.python.org/dev/peps/pep-0526/#class-and-instance-variable-annotations) is ugly. To code a class variable with a type hint`, we need to use a pseudotype named typing.ClassVar, which leverages the generics [] notation to set the type of the variable and also declare it a class attribute.

To make the type checker and @dataclass happy, this is how we are supposed to declare all\_handles in [Example 5-17:](#page-301-0)

```
 all_handles: ClassVar[set[str]] = set()
```

That type hint is saying:

*all\_handles is a class attribute of type set-of-str, with an empty set as its default value.*

To code that annotation, we must import ClassVar from the typing module.

The @dataclass decorator doesn't care about the types in the annotations, except in two cases, and this is one of them: if the type is ClassVar, an instance field will not be generated for that attribute.

The other case where the type of the field is relevant to @dataclass is when declaring *init-only variables*, our next topic.

<span id="page-303-1"></span>
## Initialization variables that are not fields

Sometimes you may need to pass arguments to \_\_init\_\_ that are not instance fields. Such arguments are called *init-only variables* by the [dataclasses](https://docs.python.org/3/library/dataclasses.html#init-only-variables) documentation. To declare an argument like that, dataclasses module provides the pseudo-type InitVar, which uses the same syntax of typing.ClassVar. The example given in the documentation is a data class that has a field initialized from a database, and the database object must be passed to the constructor.

This is the code that illustrates the [Init-only variables](https://docs.python.org/3/library/dataclasses.html#init-only-variables) section:

<span id="page-303-0"></span>*Example 5-18. Example from the [dataclasses](https://docs.python.org/3/library/dataclasses.html#init-only-variables) module documentation.*

```
@dataclass
class C:
 i: int
 j: int = None
 database: InitVar[DatabaseType] = None
```

```
 def __post_init__(self, database):
 if self.j is None and database is not None:
 self.j = database.lookup('j')
c = C(10, database=my_database)
```

Note how the database attribute is declared. InitVar will prevent @dataclass from treating database as a regular field. It will not be set as an instance attribute, and the dataclasses.fields function will not list it. However, database will be one of the arguments that the generated \_\_init\_\_ will accept, and it will be also passed to \_\_post\_init\_\_ if you write that method, you must add a corresponding argument to the method signature, as shown in [Example 5-18](#page-303-0)

This rather long overview of @dataclass covered the most useful features—some of them appeared in previous sections, like ["Main features"](#page-270-0) where we covered all three data class builders in parallel. The [dataclasses](https://docs.python.org/3/library/dataclasses.html#init-only-variables) [documentation and PEP 526 — Syntax for Variable](https://www.python.org/dev/peps/pep-0526/) Annotations have all details.

In the next section, I present a longer example with @dataclass.

<span id="page-304-2"></span>
## @dataclass Example: Dublin Core Resource Record

Often, classes built with @dataclass will have more fields than the very short examples presented so far. [Dublin Core](https://dublincore.org/specifications/dublin-core/) provides the foundation for a more typical @dataclass example.

<span id="page-304-1"></span>*The Dublin Core Schema is a small set of vocabulary terms that can be used to describe digital resources (video, images, web pages, etc.), as well as physical resources such as books or CDs, and objects like artworks. [8](#page-322-1)*

—Dublin Core on Wikipedia

[The standard defines 15 optional fields, the](#page-304-0) Resource class in Example 5- 19 uses 8 of them.

<span id="page-304-0"></span>*Example 5-19. dataclass/resource.py: code for Resource, a class based on Dublin Core terms.*

```
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto
from datetime import date
class ResourceType(Enum): 
 BOOK = auto()
 EBOOK = auto()
 VIDEO = auto()
@dataclass
class Resource:
 """Media resource description."""
 identifier: str 
 title: str = '<untitled>' 
 creators: list[str] = field(default_factory=list)
 date: Optional[date] = None 
 type: ResourceType = ResourceType.BOOK 
 description: str = ''
 language: str = ''
 subjects: list[str] = field(default_factory=list)
```

- This Enum will provide type-safe values for the Resource.type field.
- identifier is the only required field.
- title is the first field with a default. This forces all fields below to provide defaults.
- The value of date can be a datetime.date instance, or None.
- The type field default is ResourceType.BOOK.

[Example 5-20](#page-305-0) is a doctest to demonstrate how a Resource record appears in code:

<span id="page-305-0"></span>*Example 5-20. dataclass/resource.py: code for Resource, a class based on Dublin Core terms.*

```
 >>> description = 'Improving the design of existing code'
 >>> book = Resource('978-0-13-475759-9', 'Refactoring, 2nd
Edition',
 ... ['Martin Fowler', 'Kent Beck'], date(2018, 11, 19),
 ... ResourceType.BOOK, description, 'EN',
 ... ['computer programming', 'OOP'])
 >>> book # doctest: +NORMALIZE_WHITESPACE
 Resource(identifier='978-0-13-475759-9', title='Refactoring,
2nd Edition',
 creators=['Martin Fowler', 'Kent Beck'],
date=datetime.date(2018, 11, 19),
 type=<ResourceType.BOOK: 1>, description='Improving the design
of existing code',
 language='EN', subjects=['computer programming', 'OOP'])
```

The \_\_repr\_\_ generated by @dataclass is OK, but we can make it more readable. This is the format we want from repr(book):

```
 >>> book # doctest: +NORMALIZE_WHITESPACE
 Resource(
 identifier = '978-0-13-475759-9',
 title = 'Refactoring, 2nd Edition',
 creators = ['Martin Fowler', 'Kent Beck'],
 date = datetime.date(2018, 11, 19),
 type = <ResourceType.BOOK: 1>,
 description = 'Improving the design of existing code',
 language = 'EN',
 subjects = ['computer programming', 'OOP'],
 )
```

[Example 5-21](#page-306-0) is the code of \_\_repr\_\_ to produce the format above. This example uses dataclass.fields to get the names of the data class fields.

<span id="page-306-0"></span>*Example 5-21. dataclass/resource\_repr.py: code for \_\_repr\_\_ [method implemented in the](#page-304-0) Resource class from Example 5- 19.*

```
 def __repr__(self):
 cls = self.__class__
 cls_name = cls.__name__
 indent = ' ' * 4
 res = [f'{cls_name}('] 
 for f in fields(cls): 
 value = getattr(self, f.name)
```

```
 res.append(f'{indent}{f.name} = {value!r},') 
 res.append(')') 
 return '\n'.join(res)
```

- Start the res list to build the output string with the class name and open parenthesis.
- For each field f in the class…
- Get the named attribute from the instance.
- Append an indented line with the name of the field and repr(value) —that's what the !r does.
- Append closing parenthesis.
- Build multiline string from res and return it.

With this example inspired by the soul of Dublin, Ohio, we conclude our tour of Python's data class builders.

Data classes are handy, but your project may suffer if you overuse them. The next section explains.

<span id="page-307-0"></span>
## Data class as a code smell

Whether you implement a data class writing all the code yourself or leveraging one of the class builders described in this chapter, be aware that it may signal a problem in your design.

In *Refactoring, Second Edition*, Martin Fowler and Kent Beck present a catalog of "code smells"—patterns in code that may indicate the need for refactoring. The entry titled *Data Class* starts like this:

*These are classes that have fields, getting and setting methods for fields, and nothing else. Such classes are dumb data holders and are often being manipulated in far too much detail by other classes.*

<span id="page-308-0"></span>[In Fowler's personal Web site there's an illuminating post titled Code](https://martinfowler.com/bliki/CodeSmell.html) Smell. The post is very relevant to our discussion because he uses *data class* as one example of a code smell and suggests how to deal with it. Here is the post, reproduced in full.[9](#page-322-2)

## CODE SMELL

## By Martin Fowler

A code smell is a surface indication that usually corresponds to a deeper problem in the system. The term was first coined by Kent Beck while helping me with my [Refactoring](https://martinfowler.com/books/refactoring.html) book.

The quick definition above contains a couple of subtle points. Firstly a smell is by definition something that's quick to spot—or sniffable as I've recently put it. A long method is a good example of this—just looking at the code and my nose twitches if I see more than a dozen lines of Java.

The second is that smells don't always indicate a problem. Some long methods are just fine. You have to look deeper to see if there is an underlying problem there—smells aren't inherently bad on their own they are often an indicator of a problem rather than the problem themselves.

The best smells are something that's easy to spot and most of time lead you to really interesting problems. Data classes (classes with all data and no behavior) are good examples of this. You look at them and ask yourself what behavior should be in this class. Then you start refactoring to move that behavior in there. Often simple questions and initial refactorings can be the vital step in turning anemic objects into something that really has class.

One of the nice things about smells is that it's easy for inexperienced people to spot them, even if they don't know enough to evaluate if there's a real problem or to correct them. I've heard of lead developers who will pick a "smell of the week" and ask people to look for the smell and bring it up with the senior members of the team. Doing it one smell at a time is a good way of gradually teaching people on the team to be better programmers.

The main idea of Object Oriented Programming is to place behavior and data together in the same code unit: a class. If a class is widely used but has no significant behavior of its own, it's possible that code dealing with its instances is scattered (and even duplicated) in methods and functions throughout the system—a recipe for maintenance headaches. That's why Fowler's refactorings to deal with a data class involve bringing responsibilities back into it.

Taking that into account, there are a couple of common scenarios where it makes sense to have a data class with little or no behavior.

<span id="page-310-0"></span>
## Data class as scaffolding

In this scenario, the data class is an initial, simplistic implementation of a class to jump start a new project or module. With time, the class should get its own methods, instead of relying on methods of other classes to operate on its instances. Scaffolding is temporary; eventually your custom class may become fully independent from the builder you used to start it.

Python is also used for quick problem solving and experimentation, and then it's OK to leave the scaffolding in place.

<span id="page-310-1"></span>
## Data class as intermediate representation

A data class can be useful to build records about to be exported to JSON or some other interchange format, or to hold data that was just imported, crossing some system boundary. Python's data class builders all provide a method or function to convert an instance to a plain dict, and you can always invoke the constructor with a dict used as keyword arguments expanded with \*\*. Such a dict is very close to a JSON record.

In this scenario, the data class instances should be handled as immutable objects—even if the fields are mutable, you should not change them while they are in this intermediate form. If you do, you're losing the key benefit of having data and behavior close together. When importing/exporting

requires changing values, you should implement your own builder methods instead of using the given "as dict" methods or standard constructors.

Now we change the subject to see how to write patterns that match instances of arbitrary classes, and not just the sequences and mappings we've seen in the pattern matching sections of [Chapter 2](007-chapter-2-an-array-of-sequences.md#page-51-0) and [Chapter 3.](008-chapter-3-dictionaries-and-sets.md#page-140-0)

<span id="page-311-1"></span>
## Pattern Matching Class Instances

<span id="page-311-0"></span>Class patterns are designed to match class instances by type and optionally—by attributes. The subject of a class pattern can be any class instance, not only instances of data classes. [10](#page-322-3)

There are three variations of class patterns: simple, keyword, and positional. We'll study them in that order.

<span id="page-311-2"></span>
## Simple Class Patterns

We've already seen an example with simple class patterns used as subpatterns in ["Pattern Matching with Sequences":](007-chapter-2-an-array-of-sequences.md#page-81-0)

```
 case [str(name), _, _, (float(lat), float(lon))]:
```

That pattern matches a 4-item sequence where the first item must be an instance of str, and the last item must be a 2-tuple with two instances of float.

The syntax for class patterns looks like a constructor invocation. Below is a class pattern which matches float values, without binding a variable (the case body can refer to x directly if needed):

```
 match x:
 case float():
 do_something_with(x)
```

But this is likely to be a bug in your code:

```
 match x:
 case float: # DANGER!!!
 do_something_with(x)
```

In the example above, case float: matches any subject, because Python sees float as a variable, which is then bound to the subject.

The simple pattern syntax of float() or float(x) is a special case that [applies only to nine blessed built-in types, listed at the end of the](https://www.python.org/dev/peps/pep-0634/#class-patterns) *Class patterns* section of *[PEP 634—Structural Pattern Matching: Specification](https://www.python.org/dev/peps/pep-0634/)*:

```
bytes dict float frozenset int list set str tuple
```

In those classes, the variable that looks like a constructor argument—e.g. x in float(x)—is bound to the whole subject instance or the part of the subject that matches a subpattern, as exemplified by str(name) in the sequence pattern we saw earlier:

```
 case [str(name), _, _, (float(lat), float(lon))]:
```

If the class is not one of those nine blessed built-ins, then the argument-like variables or constants represent different attributes of the class, as if they were keyword arguments or positional arguments.

<span id="page-312-1"></span>
## Keyword Class Patterns

To understand how to use keyword class patterns, consider the following City class and five instances:

<span id="page-312-0"></span>*Example 5-22. City class and a few instances.*

```
import typing
class City(typing.NamedTuple):
 continent: str
 name: str
 country: str
cities = [
```

```
 City('Asia', 'Tokyo', 'JP'),
 City('Asia', 'Delhi', 'IN'),
 City('North America', 'Mexico City', 'MX'),
 City('North America', 'New York', 'US'),
 City('South America', 'São Paulo', 'BR'),
]
```

Given those definitions the following function would return a list of Asian cities:

```
def match_asian_cities():
 results = []
 for city in cities:
 match city:
 case City(continent='Asia'):
 results.append(city)
 return results
```

The pattern City(continent='Asia') matches any City instance where the continent attribute value is equal to 'Asia', regardless of the values of the other attributes.

If you want to collect the value of the country attribute, you could write:

```
def match_asian_countries():
 results = []
 for city in cities:
 match city:
 case City(continent='Asia', country=cc):
 results.append(cc)
 return results
```

The pattern City(continent='Asia', country=cc) matches the same Asian cities as before, but now the cc variable is bound to the country attribute of the instance. This also works if the pattern variable is called country as well:

```
 match city:
 case City(continent='Asia', country=country):
 results.append(country)
```

Keyword class patterns are very readable, and work with any class that has public instance attributes, but they are somewhat verbose.

Positional class patterns are more convenient in some cases, but they require explicit support by the class of the subject, as we'll see next.

<span id="page-314-0"></span>
## Positional Class Patterns

Given the definitions from [Example 5-22,](#page-312-0) the following function would return a list of Asian cities, using a positional class pattern:

```
def match_asian_cities_pos():
 results = []
 for city in cities:
 match city:
 case City('Asia'):
 results.append(city)
 return results
```

The pattern City('Asia') matches any City instance where the first attribute value is 'Asia', regardless of the values of the other attributes.

If you want to collect the value of the country attribute, you could write:

```
def match_asian_countries_pos():
 results = []
 for city in cities:
 match city:
 case City('Asia', _, country):
 results.append(country)
 return results
```

The pattern City('Asia', \_, country) matches the same cities as before, but now the country variable is bound to the third attribute of the instance.

I've mentioned "first" or "third" attribute, but what does that really mean?

What makes City or any class work with positional patterns is the presence of a special class attribute named \_\_match\_args\_\_, which the class builders in this chapter automatically create. This is value of \_\_match\_args\_\_ in the City class:

```
>>> City.__match_args__
('continent', 'name', 'country')
```

As you can see, \_\_match\_args\_\_ declares the names of the attributes in the order they will be used in positional patterns.

In [Chapter 11](018-chapter-11-a-pythonic-object.md#page-533-0) we'll write code to define \_\_match\_args\_\_ for a class we'll create without the help of a class builder.

## TIP

You can combine keyword and positional arguments in a pattern. Some but not all of the instance attributes available for matching may be listed in \_\_match\_args\_\_. Therefore, sometimes you may need to use keyword arguments in addition to positional arguments in a pattern.

<span id="page-315-0"></span>Time for a chapter summary.

## Chapter Summary

The main topic of this chapter were the data class builders collections.namedtuple, typing.NamedTuple and dataclasses.dataclass. We saw that each of them generate data classes from descriptions provided as arguments to a factory function or from class statements with type hints—in the case of the latter two. In particular, both named tuple variants produce tuple subclasses, adding only the ability to access fields by name, and providing a \_fields class attribute listing the field names as a tuple of strings.

Next we studied the main features of the three class builders side by side, including how to extract instance data as a dict, how to get the names and default values of fields, and how to make a new instance from an existing one.

This prompted our first look into type hints, particularly those used to annotate attributes in a class statement, using the notation introduced in Python 3.6 with [PEP 526—Syntax for Variable Annotations.](https://www.python.org/dev/peps/pep-0526/) Probably the most surprising aspect of type hints in general is the fact that they have no effect at all at runtime. Python remains a dynamic language. External tools, like Mypy, are needed to take advantage of typing information to detect errors via static analysis of the source code. After a basic overview of the syntax from PEP 526, we studied the effect of annotations in a plain class and in classes built by typing.NamedTuple and @dataclass.

Next we covered the most commonly used features provided by @dataclass and the default\_factory option of the dataclasses.field function. We also looked into the special pseudotype hints typing.ClassVar and dataclasses.InitVar that are important in the context of data classes. This main topic concluded with an example based on the Dublin Core Schema, which illustrated how to use dataclasses.fields to iterate over the attributes of a Resource instance in a custom \_\_repr\_\_.

["Data class as a code smell"](#page-307-0) came after that, warning against possible abuse of data classes defeating a basic principle of Object Oriented Programming: data and the functions that touch it should be together in the same class. Classes with no logic may be a sign of misplaced logic.

In the last section, we saw how pattern matching works with subjects that are instances of any class—not just classes built with the tools presented in this chapter.

<span id="page-317-0"></span>
## Further Reading

Python's standard documentation for the data class builders we covered is very good, and has quite a few small examples.

For @dataclass in particular, most of [PEP 557—Data Classes](https://www.python.org/dev/peps/pep-0557/) was copied into the [dataclasses](https://docs.python.org/3/library/dataclasses.html) module documentation. But [PEP 557](https://www.python.org/dev/peps/pep-0557/) has a [few very informative sections that were not copied, including Why not just](https://www.python.org/dev/peps/pep-0557/#id47) [use namedtuple?,](https://www.python.org/dev/peps/pep-0557/#id33) [Why not just use typing.NamedTuple](https://www.python.org/dev/peps/pep-0557/#id48)[? and the Rationale](https://www.python.org/dev/peps/pep-0557/#id33) section which concludes with this Q&A:

*Where is it not appropriate to use Data Classes?*

*API compatibility with tuples or dicts is required. Type validation beyond that provided by PEPs 484 and 526 is required, or value validation or conversion is required.*

—Eric V. Smith, PEP 557 Rationale

[Over at RealPython.com, Geir Arne Hjelle wrote a very complete Ultimate](https://realpython.com/python-data-classes/) Guide to Data Classes in Python 3.7.

[At PyCon US 2018, Raymond Hettinger presented Dataclasses: The code](https://www.youtube.com/watch?v=T-TwcmT6Rcw) generator to end all code generators (video).

[For more features and advanced functionality, including validation, the](https://www.attrs.org/en/stable/) *attrs* project led by Hynek Schlawack appeared years before dataclasses, and offers more features, promising to "bring back the joy of writing classes by relieving you from the drudgery of implementing object protocols (aka

dunder methods)." The influence of *attrs* on @dataclass is acknowledged by Eric V. Smith in PEP 557. This probably includes Smith's most important API decision: the use of a class decorator instead of a base class and/or a metaclass to do the job.

Glyph—founder of the Twisted project—wrote an excellent introduction to *attrs* in [The One Python Library Everyone Needs.](https://glyph.twistedmatrix.com/2016/08/attrs.html) The *attrs* documentation includes a [discussion of alternatives](https://attrs.readthedocs.io/en/stable/why.html).

Book author, instructor, and mad computer scientist Dave Beazley wrote *[cluegen](https://github.com/dabeaz/cluegen)*, yet another data class generator. If you've seen any of Dave's talks, you know he is a master of metaprograming Python from first principles. So, I found it inspiring to learn from the *cluegen README.md* file the concrete use case that motivated him to write an alternative to Python's @dataclass, and his philosophy of presenting an approach to solve the problem, in contrast to providing a tool: the tool may be quicker to use at first, but the approach is more flexible and can take you as far as you want to go.

Regarding *Data Class* as a code smell, the best source I found was Martin Fowler's book *Refactoring, Second Edition*. This newest version is missing the quote from the epigraph of this chapter, "Data classes are like children…", but otherwise it's the best edition of Fowler's most famous book, particularly for Pythonistas because the examples are in modern JavaScript, which is closer to Python than Java—the language of the first edition.

The Web site [Refactoring Guru](https://refactoring.guru/) also has a description of the [Data Class](https://refactoring.guru/smells/data-class) code smell.

## SOAPBOX

The entry for ["Guido"](https://web.archive.org/web/20190204130328/http://catb.org/esr/jargon/html/G/Guido.html) in the Jargon file is about Guido van Rossum. It says, among other things:

*Mythically, Guido's most important attribute besides Python itself is Guido's time machine, a device he is reputed to possess because of the unnerving frequency with which user requests for new features have been met with the response "I just implemented that last night…"*

For the longest time, one of the missing pieces in Python's syntax has been a quick, standard way to declare instance attributes in a class. Many Object-Oriented languages have that. Here is part of a Point class definition in Smalltalk:

```
Object subclass: #Point
 instanceVariableNames: 'x y'
 classVariableNames: ''
 package: 'Kernel-BasicObjects'
```

The second line lists the names of the instance attributes x and y. If there were class attributes, they would be in the third line.

Python has always offered an easy way to declare class attributes, if they have an initial value. But instance attributes are much more common, and Python coders have been forced to look into the \_\_init\_\_ method to find them, always afraid that there may be instance attributes created elsewhere in the class—or even created by external functions or methods of other classes.

Now we have @dataclass, yay!

But they bring their own problems.

First: when you use @dataclass, type hints are not optional. We've been promised for the last 7 years since [PEP 484—Type Hints](https://www.python.org/dev/peps/pep-0484/) that they would always be optional. Now we have a major new language feature

that requires them. If you don't like the whole static typing trend, you may want to use [attrs](https://www.attrs.org/en/stable/) instead.

Second: the [PEP 526](https://www.python.org/dev/peps/pep-0526/) syntax for annotating instance and class attributes reverses the established convention of class statements: everything declared at the top-level of a class block was a class attribute (methods are class attributes too). With PEP 526 and @dataclass, any attribute declared at the top level with a type hint becomes an instance attribute:

```
 @dataclass
 class Spam:
 repeat: int # instance attribute
```

Below, repeat is also an instance attribute:

```
 @dataclass
 class Spam:
 repeat: int = 99 # instance attribute
```

But if there are no type hints, suddenly you are back in the good old times when declarations at the top-level of the class belong to the class only:

```
 @dataclass
 class Spam:
 repeat = 99 # class attribute!
```

Finally, if you want to annotate that class attribute with a type, you can't use regular types because then it will become an instance attribute. You must resort to that pseudo-type ClassVar annotation:

```
 @dataclass
 class Spam:
 repeat: ClassVar[int] = 99 # aargh!
```

Here we are talking about the exception to the exception to the rule. This seems rather unpythonic to me.

[I did not take part in the discussions leading to PEP 526 or PEP 557—](https://www.python.org/dev/peps/pep-0557/) Data Classes, but here is an alternative syntax that I'd like to see:

### @dataclass

```
class HackerClubMember:
 .name: str 
 .guests: list = field(default_factory=list)
 .handle: str = ''
 all_handles = set()
```

- Instance attributes must be declared with a . prefix.
- Any attribute name that doesn't have a . prefix is a class attribute (as they always have been).

The language grammar would have to change to accept that. I find this quite readable, and it avoids the exception-to-the-exception issue.

I wish I could borrow Guido's time machine to go back to 2017 and sell this idea to the core team.

- <span id="page-321-0"></span>[1](#page-265-1) From *Refactoring, First Edition*, chapter 3, *Bad Smells in Code*, *Data Class* section, page 87.
- <span id="page-321-1"></span>[2](#page-269-2) Metaclasses are one of the subjects covered in [Chapter 25](032-chapter-25-class-metaprogramming.md#page-1296-0)—*Class Metaprogramming*.
- <span id="page-321-2"></span>[3](#page-270-1) Class decorators are covered in [Chapter 25](032-chapter-25-class-metaprogramming.md#page-1296-0)—*Class Metaprogramming*, along with metaclasses. Both are ways of customizing class behavior beyond what is possible with inheritance.
- <span id="page-321-3"></span>[4](#page-281-0) If you know Ruby, you know that injecting methods is a well-known but controversial technique among Rubyists. In Python, it's not as common, because it doesn't work with any built-in type—str, list, etc. I consider this limitation of Python a blessing.
- <span id="page-321-4"></span>[5](#page-283-0) In the context of type hints, None is not the NoneType singleton, but an alias for NoneType itself. This is strange when we stop to think about it, but appeals to our intuition and makes function return annotations easier to read in the common case of functions that return None.
- <span id="page-321-5"></span>[6](#page-285-0) Python has no concept of *undefined*, one of the silliest mistakes in the design of JavaScript. Thank Guido!

- <span id="page-322-0"></span>[7](#page-289-0) However, almost always when I see this in real code it's a bad idea. I once spent hours chasing a bug that was caused by attributes sneakily stashed in instances, like contraband across module borders. Also, setting an attribute after \_\_init\_\_ defeats the \_\_dict\_\_ keysharing memory optimization mentioned in ["Practical Consequences of How dict Works".](008-chapter-3-dictionaries-and-sets.md#page-172-0)
- <span id="page-322-1"></span>[8](#page-304-1) Source: [Dublin Core](https://en.wikipedia.org/wiki/Dublin_Core) article in the English Wikipedia.
- <span id="page-322-2"></span>[9](#page-308-0) I am fortunate to have Martin Fowler as a colleague at Thoughtworks, so it took just 20 minutes to get his permission.
- <span id="page-322-3"></span>[10](#page-311-0) I put this content here because it is the earliest chapter focusing on user-defined classes, and I thought pattern matching with classes was too important to wait until part III of the book. My philosophy: it's more important to know how to use classes than to define classes.
