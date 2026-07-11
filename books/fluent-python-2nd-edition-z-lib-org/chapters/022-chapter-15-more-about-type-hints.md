<span id="page-738-0"></span>
# Chapter 15: More About Type Hints

## A NOTE FOR EARLY RELEASE READERS

With Early Release ebooks, you get books in their earliest form—the author's raw and unedited content as they write—so you can take advantage of these technologies long before the official release of these titles.

This will be the 15th chapter of the final book. Please note that the GitHub repo will be made active later on.

If you have comments about how we might improve the content and/or examples in this book, or if you notice missing material within this chapter, please reach out to the author at [fluentpython2e@ramalho.org.](mailto:fluentpython2e@ramalho.org)

*I learned a painful lesson that for small programs, dynamic typing is great. For large programs you need a more disciplined approach. And it helps if the language gives you that discipline rather than telling you "Well, you can do whatever you want". [1](#page-795-0)*

<span id="page-738-1"></span>—Guido van Rossum, a fan of Monty Python

This chapter is a sequel to [Chapter 8,](014-chapter-8-type-hints-in-functions.md#page-388-0) covering more of Python's gradual type system. The main topics are:

- Overloaded function signatures;
- typing.TypedDict for type hinting dicts used as records;
- Type casting;
- Runtime access to type hints;

- Generic types:
  - Declaring a generic class;
  - Variance: invariant, covariant, and contravariant types;
  - Generic static protocols.

<span id="page-739-1"></span>
## What's new in this chapter

This chapter is new in *Fluent Python, Second Edition*.

Let's start with a subject that really belonged in [Chapter 8](014-chapter-8-type-hints-in-functions.md#page-388-0), but I moved it here because that was already the longest chapter in the book.

<span id="page-739-0"></span>
## Overloaded signatures

Some Python functions accept different combinations of arguments. The @typing.overload allows annotating each different combination. This is particularly important when the return type of the function depends on the type of two or more parameters.

Consider the sum built-in function. This is the text of help(sum):

```
>>> help(sum)
sum(iterable, /, start=0)
 Return the sum of a 'start' value (default: 0) plus an
iterable of numbers
 When the iterable is empty, return the start value.
 This function is intended specifically for use with numeric
values and may
 reject non-numeric types.
```

The sum built-in is written in C, but *typeshed* has overloaded type hints for it, in [builtins.pyi](https://github.com/python/typeshed/blob/a8834fcd46339e17fc8add82b5803a1ce53d3d60/stdlib/2and3/builtins.pyi#L1434):

```
@overload
def sum(__iterable: Iterable[_T]) -> Union[_T, int]: ...
```

```
@overload
def sum(__iterable: Iterable[_T], start: _S) -> Union[_T, _S]:
...
```

First let's look at the overall syntax of overloads. On a stub file (.pyi), that's all there would be about sum—the implementation would be in a different file.

The type checker tries to match the given arguments with each overloaded signature, in order. The call sum(range(100), 1000) doesn't match the first overload, but matches the second.

You can also use @overload in a regular Python module, by writing the overloaded signatures right before the function's actual signature and implementation. [Example 15-1](#page-740-0) shows how sum would appear annotated and implemented in a Python module.

<span id="page-740-0"></span>*Example 15-1. mysum.py: definition of the sum function with overloaded signatures:*

```
import functools
import operator
from collections.abc import Iterable
from typing import overload, Union, TypeVar
T = TypeVar('T')
S = TypeVar('S') 
@overload
def sum(it: Iterable[T]) -> Union[T, int]: ... 
@overload
def sum(it: Iterable[T], /, start: S) -> Union[T, S]: ... 
def sum(it, /, start=0): 
 return functools.reduce(operator.add, it, start)
```

- We need this second TypeVar in the second overload.
- This signature is for the simple case: sum(my\_iterable). The result type may be T—the type of the elements that my\_iterable yields or it may be int if the iterable is empty, because the default value of the start parameter is 0.

- When start is given, it can be of any type S, so the result type is Union[T, S]. This is why we need S. If we reused T then the type of start would have to be the same type as the elements of Iterable[T].
- The signature of the actual function implementation has no type hints.

That's a lot of lines to annotate a one-line function. Probably overkill, I know. At least it wasn't a foo function.

If you want to learn about @overload by reading code, *typeshed* has hundreds of examples. On *typeshed*, the [stub file](https://github.com/python/typeshed/blob/master/stdlib/2and3/builtins.pyi) for Python's built-ins has 186 overloads as I write this—more than any other in the standard library.

## TAKE ADVANTAGE OF** *GRADUAL* **TYPING

Aiming for 100% of annotated code may lead to type hints that add lots of noise but little value. Refactoring to simplify type hinting can lead to cumbersome APIs. Sometimes it's better to be pragmatic and leave a piece of code without type hints.

The handy APIs we call Pythonic are often hard to annotate. In the next section we'll see example of this: six overloads are needed to properly annotate the flexible max built-in function.

<span id="page-741-0"></span>
## Max Overload

It is difficult to add type hints to functions that leverage the powerful dynamic features of Python.

While studying *typeshed*, I found bug report [\(#4051](https://github.com/python/typeshed/issues/4051)): Mypy failed to warn that it is illegal to pass None as one of the arguments to the built-in max() function, or to pass an iterable that at some point yields None. In either case, you get a runtime exception like this one:

```
TypeError: '>' not supported between instances of 'int' and
'NoneType'
```

The documentation of max starts with this sentence:

*Return the largest item in an iterable or the largest of two or more arguments.*

To me, that's a very intuitive description.

But if I must annotate a function described in those terms, I have to ask: which is it? An iterable or two or more arguments?

The reality is more complicated because max also takes two optional keyword arguments: key and default.

I coded max in Python to make it easier to test (the original max is in C).

```
def max(first, *args, key=None, default=MISSING):
 if args:
 series = args
 candidate = first
 else:
 series = iter(first)
 try:
 candidate = next(series)
 except StopIteration:
 if default is not MISSING:
 return default
 raise ValueError(EMPTY_MSG) from None
 if key is None:
 for current in series:
 if candidate < current:
 candidate = current
 else:
 candidate_key = key(candidate)
 for current in series:
 current_key = key(current)
 if candidate_key < current_key:
 candidate = current
 candidate_key = current_key
 return candidate
```

<span id="page-742-0"></span>To fix [issue #4051](https://github.com/python/typeshed/issues/4051), I wrote the code in Example 15-2. [2](#page-795-1)

```
from typing import Protocol, Any, TypeVar, overload, Callable,
Iterable, Union
class SupportsLessThan(Protocol):
 def __lt__(self, other: Any) -> bool: ...
T = TypeVar('T')
LT = TypeVar('LT', bound=SupportsLessThan)
DT = TypeVar('DT')
MISSING = object()
EMPTY_MSG = 'max() arg is an empty sequence'
@overload
def max(__arg1: LT, __arg2: LT, *args: LT, key: None = ...) -> LT:
 ...
@overload
def max(__arg1: T, __arg2: T, *args: T, key: Callable[[T], LT]) ->
T:
 ...
@overload
def max(__iterable: Iterable[LT], *, key: None = ...) -> LT:
 ...
@overload
def max(__iterable: Iterable[T], *, key: Callable[[T], LT]) -> T:
 ...
@overload
def max(__iterable: Iterable[LT], *, key: None = ...,
 default: DT) -> Union[LT, DT]:
 ...
@overload
def max(__iterable: Iterable[T], *, key: Callable[[T], LT],
 default: DT) -> Union[T, DT]:
 ...
```

My Python implementation of max is about the same length as all those typing imports and declarations. Thanks to duck typing, my code has no isinstance checks, and provides the same error checking as those type hints—but only at runtime, of course.

The double underscore prefix in some arguments is a convention used on *typeshed* for positional-only arguments. That means you can call max(10, 20), but not max(\_\_arg1=10, \_\_arg2=20).

A key benefit of @overload making the return type as precise as possible, according to the types of the arguments given. Let's study the overloads for max in groups.

## Inputs implementing SupportsLessThan, no default=

```
@overload
def max(__arg1: LT, __arg2: LT, *_args: LT, key: None = ...) ->
LT:
 ...
# ... lines omitted ...
@overload
def max(__iterable: Iterable[LT], *, key: None = ...) -> LT:
 ...
```

In these cases the inputs are either separate arguments of type LT implementing SupportsLessThan, or an Iterable of such items. The return type of max is the same as the actual arguments or items, as described in [Link to Come].

Sample calls that match these overloads:

```
max(1, 2, -3) # returns 2
max(['Go', 'Python', 'Rust']) # returns 'Rust'
```

## key= provided, no default=

```
@overload
def max(__arg1: T, __arg2: T, *_args: T, key: Callable[[T], LT])
-> T:
 ...
# ... lines omitted ...
@overload
def max(__iterable: Iterable[T], *, key: Callable[[T], LT]) -> T:
 ...
```

The inputs can be separate items of any type T or a single Iterable[T], and key= must be a callable that takes an argument of the same type T, and returns a value that implements SupportsLessThan. The return type of max is the same as the actual arguments.

Sample calls that match these overloads:

```
max(1, 2, -3, key=abs) # returns -3
  max(['Go', 'Python', 'Rust'], key=len) # returns 'Python'
default= provided, no key=
  @overload
  def max(__iterable: Iterable[LT], *, key: None = ...,
   default: DT) -> Union[LT, DT]:
```

The input is an iterable of items of type LT implementing SupportsLessThan. The default= argument is the return value when the Iterable is empty. Therefore the return type of max must be a Union of type LT or the type of the default argument.

Sample calls that match these overloads:

```
max([1, 2, -3], default=0) # returns 2
max([], default=None) # returns None
```

## key= and default= provided

```
@overload
def max(__iterable: Iterable[T], *, key: Callable[[T], LT],
 default: DT) -> Union[T, DT]:
 ...
```

The inputs are:

...

- an Iterable of items of any type T;
- callable that takes an argument of type T and returns a value of type LT that implements SupportsLessThan;
- a default value of any type DT.

The return type of max must be a Union of type T or the type of the default argument.

```
max([1, 2, -3], key=abs, default=None) # returns -3
max([], key=abs, default=None) # returns None
```

<span id="page-746-1"></span>
## Takeaways from Overloading max

Type hints allow Mypy to flag a call like max([None, None]) with this error message:

```
mymax_demo.py:109: error: Value of type variable "_LT" of "max"
 cannot be "None"
```

On the other hand, having to write so many lines to support the type checker may discourage people from writing convenient and flexible functions like max. If I had to reinvent the min function as well, I could refactor and reuse most of the implementation of max. But I'd have to copy & paste all overloaded declarations—even though they would be identical for min, except for the function name.

My friend João S. O. Bueno—one of the smartest Python devs I know tweeted [this](https://twitter.com/gwidion/status/1265384692464967680):

*Although it is this hard to express the signature of max—it fits in one's mind quite easily. My understanding is that the expressiveness of annotation markings is very limited, compared to that of Python.*

Now let's study the TypedDict typing construct. It is not as useful as I imagined at first, but has its uses. Experimenting with TypedDict demonstrates the limitations of static typing for handling dynamic structures such as JSON data.

<span id="page-746-0"></span>
## TypedDict

## WARNING

It's tempting to use TypedDict to protect against errors while handling dynamic data structures like JSON API responses. But the examples here make clear that correct handling of JSON must be done at runtime, and not with static type checking. For runtime checking of JSON-like structures using type hints, check out the [pydantic](https://pypi.org/project/pydantic/) package on PyPI.

Python dictionaries are sometimes used as records, with the keys used as field names and field values of different types.

For example, consider a record describing a book in JSON or Python:

```
{"isbn": "0134757599",
 "title": "Refactoring, 2e",
 "authors": ["Martin Fowler", "Kent Beck"],
 "pagecount": 478}
```

Before Python 3.8, there was no good way to annotate a record like that, because the mapping types we saw in ["Generic mappings"](014-chapter-8-type-hints-in-functions.md#page-421-1) limit all values to have the same type.

Here are two lame attempts to annotate a record like the JSON object above:

```
Dict[str, Any]
```

The values may be of any type.

```
Dict[str, Union[str, int, List[str]]]
```

Hard to read, and doesn't preserve the relationship between field names and their respective field types: title is supposed to be a str, it can't be an int or a List[str].

*[PEP 589—TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys](https://www.python.org/dev/peps/pep-0589/)* addressed that problem. Here is a simple TypedDict:

*Example 15-3. books.py: the BookDict definition.*

```
from typing import TypedDict
import json
class BookDict(TypedDict):
 isbn: str
 title: str
 authors: list[str]
 pagecount: int
```

At first glance, typing.TypedDict may seem like a data class builder, similar to typing.NamedTuple—covered in [Chapter 5](010-chapter-5-data-class-builders.md#page-265-0).

The syntactic similarity is misleading. TypedDict is very different. It exists only for the benefit of type checkers, and has no runtime effect.

TypedDict provides two things:

- 1. Class-like syntax to annotate a dict with type hints for the value of each "field".
- 2. A constructor that tells the type checker to expect a dict with the keys and values as specified.

At runtime, a TypedDict constructor such as BookDict is placebo: it has the same effect as calling the dict constructor with the same arguments.

The fact that BookDict creates a plain dict also means that:

- The "fields" in the pseudo-class definition don't create instance attributes.
- You can't write initializers with default values for the "fields".
- Method definitions are not allowed.

Let's explore the behavior of a BookDict at runtime.

*Example 15-4. Using a BookDict, but not quite as intended.*

```
>>> from books import BookDict
>>> pp = BookDict(title='Programming Pearls', 
... authors='Jon Bentley', 
... isbn='0201657880',
```

```
... pagecount=256)
>>> pp 
{'title': 'Programming Pearls', 'authors': 'Jon Bentley', 'isbn':
'0201657880',
 'pagecount': 256}
>>> type(pp)
<class 'dict'>
>>> pp.title 
Traceback (most recent call last):
 File "<stdin>", line 1, in <module>
AttributeError: 'dict' object has no attribute 'title'
>>> pp['title']
'Programming Pearls'
>>> BookDict.__annotations__ 
{'isbn': <class 'str'>, 'title': <class 'str'>, 'authors':
typing.List[str],
 'pagecount': <class 'int'>}
```

- You can call BookDict like a dict constructor with keyword arguments, or passing a dict argument—including a dict literal.
- Ooops… I forgot authors takes a list. But gradual typing means no type checking at runtime.
- The result of calling BookDict is a plain dict…
- … therefore you can't read the data using object.field notation.
- The type hints are in BookDict.\_\_annotations\_\_, and not in pp.

Without a type checker, TypedDict is as useful as comments: it may help people read the code, but that's it. In contrast, the class builders from [Chapter 5](010-chapter-5-data-class-builders.md#page-265-0) are useful even if you don't use a type checker because at runtime they generate or enhance a custom class that you can instantiate. They also provide several useful methods or functions listed in [Table 5-1](010-chapter-5-data-class-builders.md#page-271-0).

[Example 15-5](#page-750-0) builds a valid BookDict and tries some operations on it. This shows how TypedDict enables Mypy to catch errors, shown in [Example 15-6](#page-751-0).

<span id="page-750-0"></span>
## Example 15-5. demo\_books.py: legal and ilegal operations on a BookDict.

```
from books import BookDict
from typing import TYPE_CHECKING
def demo() -> None: 
 book = BookDict( 
 isbn='0134757599',
 title='Refactoring, 2e',
 authors=['Martin Fowler', 'Kent Beck'],
 pagecount=478
 )
 authors = book['authors']
 if TYPE_CHECKING: 
 reveal_type(authors) 
 authors = 'Bob' 
 book['weight'] = 4.2
 del book['title']
if __name__ == '__main__':
 demo()
```

- Remember to add a return type, so that Mypy doesn't ignore the function.
- This is a valid BookDict: all the keys are present, with values of the correct types.
- Mypy will infer the type of authors from the annotation for the 'authors' key in BookDict.
- typing.TYPE\_CHECKING is only True when the program is being type checked. At runtime, it's always false.
- The previous if statement prevents reveal\_type(authors) from being called at runtime. reveal\_type is not a runtime Python function, but a debugging facility provided by Mypy. That's why there is no import for it. See its output in [Example 15-6](#page-751-0).

The last three lines of the demo function are illegal. They will cause error messages in [Example 15-6](#page-751-0).

Type checking demo\_books.py from [Example 15-5](#page-750-0), this is what we get:

<span id="page-751-0"></span>
## Example 15-6. Type checking demo\_books.py.

```
…/typeddict/ $ mypy demo_books.py
demo_books.py:13: note: Revealed type is 'built-ins.list[built-
ins.str]' 
demo_books.py:14: error: Incompatible types in assignment
 (expression has type "str", variable has type
"List[str]") 
demo_books.py:15: error: TypedDict "BookDict" has no key 'weight' 
demo_books.py:16: error: Key 'title' of TypedDict "BookDict" cannot
be deleted 
Found 3 errors in 1 file (checked 1 source file)
```

- This note is the result of reveal\_type(authors).
- The type of the authors variable was inferred from the type of the book['authors'] expression that initialized it. You can't assign a str to a variable of type List[str]. Type checkers usually don't allow the type of a variable to change. [3](#page-795-2)
- <span id="page-751-1"></span>Cannot assign to a key that is not part of the BookDict definition.
- Cannot delete a key that is part of the BookDict definition.

Now let's see BookDict used in function signatures, to type check function calls.

Imagine you need to generate XML from book records, similar to this:

```
<BOOK>
 <ISBN>0134757599</ISBN>
 <TITLE>Refactoring, 2e</TITLE>
 <AUTHOR>Martin Fowler</AUTHOR>
 <AUTHOR>Kent Beck</AUTHOR>
```

```
 <PAGECOUNT>478</PAGECOUNT>
</BOOK>
```

If you were writing MicroPython code to embed in a tiny microcontroller, you might write a function like this: [4](#page-795-3)

<span id="page-752-0"></span>*Example 15-7. books.py: to\_xml function.*

```
AUTHOR_EL = '<AUTHOR>{}</AUTHOR>'
def to_xml(book: BookDict) -> str: 
 elements: list[str] = [] 
 for key, value in book.items():
 if isinstance(value, list): 
 elements.extend(
 AUTHOR_EL.format(n) for n in value) 
 else:
 tag = key.upper()
 elements.append(f'<{tag}>{value}</{tag}>')
 xml = '\n\t'.join(elements)
 return f'<BOOK>\n\t{xml}\n</BOOK>'
```

- The whole point of the example: using BookDict in the function signature.
- It's often necessary to annotate collections that start empty, otherwise Mypy can't infer the type of the elements. [5](#page-795-4)
- <span id="page-752-2"></span>Mypy understands isinstance checks, and treats value as a list in this block.
- When I used key == 'authors' as the condition for the if guarding this block, Mypy found an error in this line: "object" has no attribute "\_\_iter\_\_", because it inferred the type of value returned from book.items() as object, which doesn't support the \_\_iter\_\_ method required by the generator expression. With the isinstance check, this works because Mypy knows that value is a list in this block.

Here is a function that parses a JSON str and returns a BookDict:

<span id="page-753-0"></span>
## Example 15-8. books\_any.py: from\_json function.

```
def from_json(data: str) -> BookDict:
 whatever = json.loads(data) 
 return whatever
```

- <span id="page-753-2"></span>The return type of json.loads() is Any. [6](#page-795-5)
- I can return whatever—of type Any—because Any is *consistent-with* every type, including the declared return type, BookDict.

The second point of [Example 15-8](#page-753-0) is very important to keep in mind: Mypy will not flag any problem in this code, but at runtime the value in whatever may not conform to the BookDict structure—in fact, it may not be a dict at all!

If you run Mypy with --disallow-any-expr it will complain about the two lines in the body of from\_json:

```
…/typeddict/ $ mypy books_any.py --disallow-any-expr
books_any.py:30: error: Expression has type "Any"
books_any.py:31: error: Expression has type "Any"
Found 2 errors in 1 file (checked 1 source file)
```

In this case, the type error can be silenced by adding a type hint to the initialization of the whatever variable, as in [Example 15-9](#page-753-1):

<span id="page-753-1"></span>*Example 15-9. books.py: from\_json function with variable annotation.*

```
def from_json(data: str) -> BookDict:
 whatever: BookDict = json.loads(data) 
 return whatever
```

- --disallow-any-expr does not cause errors when an expression of type Any is immediately assigned to a variable with a type hint.
- Now whatever is of type BookDict, the declared return type.

## WARNING

Don't be lulled into a false sense of type safety by [Example 15-9!](#page-753-1) Looking at the code at rest, the type checker cannot predict that json.loads() will return anything that resembles a BookDict. Only runtime validation can guarantee that.

Static type checking is unable to prevent errors with code that is inherently dynamic, such as json.loads(), which builds a Python objects of different types at runtime. [Example 15-10](#page-754-0), [Example 15-11,](#page-755-0) and [Example 15-12](#page-756-0) demonstrate.

<span id="page-754-0"></span>*Example 15-10. demo\_not\_book.py: from\_json returns an invalid BookDict, and to\_xml accepts it.*

```
from books import to_xml, from_json
from typing import TYPE_CHECKING
def demo() -> None:
 NOT_BOOK_JSON = """
 {"title": "Andromeda Strain",
 "flavor": "pistachio",
 "authors": true}
 """
 not_book = from_json(NOT_BOOK_JSON) 
 if TYPE_CHECKING: 
 reveal_type(not_book)
 reveal_type(not_book['authors'])
 print(not_book) 
 print(not_book['flavor']) 
 xml = to_xml(not_book) 
 print(xml) 
if __name__ == '__main__':
 demo()
```

- This line does not produce a valid BookDict—see the content of NOT\_BOOK\_JSON.
- Let's have Mypy reveal a couple of types.

- This should not be a problem: print can handle object and every other type.
- BookDict has no 'flavor' key, but the JSON source does… what will happen?
- Remember the signature: def to\_xml(book: BookDict) -> str:
- How will the XML output look like?

Checking demo\_not\_book.py with Mypy:

<span id="page-755-0"></span>*Example 15-11. Mypy report for demo\_not\_book.py, reformatted for clarity.*

```
…/typeddict/ $ mypy demo_not_book.py
demo_not_book.py:12: note: Revealed type is
 'TypedDict('books.BookDict', {'isbn': built-ins.str,
 'title': built-ins.str,
 'authors': built-ins.list[built-
ins.str],
 'pagecount': built-ins.int})' 
demo_not_book.py:13: note: Revealed type is 'built-ins.list[built-
ins.str]' 
demo_not_book.py:16: error: TypedDict "BookDict" has no key
'flavor' 
Found 1 error in 1 file (checked 1 source file)
```

- The revealed type is the nominal type, not the runtime content of not\_book.
- Again, this is the nominal type of not\_book['authors'], as defined in BookDict. Not the runtime type.
- This error is for line print(not\_book['flavor']): that key does not exist in the nominal type.

Now let's run demo\_not\_book.py.

<span id="page-756-0"></span>
## Example 15-12. Output of running demo\_not\_book.py.

```
…/typeddict/ $ python3 demo_not_book.py
{'title': 'Andromeda Strain', 'flavor': 'pistachio', 'authors':
True} 
pistachio 
<BOOK> 
 <TITLE>Andromeda Strain</TITLE>
 <FLAVOR>pistachio</FLAVOR>
 <AUTHORS>True</AUTHORS>
</BOOK>
```

- This is not really a BookDict.
- The value of not\_book['flavor'].
- to\_xml takes a BookDict argument, but there is no runtime checking: garbage in, garbage out.

[Example 15-12](#page-756-0) shows that demo\_not\_book.py outputs nonsense, but has no runtime errors. Using a TypedDict while handling JSON data did not provide much type safety.

If you look at the code for to\_xml in [Example 15-7](#page-752-0) through the lens of duck typing, the argument book must provide an .items() method that returns an iterable of tuples like (key, value) where:

- key must have an .upper() method;
- value can be anything.

The point of this demonstration: when handling data with a dynamic structure, such as JSON or XML, TypedDict is absolutely not a replacement for data validation at runtime. For that, use [pydantic](https://pypi.org/project/pydantic/).

TypedDict has more features, including support for optional keys, a limited form of inheritance, and an alternative declaration syntax. If you [want to know more about it, please review](https://www.python.org/dev/peps/pep-0589/) *PEP 589\_TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys*.

Now let's turn our attention to a function that is best avoided, but sometimes is unavoidable: typing.cast.

<span id="page-757-0"></span>
## Type Casting

No type system is perfect, and neither are the static type checkers, the type hints in the *typeshed* project, or the type hints in the third-party packages that have them.

The typing.cast() special function provides one way to handle type checking malfunctions or incorrect type hints in code we can't fix. The [Mypy documentation](https://mypy.readthedocs.io/en/stable/casts.html) explains:

*Casts are used to silence spurious type checker warnings and give the type checker a little help when it can't quite understand what is going on.*

At runtime, typing.cast does absolutely nothing. This is its [implementation](https://github.com/python/cpython/blob/bee66d3cb98e740f9d8057eb7f503122052ca5d8/Lib/typing.py#L1340):

```
def cast(typ, val):
 """Cast a value to a type.
 This returns the value unchanged. To the type checker this
 signals that the return value has the designated type, but at
 runtime we intentionally don't check anything (we want this
 to be as fast as possible).
 """
 return val
```

PEP 484 requires type checkers to "blindly believe" the type stated in the cast. The [Casts](https://www.python.org/dev/peps/pep-0484/#casts) section of PEP 484 gives an example where the type checker needs the guidance of cast::

```
from typing import cast
def find_first_str(a: list[object]) -> str:
 index = next(i for i, x in enumerate(a) if isinstance(x,
str))
 # We only get here if there's at least one string in a
 return cast(str, a[index])
```

The next() call on the generator expression will either return the index of a str item or raise StopIteration. Therefore, find\_first\_str will always return a str if no exception is raised, and str is the declared return type.

<span id="page-758-0"></span>But if the last line were just return a[index], Mypy would infer the return type as object because the a argument is declared as list[object]. So the cast() is required to guide Mypy. [7](#page-795-6)

Here is another example with cast, this time to correct an outdated type hint for Python's standard library. In [Example 22-12,](029-chapter-22-asynchronous-programming.md#page-1164-0) I create an *asyncio* Server object and I want to get the address the server is listening to. I coded this line:

```
addr = server.sockets[0].getsockname()
```

But Mypy reported this error:

```
Value of type "Optional[List[socket]]" is not indexable
```

The type hint for Server.sockets on *typeshed* in May 2021 is valid for Python 3.6, where the sockets attribute could be None. But in Python 3.7 sockets became a property with a getter that always returns a list —which may be empty if the server has no sockets. And since Python 3.8 the getter returns a tuple (used as an immutable sequence).

Since I can't fix *typeshed* right now I added a cast, like this: [8](#page-796-0)

```
from asyncio.trsock import TransportSocket
from typing import cast
# ... many lines omitted ...
 socket_list = cast(tuple[TransportSocket, ...],
server.sockets)
 addr = socket_list[0].getsockname()
```

Using cast in this case required a couple of hours to understand the problem and read *asyncio* source code to find the correct type of the sockets: the TransportSocket class from the undocumented asyncio.trsock module. I also had to add two import statements and another line of code for readability. But the code is safer. [9](#page-796-1)

The careful reader may note that sockets[0] could raise IndexError if sockets is empty. However, as far as I understand asyncio, that cannot happen in [Example 22-12](029-chapter-22-asynchronous-programming.md#page-1164-0) because the server is ready to accept connections by the time I read its sockets attribute, therefore it will not be empty. Anyway, IndexError is a runtime error. Mypy can't spot the problem even in a trivial case like print([][0]).

<span id="page-759-0"></span>
## WARNING

Don't get too comfortable using cast to silence Mypy, because Mypy is usually right when it reports an error. If you are using cast very often, that's a [code smell](https://en.wikipedia.org/wiki/Code_smell). Your team may be misusing type hints, or you may have low quality dependencies in your codebase.

Despite the downsides, there are valid uses for cast. Here is something Guido van Rossum wrote about it:

<span id="page-759-1"></span>*What's wrong with the occasional cast() call or # type: ignore comment? [10](#page-796-2)*

It is unwise to completely ban the use of cast, especially because the other workarounds are worse:

- <span id="page-759-2"></span># type: ignore is less informative; . [11](#page-796-3)
- Using Any is contagious: since Any is *consistent-with* all types, abusing it may produce cascading effects through type inference, undermining the type checker's ability to detect errors in other parts of the code.

Of course, not all typing mishaps can be fixed with cast. Sometimes we need # type: ignore, the occasional Any, or even leaving a function without type hints.

Next, let's talk about using annotations at runtime.

<span id="page-760-1"></span>
## Reading Type Hints at Runtime

At import time, Python reads the type hints in functions, classes and modules and stores them in attributes named \_\_annotations\_\_. For example, Example 15-13 is an annotated signature of [Link to Come].

```
Example 15-13. Annotated clip function
```

```
def clip(text: str, max_len: int = 80) -> str:
```

The type hints are stored as a dict in the \_\_annotations\_\_ attribute of the function:

```
>>> from clip_annot import clip
>>> clip.__annotations__
{'text': <class 'str'>, 'max_len': <class 'int'>, 'return':
<class 'str'>}
```

The 'return' key maps to the return type hint after the -> symbol in Example 15-13.

Note that the annotations are evaluated by the interpreter. That's why the values in the annotations are the Python classes str and int, and not the strings 'str' and 'int'. The import time evaluation of annotations is the standard in Python 3.9 and even in Python 3.10 (unreleased as of May, 2021), and it is the behavior described in [PEP 3107](https://www.python.org/dev/peps/pep-3107/) when the syntax for annotations was introduced way back in 2006.

<span id="page-760-0"></span>
## Problems with Annotations at Runtime

The increased use of type hints raised two problems:

- Importing modules uses more CPU and memory when many type hints are used.
- Referring to types not yet defined requires using strings instead of actual types.

Both issues are relevant. The first is self-explanatory at a high level. The root causes at a lower level are beyond the scope of this book. Let's focus on the second issue.

The second issue is often described as the "forward reference" problem, but one of its common manifestations in source code doesn't look like a forward reference at all: that's when a method returns a new object of the same class. Since the class object is not defined until Python completely evaluates the class body, type hints must use the name of the class as a string. Here is an example:

```
class Rectangle:
 # ... lines omitted ...
 def stretch(self, factor: float) -> 'Rectangle'
 return Rectangle(width=self.width * factor)
```

Writing forward referencing type hints as strings is the standard and required practice as of Python 3.10. Static type checkers were designed to deal with that issue from the beginning.

But at runtime, if you write code to read the return annotation for stretch, you will get a string 'Rectangle' instead of a reference to the actual type, the Rectangle class. Now your code needs to figure out what that string means.

The typing module includes three functions and a class categorized as [Introspection helpers](https://docs.python.org/3/library/typing.html#introspection-helpers), the most important being typing.get\_type\_hints. Part of its documentation states: *get\_type\_hints(obj, globals=None, locals=None, include\_extras=False)*

[…] This is often the same as obj.\_\_annotations\_\_. In addition, forward references encoded as string literals are handled by evaluating them in globals and locals namespaces. […]

That sounds great, but get\_type\_hints can't handle all cases, as we'll see.

[PEP 563—Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/) was approved to make it unnecessary to write annotations as strings, and to reduce the runtime costs of type hints. Its main idea is described in these two periods of the *[Abstract](https://www.python.org/dev/peps/pep-0563/#abstract)*:

*This PEP proposes changing function annotations and variable annotations so that they are no longer evaluated at function definition time. Instead, they are preserved in annotations in string form.*

Beginning with Python 3.7, that's how annotations are handled in any module that starts with this import statement:

```
from __future__ import annotations
```

To demonstrate its effect, I put a copy of the same clip function mentioned before in a *clip\_annot\_post.py* module with that \_\_future\_\_ import at the top.

At the console, here's what I get when you import that module and read the annotations from clip:

```
>>> from clip_annot_post import clip
>>> clip.__annotations__
{'text': 'str', 'max_len': 'int', 'return': 'str'}
```

As you can see, all the type hints are now plain strings, despite the fact they are not written as quoted strings in the definition of clip (Example 15-13\).

The typing.get\_type\_hints function is able to resolve many type hints, including those in clip:

```
>>> from clip_annot_post import clip
>>> from typing import get_type_hints
>>> get_type_hints(clip)
{'text': <class 'str'>, 'max_len': <class 'int'>, 'return':
<class 'str'>}
```

Calling get\_type\_hints gives us the real types—even in some cases where the original type hint is written as a quoted string. That's the recommended way to read type hints at runtime.

The PEP 563 behavior was scheduled to become default in Python 3.10 with no \_\_future\_\_ import needed. However, the maintainers of *FastAPI* and *pydantic* raised the alarm that the change would break their code which relies on type hints at runtime, and cannot use get\_type\_hints reliably.

In the ensuing discussion on the *python-dev* mailing list, Łukasz Langa the author of PEP 563—described some limitations of that function:

*[…] it turned out that typing.get\_type\_hints() has limits that make its use in general costly at runtime, and more importantly insufficient to resolve all types. The most common example deals with non-global context in which types are generated (e.g. inner classes, classes within functions, etc.). But one of the crown examples of forward references: classes with methods accepting or returning objects of their own type, also isn't properly handled by*

<span id="page-763-0"></span>*typing.get\_type\_hints() if a class generator is used. There's some trickery we can do to connect the dots but in general it's not great. [12](#page-796-4)*

Python's Steering Council decided to postpone making PEP 563 the default behavior until Python 3.11 or later, giving more time to developers to come up with a solution that addresses the issues PEP 563 tried to solve, without [breaking widespread uses of type hints at runtime. PEP 649—Deferred](https://www.python.org/dev/peps/pep-0649/) Evaluation Of Annotations Using Descriptors is under consideration as a possible solution, but a different compromise may be reached.

To summarize: reading type hints at runtime is not 100% reliable as of Python 3.10 and is likely to change in 2022.

<span id="page-764-1"></span>
## Dealing with the Problem

Giving the present situation, I recommend:

- 1. Avoid reading \_\_annotations\_\_ directly; use typing.get\_type\_hints instead.
- 2. Wrap any calls to typing.get\_type\_hints in a function of your own, so that future changes that may be required are localized.

To demonstrate the second point, here are the first lines of the Checked class defined in [Example 25-5,](032-chapter-25-class-metaprogramming.md#page-1309-0) which we'll study in [Chapter 25.](032-chapter-25-class-metaprogramming.md#page-1296-0)

```
class Checked:
 @classmethod
 def _fields(cls) -> dict[str, type]:
 return get_type_hints(cls)
 # ... more lines ...
```

The Checked.\_fields class method protects other parts of the module from depending directly on typing.get\_type\_hints. If get\_type\_hints changes in the future, I can add logic to Checked.\_fields to work around eventual issues, hopefully avoiding changes elsewhere in my code.

The remaining sections of this chapter cover generics, starting with how to define a generic class that can be parameterized by its users.

<span id="page-764-0"></span>
## Implementing a generic class

In [Example 13-7](020-chapter-13-interfaces-protocols-and-abcs.md#page-656-0) we defined the Tombola ABC: an interface for classes that work like a bingo cage. The LottoBlower class from [Example 13-10](020-chapter-13-interfaces-protocols-and-abcs.md#page-663-0) is a concrete implementation. Now we'll study a generic version of LottoBlower used like this:

*Example 15-14. generic\_lotto\_demo.py: using a generic lottery blower class*

```
from generic_lotto import LottoBlower
machine = LottoBlower[int](range(1, 11)) 
first = machine.pick() 
remain = machine.inspect()
```

- To instantiate a generic class we give it a actual type parameter, like int here.
- Mypy will correctly infer that first is an int…
- … and that remain is a tuple of integers.

In addition, Mypy reports violations of the parameterized type with helpful messages, such as these:

*Example 15-15. generic\_lotto\_errors.py: errors reported by Mypy*

```
from generic_lotto import LottoBlower
machine = LottoBlower[int]([1, .2])
## error: List item 1 has incompatible type "float"; 
## expected "int"
machine = LottoBlower[int](range(1, 11))
machine.load('ABC')
## error: Argument 1 to "load" of "LottoBlower" 
## has incompatible type "str";
## expected "Iterable[int]"
## note: Following member(s) of "str" have conflicts:
## note: Expected:
## note: def __iter__(self) -> Iterator[int]
## note: Got:
## note: def __iter__(self) -> Iterator[str]
```

- Upon instantiation of LottoBlower[int], Mypy flags the float.
- When calling .load('ABC'), Mypy explains why a str won't do: str.\_\_iter\_\_ returns an Iterator[str], but LottoBlower[int] requires an Iterator[int].

[Example 15-16](#page-766-0) is the implementation.

<span id="page-766-0"></span>*Example 15-16. generic\_lotto.py: a generic lottery blower class*

```
import random
from collections.abc import Iterable
from typing import TypeVar, Generic
from tombola import Tombola
T = TypeVar('T')
class LottoBlower(Tombola, Generic[T]): 
 def __init__(self, items: Iterable[T]) -> None: 
 self._balls = list[T](items)
 def load(self, items: Iterable[T]) -> None: 
 self._balls.extend(items)
 def pick(self) -> T: 
 try:
 position = random.randrange(len(self._balls))
 except ValueError:
 raise LookupError('pick from empty LottoBlower')
 return self._balls.pop(position)
 def loaded(self) -> bool: 
 return bool(self._balls)
 def inspect(self) -> tuple[T, ...]: 
 return tuple(self._balls)
```

Generic class declarations often use multiple inheritance, because we need to subclass Generic to declare the formal type parameters—in this case, T.

- The items argument in \_\_init\_\_ is of type Iterable[T], which becomes Iterable[int] when an instance is declared as LottoBlower[int].
- The load method is likewise constrained.
- The return type of T now becomes int in a LottoBlower[int].
- No type variable here.
- Finally, T sets the type of the items in the returned tuple.

<span id="page-767-0"></span>
## TIP

The *[User-defined generic types](https://docs.python.org/3/library/typing.html#user-defined-generic-types)* section of the typing module documentation is short, presents good examples, and provides a few more details that I do not cover here.

Now that we've seen how to implement a generic class, let's define the terminology to talk about generics.

<span id="page-767-1"></span>
## Basic Jargon for Generic Types

Here are a few definitions that I found useful when studying generics. *Generic type* [13](#page-796-5)

A type declared with one or more type variables. Examples: LottoBlower[T], abc.Mapping[KT, VT].

## Formal type parameter

The type variables that appear in a generic type declaration. Example: T, KT, and VT in the generic type examples above.

## Parameterized type

```
A type declared with actual type parameters.
Examples: list[int], abc.Mapping[str, float].
```

*Actual type parameter*

The actual types given as parameters when a parameterized type is declared.

Example: the int in LottoBlower[int].

The next topic is about how to make generic types more flexible, introducing the concepts of covariance, contravariance, and invariance.

<span id="page-768-0"></span>
## Variance

The interaction of generics and a type hierarchy introduces a new typing concept: variance. We will approach this abstract concept through an analogy. Imagine that a school cafeteria has a rule that only juice dispensers can be installed. General beverage dispensers are not allowed because they may serve sodas, which are banned by the school board. [14](#page-796-6)

<span id="page-768-3"></span>
<span id="page-768-2"></span>
## An Invariant Dispenser

Let's try to model the cafeteria scenario with a generic BeverageDispenser class that can be parameterized on the type of beverage. See [Example 15-17](#page-768-1).

<span id="page-768-1"></span>*Example 15-17. invariant.py: type definitions and install function.* **from typing import** TypeVar, Generic

```
class Beverage: 
 """Any beverage."""
class Juice(Beverage):
 """Any fruit juice."""
class OrangeJuice(Juice):
 """Delicious juice from Brazilian oranges."""
```

```
T = TypeVar('T') 
class BeverageDispenser(Generic[T]): 
 """A dispenser parameterized on the beverage type."""
 def __init__(self, beverage: T) -> None:
 self.beverage = beverage
 def dispense(self) -> T:
 return self.beverage
def install(dispenser: BeverageDispenser[Juice]) -> None: 
 """Install a fruit juice dispenser."""
```

- Beverage, Juice and OrangeJuice form a type hierarchy.
- Simple TypeVar declaration.
- BeverageDispenser is parameterized on the type of beverage.
- install is a module-global function. Its type hint enforces the rule that only a juice dispenser is acceptable.

Given the definitions in [Example 15-17,](#page-768-1) the following code is legal:

```
juice_dispenser = BeverageDispenser(Juice())
install(juice_dispenser)
```

However, this is not legal:

```
beverage_dispenser = BeverageDispenser(Beverage())
install(beverage_dispenser)
## mypy: Argument 1 to "install" has
## incompatible type "BeverageDispenser[Beverage]"
## expected "BeverageDispenser[Juice]"
```

A dispenser that serves any Beverage is not acceptable because the cafeteria requires a dispenser that is specialized for Juice.

Somewhat surprisingly, this code is also illegal:

```
orange_juice_dispenser = BeverageDispenser(OrangeJuice())
install(orange_juice_dispenser)
## mypy: Argument 1 to "install" has
## incompatible type "BeverageDispenser[OrangeJuice]"
## expected "BeverageDispenser[Juice]"
```

A dispenser specialized for OrangeJuice is not allowed either. Only BeverageDispenser[Juice] will do. In the typing jargon, this means that the BeverageDispenser generic class is invariant.

Python mutable collection types—such as list and set—are invariant. The LottoBlower class from [Example 15-16](#page-766-0) is also invariant.

<span id="page-770-0"></span>
## A Covariant Dispenser

If we want to be more flexible and model dispensers as a generic class that can accept some beverage type and also its subtypes, we must make it covariant. This is how we'd declare BeverageDispenser:

*Example 15-18. covariant.py: type definitions and install function.*

```
T_co = TypeVar('T_co', covariant=True) 
class BeverageDispenser(Generic[T_co]): 
 def __init__(self, beverage: T_co) -> None:
 self.beverage = beverage
 def dispense(self) -> T_co:
 return self.beverage
def install(dispenser: BeverageDispenser[Juice]) -> None: 
 """Install a fruit juice dispenser."""
```

- Set covariant=True when declaring the type variable; \_co is a conventional suffix for covariant type parameters on *typeshed*.
- Use T\_co to parameterize the Generic special class.
- Type hints for install are the same as in [Example 15-17](#page-768-1).

The following code works because now both the Juice dispenser and the OrangeJuice dispenser are valid in a covariant BeverageDispenser.

```
juice_dispenser = BeverageDispenser(Juice())
install(juice_dispenser)
orange_juice_dispenser = BeverageDispenser(OrangeJuice())
install(orange_juice_dispenser)
```

But a dispenser for any Beverage is not acceptable:

```
beverage_dispenser = BeverageDispenser(Beverage())
install(beverage_dispenser)
## mypy: Argument 1 to "install" has
## incompatible type "BeverageDispenser[Beverage]"
## expected "BeverageDispenser[Juice]"
```

That's covariance: the subtype relationship of the parameterized dispensers varies in the same direction of the subtype relationship of the type parameters.

<span id="page-771-0"></span>
## A Contravariant Trash Can

Now we'll model the cafeteria rule for deploying a trash can. Let's assume food and drinks are served in biodegradable packages, and leftovers as well as single-use utensils are also biodegradable. The trash cans must be suitable for biodegradable refuse.

This code models the cafeteria trash can rule:

*Example 15-19. contravariant.py: type definitions and install function.*

```
from typing import TypeVar, Generic
class Refuse: 
 """Any refuse."""
class Biodegradable(Refuse):
 """Biodegradable refuse."""
```

```
class Compostable(Biodegradable):
 """Compostable refuse."""
T_contra = TypeVar('T_contra', contravariant=True) 
class TrashCan(Generic[T_contra]): 
 def put(self, refuse: T_contra) -> None:
 """Store trash until dumped."""
def deploy(trash_can: TrashCan[Biodegradable]):
 """Deploy a trash can for biodegradable refuse."""
```

- A type hierarchy for refuse: Refuse is the most general type, Compostable is the most specific.
- T\_contra is a conventional name for a contravariant type variable.
- TrashCan is contravariant on the type of refuse.

Given those definitions, these types of trash cans are acceptable:

```
bio_can: TrashCan[Biodegradable] = TrashCan()
deploy(bio_can)
trash_can: TrashCan[Refuse] = TrashCan()
deploy(trash_can)
```

The more general TrashCan[Refuse] is acceptable because it can take any kind of refuse, including Biodegradable and Compostable.

However, a TrashCan[Compostable] won't do, because it is cannot take Biodegradable or general Trash:

```
compost_can: TrashCan[Compostable] = TrashCan()
deploy(compost_can)
## mypy: Argument 1 to "deploy" has
## incompatible type "TrashCan[Compostable]"
## expected "TrashCan[Biodegradable]"
```

Let's summarize the concepts we just saw.

<span id="page-773-1"></span>
## Variance Review

## Invariant Types

A generic type L is invariant when there is no supertype or subtype relationship between two parameterized types, regardless of the relationship that may exist between the actual parameters. In other words, if L is invariant, then L[A] is not a supertype or a subtype of L[B]. They are inconsistent in both ways.

As mentioned, Python's mutable collections are invariant by default. The list type is a good example: list[int] is not *consistent-with* list[float] and vice-versa.

In general, if a formal type parameter appears in type hints of method arguments and the same parameter appears in method return types, that parameter must be invariant to ensure type safety when updating and reading from the collection.

For example, here is part of the type hints for the list built-in on *[typeshed](https://github.com/python/typeshed/blob/bfc83c365a0b26ab16586beac77ff16729d0e473/stdlib/builtins.pyi#L743)*:

```
class list(MutableSequence[_T], Generic[_T]):
 @overload
 def __init__(self) -> None: ...
 @overload
 def __init__(self, iterable: Iterable[_T]) -> None: ...
 # ... lines omitted ...
 def append(self, __object: _T) -> None: ...
 def extend(self, __iterable: Iterable[_T]) -> None: ...
 def pop(self, __index: int = ...) -> _T: ...
 # etc...
```

Note that \_T appears in the arguments of \_\_init\_\_, append, and extend and as the return type of pop. There is no way to make such a class type safe if it is covariant or contravariant in \_T.

<span id="page-773-0"></span>
## Covariant Types

Consider two types A and B where B is *consistent-with* A, and neither of them is Any. Some authors use the <: and :> symbols to denote type relationships like this:

*A :> B*

A is a supertype or the same as B.

*B <: A*

B is a subtype or the same as A.

Given A :> B, a generic type C is covariant when C[A] :> C[B].

Note the direction of the :> symbol is the same in both cases where A is to the left of B. Covariant generic types follow the subtype relationship of the actual type parameters.

Immutable containers can be covariant. For example, this how the typing.FrozenSet class is [documented](https://docs.python.org/3.9/library/typing.html#typing.FrozenSet) as a covariant with a type variable using the conventional name T\_co:

```
class FrozenSet(frozenset, AbstractSet[T_co]):
```

Applying the :> notation to parameterized types, we have:

```
 float :> int
frozenset[float] :> frozenset[int]
```

Iterators are another example of covariant generics: they are not read-only collections like a frozenset, but they only produce output. Any code expecting an abc.Iterator[float] yielding floats can safely use an abc.Iterator[int] yielding integers.

<span id="page-774-0"></span>
## Contravariant Types

Given A :> B, a generic type K is contravariant if K[A] <: K[B].

Contravariant generic types reverse the subtype relationship of the actual type parameters.

The TrashCan class exemplifies this:

```
 Refuse :> Biodegradable
TrashCan[Refuse] <: TrashCan[Biodegradable]
```

A contravariant container is usually a write-only data structure, also known as a "sink".

There are no examples of contravariant generics with a single formal type parameter in the Python 3.9 standard library. But [Generator](https://docs.python.org/3.9/library/typing.html#typing.Generator), [Coroutine](https://docs.python.org/3.9/library/typing.html#typing.Coroutine), and [AsyncGenerator](https://docs.python.org/3.9/library/typing.html#typing.AsyncGenerator) all have multiple formal type parameters, and each of them has one contravariant formal parameter.

Those three generic types are all related to generator-like constructs used as coroutines—as opposed to simple iterators. The Generator type appears in [Chapter 19;](026-chapter-19-classic-coroutines.md#page-953-0) Coroutine and AsyncGenerator, in [Chapter 22.](029-chapter-22-asynchronous-programming.md#page-1122-0)

For the present discussion about variance, the main point is that the contravariant formal parameter defines the type of the only argument used to send data to the object, while a different covariant formal parameter defines the type of outputs produced by the object—the yield type. The precise meanings of "send" and "yield" are explained in [Chapter 19.](026-chapter-19-classic-coroutines.md#page-953-0)

We can derive useful guidelines from these observations of covariant outputs and contravariant inputs.

<span id="page-775-0"></span>
## Variance Rules of Thumb

- 1. If a formal type parameter defines a type for data that comes out of the object, it can be covariant.
- 2. If a formal type parameter defines a type for data that goes into the object after its initial construction, it can be contravariant.
- 3. If a formal type parameter defines a type for data that comes out of the object and the same parameter defines a type for data that goes

into it, it must be invariant.

4. To err on the safe side, make formal parameters invariant.

By default, TypeVar creates formal parameters that are invariant, and that's how the mutable collections in the standard library are annotated.

The generic typing.Generator is a great example of rules #1 and #2, as long as you understand how classic coroutines work—because that's what that type describes. After [Chapter 19](026-chapter-19-classic-coroutines.md#page-953-0) covers classic coroutines in depth, ["Generic Type Hints for Classic Coroutines"](026-chapter-19-classic-coroutines.md#page-1005-0) continues the present discussion about variance.

Next, let's see how to define generic static protocols, applying the idea of covariance to a couple of new examples.

<span id="page-776-0"></span>
## Implementing a generic static protocol

The Python 3.9 standard library provides a couple of generic static protocols. One of them is SupportsAbs[, implemented like this in the](https://github.com/python/cpython/blob/46b16d0bdbb1722daed10389e27226a2370f1635/Lib/typing.py#L1786) *typing* module:

```
@runtime_checkable
class SupportsAbs(Protocol[T_co]):
 """An ABC with one abstract method __abs__ that is covariant
in its return type."""
 __slots__ = ()
 @abstractmethod
 def __abs__(self) -> T_co:
 pass
```

T\_co is declared according to the naming convention:

```
T_co = TypeVar('T_co', covariant=True)
```

Thanks to SupportsAbs, Mypy recognizes this code as valid:

## Example 15-20. abs\_demo.py: use of the generic SupportsAbs protocol.

```
#!/usr/bin/env python3
import math
from typing import NamedTuple, SupportsAbs
class Vector2d(NamedTuple):
 x: float
 y: float
 def __abs__(self) -> float: 
 return math.hypot(self.x, self.y)
def is_unit(v: SupportsAbs[float]) -> bool: 
 """'True' if the magnitude of 'v' is close to 1."""
 return math.isclose(abs(v), 1.0) 
assert issubclass(Vector2d, SupportsAbs) 
v0 = Vector2d(0, 1) 
sqrt2 = math.sqrt(2)
v1 = Vector2d(sqrt2 / 2, sqrt2 / 2)
v2 = Vector2d(1, 1)
v3 = complex(.5, math.sqrt(3) / 2)
v4 = 1 
assert is_unit(v0)
assert is_unit(v1)
assert not is_unit(v2)
assert is_unit(v3)
assert is_unit(v4)
print('OK')
```

- Defining \_\_abs\_\_ makes Vector2d *consistent-with* SupportsAbs.
- Parameterizing SupportsAbs with float ensures…
- …that Mypy accepts abs(v) as the first argument for math.isclose.

- Thanks to @runtime\_checkable in the definition of SupportsAbs, this is a valid runtime assertion.
- The remaining code all passes Mypy checks and runtime assertions.
- The int type is also *consistent-with* SupportsAbs. According to *[typeshed](https://github.com/python/typeshed/blob/2a9f081abbf01134e4e04ced6a750107db904d70/stdlib/builtins.pyi#L239)*, int.\_\_abs\_\_ returns an int, which is *consistent-with* the float type parameter declared in the is\_unit type hint for the v argument.

Similarly, we can write a generic version of the RandomPicker protocol presented in [Example 13-18,](020-chapter-13-interfaces-protocols-and-abcs.md#page-683-0) which was defined with a single method pick returning Any.

[Example 15-21](#page-778-0) shows how to make a generic RandomPicker covariant on the return type of pick.

<span id="page-778-0"></span>*Example 15-21. generic\_randompick.py: definition of generic RandomPicker.*

```
from typing import Protocol, runtime_checkable, TypeVar
T_co = TypeVar('T_co', covariant=True) 
@runtime_checkable
class RandomPicker(Protocol[T_co]): 
 def pick(self) -> T_co: ...
```

- Declare T\_co as covariant.
- This makes RandomPicker generic with a covariant formal type parameter.
- Use T\_co as the return type.

The generic RandomPicker protocol can be covariant because its only formal parameter is used in a return type.

<span id="page-779-0"></span>With this, we can call it a chapter.

## Chapter summary

The chapter started with a simple example of using @overload, followed by much more complex example that we studied in detail: the overloaded signatures required to correctly annotate the max built-in function.

The typing.TypedDict special construct came next. I chose to cover it here, and not in [Chapter 5](010-chapter-5-data-class-builders.md#page-265-0) where we saw typing.NamedTuple, because TypedDict is not a class builder: it's merely a way to add type hints to variable or argument that requires a dict with a specific set of string keys, and specific types for each key—which happens when we use a dict as a record, often in the context of handling with JSON data. That section was a bit long because using TypedDict can give a false sense of security, and I wanted to show how runtime checks and error handling are really inevitable when trying to make statically structured records out of mappings that are dynamic in nature.

Next we talked about typing.cast, a function designed to let us guide work of the type checker. It's important to carefully consider when to use cast, because overusing it hinders the type checker.

Runtime access to type hints came next. The key point was to use typing.get\_type\_hints instead of reading the \_\_annotations\_\_ attribute directly. However, we also discussed how that function may be unreliable with some annotations, and we saw that Python core developers are still working on a way to make type hints usable at runtime, while reducing their impact on CPU and memory usage.

The final sections were about generics, starting with the LottoBlower generic class—which we later learn is an invariant generic class. That example was followed by definitions of four basic terms: *generic type*, *formal type parameter*, *parameterized type*, and *actual type parameter*.

The major topic of variance was presented next, using cafeteria beverage dispensers and trash cans as "real life" examples of invariant, covariant and contravariant generic types. Next we reviewed, formalized and further applied those concepts to examples in Python's standard library.

Lastly, we saw how a generic static protocol is defined, first considering the typing.SupportsAbs protocol, and then applying the same idea to the RandomPicker example making it more strict than the original protocol from [Chapter 13](020-chapter-13-interfaces-protocols-and-abcs.md#page-622-0).

## NOTE

Python's type system is a huge and rapidly evolving subject. This chapter is not comprehensive. I chose to focus on topics that are either widely applicable, particularly challenging, or conceptually important.

<span id="page-781-0"></span>
## Further Reading

Python's static type system was complex as initially designed, and is getting more complex with each passing year. [Table 15-1](#page-782-0) lists all the PEPs that I am aware of as of May 2021. Python's official documentation hardly keeps up with all that, so *[Mypy's documentation](https://mypy.readthedocs.io/en/stable/)* is an essential reference. *Robust Python* [by Patrick Viafore \(O'Reilly, 2021\) is the only book that I know](https://learning.oreilly.com/library/view/robust-python/9781098100650/) about focusing on Python's static type system.

<span id="page-782-0"></span>T

а

b l

e

1 5

1

. Р

E P

S

а

b

0

и t

t

y p e h

i

n

t

S

, W

it

h li

n

k

s i

n

t

h

e

ti

tl

e

S

. Р

E P

W

it h

n

и

m

b

e

r S

m

а

r

k

e

d W

it

h \*

а

r

e

i

m

p

0

r

t

а n

t

e

n

o и

g h

t 0

b

e

m

e

n

ti

0 n

e

d

i

n

t

h e

o

p e n i n д р а r а g r а p h o f t h e t у p i n g d 0 C и m e n t

а

ti

0

n

. Q

и

e

S

ti

0

n

m

а

r k

s i

n

t h

е **Р** 

y t

h

0

n C

0

l

и

m

n i

n d

i C

а

t

e P

 $\boldsymbol{E}$ 

 $\boldsymbol{P}$ 

S

и

n d

e

r d

i

S

C

и

S

s i

o

n

0 r

n

0

t

y e

t i

m

p l

*e m e n t e d .*

| PEP  | Title<br>Python                                               | Year |      |
|------|---------------------------------------------------------------|------|------|
|      |                                                               |      |      |
| 3107 | Function Annotations                                          | 3.0  | 2006 |
| 483* | The Theory of Type Hints                                      | n/a  | 2014 |
| 484* | Type Hints                                                    | 3.5  | 2014 |
| 482  | Literature Overview for Type Hints                            | n/a  | 2015 |
| 526* | Syntax for Variable Annotations                               | 3.6  | 2016 |
| 544* | Protocols: Structural subtyping<br>(static duck typing)       | 3.8  | 2017 |
| 557  | Data Classes                                                  | 3.7  | 2017 |
| 560  | Core support for typing module<br>and generic types           | 3.7  | 2017 |
| 561  | Distributing and Packaging Type<br>Information                | 3.7  | 2017 |
| 563  | Postponed Evaluation of<br>Annotations                        | 3.7  | 2017 |
| 586* | Literal Types                                                 | 3.8  | 2018 |
| 585  | Type Hinting Generics In Standard<br>Collections              | 3.9  | 2019 |
| 589* | TypedDict: Type Hints for<br>Dictionaries with a Fixed Set of | 3.8  | 2019 |

| Keys |  |
|------|--|
|      |  |

| Adding a final qualifier to typing                                          | 3.8  | 2019 |
|-----------------------------------------------------------------------------|------|------|
| Flexible function and variable<br>annotations                               | ?    | 2019 |
| Allow writing union types as X   Y                                          | 3.10 | 2019 |
| Parameter Specification Variables                                           | 3.10 | 2019 |
| Explicit Type Aliases                                                       | 3.10 | 2020 |
| Allow writing optional types as x?                                          | ?    | 2020 |
| Variadic Generics                                                           | ?    | 2020 |
| User-Defined Type Guards                                                    | 3.10 | 2021 |
| Deferred Evaluation Of<br>Annotations Using Descriptors                     | ?    | 2021 |
| Marking individual TypedDict<br>items as required or potentially<br>missing | ?    | 2021 |
|                                                                             |      |      |

The subtle topic of variance has its own [section](https://www.python.org/dev/peps/pep-0484/#covariance-and-contravariance) in PEP 484, and is also covered in the *[Generics](https://mypy.readthedocs.io/en/stable/generics.html#variance-of-generic-types)* page of Mypy, as well as in their invaluable *[Common Issues](https://mypy.readthedocs.io/en/latest/common_issues.html#variance)* page.

*[PEP 362—Function Signature Object](https://www.python.org/dev/peps/pep-0362/)* is worth reading if you intend to use the inspect module that complements the typing.get\_type\_hints function.

If you are interested in the history of Python, you may like to know that Guido van Rossum posted *[Adding Optional Static Typing to Python](https://www.artima.com/weblogs/viewpost.jsp?thread=85551)* on December 23, 2004.

*[Python 3 types in the wild: a tale of two type systems](https://dl.acm.org/doi/10.1145/3426422.3426981)* is a research paper by Ingkarat Rak-amnouykit and others from the Rensselaer Polytechnic Institute and IBM TJ Watson Research Center. The paper surveys the use of type hints in open source projects on GitHub, showing that most projects don't use them, and also that most projects that have type hints apparently don't use a type checker. I found most interesting the discussion of the different semantics of *Mypy* and Google's *pytype*, which they conclude are "essentially two different type systems".

Gilad Bracha's seminal paper *[Pluggable Types](http://bracha.org/pluggableTypesPosition.pdf)*, submits that one of the advantages of gradual typing is to allow multiple type systems for the same language:

*Once our runtime is independent of the type system, we can choose to treat type systems as plug-ins. We can have zero, one or many type systems, suited to differing purposes, all at the same time. There are static type systems that deal with aliasing, ownership, with information flow, as well as traditional types systems. Indeed, a very wide range of static analyses can be cast as type systems.*

Another seminal paper about gradual typing is *Static Typing Where [Possible, Dynamic Typing When Needed: The End of the Cold War Between](https://www.researchgate.net/publication/213886116_Static_Typing_Where_Possible_Dynamic_Typing_When_Needed_The_End_of_the_Cold_War_Between_Programming_Languages) Programming Languages* by Eric Meijer and Peter Drayton. [15](#page-796-7)

I learned a lot reading the relevant parts of a some books about other languages that implement some of the same ideas:

- <span id="page-790-0"></span>*[Atomic Kotlin](https://www.atomickotlin.com/atomickotlin/)*—Bruce Eckel and Svetlana Isakova (Leanpub, 2020)
- *[Effective Java, 3rd Edition](https://www.informit.com/store/effective-java-9780134685991)*—Joshua Bloch (Addison-Wesley, 2017)
- *[Programming with Types: TypeScript Examples](https://www.manning.com/books/programming-with-types)*—Vlad Riscutia (Manning, 2019)
- *[Programming TypeScript](https://learning.oreilly.com/library/view/programming-typescript/9781492037644/)*—Boris Cherny (O'Reilly, 2019)
- <span id="page-790-1"></span>*[The Dart Programming Language](https://www.informit.com/store/dart-programming-language-9780321927705)*—Gilad Bracha (Addison-Wesley, 2016). [16](#page-796-8)

For some critical views on type systems, I recommend Victor Youdaiken's posts *[Bad ideas in type theory](https://www.yodaiken.com/2017/09/15/bad-ideas-in-type-theory/)* and *[Types considered harmful II](https://www.yodaiken.com/2017/11/30/types-considered-harmful-ii/)*,

Finally, I was surprised to find [Generics Considered Harmful](https://web.archive.org/web/20071010002142/http://weblogs.java.net/blog/arnold/archive/2005/06/generics_consid_1.html) by Ken Arnold, a core contributor to Java from the beginning, as well as co-author of the first four editions of the officially branded *The Java Programming Language* book—in collaboration with James Gosling, the lead designer of Java.

Sadly, Arnold's criticism of Java's type system applies to Python's as well. While reading the many rules and special cases of the typing PEPs, I was constantly reminded of this passage from Gosling's post:

*Which brings up the problem that I always cite for C++: I call it the "N order exception to the exception rule." It sounds like this: "You can do x, except in case y, unless y does z, in which case you can if …" th*

Fortunately, Python has a key advantage over Java and C++: we have a gradual type system. We can completely or partially omit type hints when the complexity they add is not worthwhile.

## SOAPBOX

## Typing Rabbit Holes

When using a type checker, we are sometimes forced to discover and import classes we did not need to know about, and our code has no need to reference—except to write type hints. Such classes are undocumented, probably because they are considered implementation details by the authors of the packages. Here are two examples from the standard library.

To use cast() in the server.sockets example in "Type [Casting", I had to scour the vast](#page-757-0) *asyncio* documentation and then browse the source code of several modules in that package to discover the undocumented TransportSocket class in the equally undocumented asyncio.trsock module. Using socket.socket instead of TransportSocket would be incorrect, because the latter is explicitly not a subtype of the former, according to a [docstring](https://github.com/python/cpython/blob/3e7ee02327db13e4337374597cdc4458ecb9e3ad/Lib/asyncio/trsock.py#L5) in the source code.

[I fell into a similar rabbit hole when I added type hints to Example 20-](027-chapter-20-concurrency-models-in-python.md#page-1049-0) 13, a simple demonstration of multiprocessing. That example uses SimpleQueue objects, which you get by calling multiprocessing.SimpleQueue(). However, I could not use that name in a type hint, because it turns out that multiprocessing.SimpleQueue is not a class! It's a bound method of the undocumented multiprocessing.BaseContext class, which builds and returns an instance of the SimpleQueue class defined in the undocumented multiprocessing.queues module.

In each of those cases I had to spend a couple of hours to find the right undocumented class to import, just to write a single type hint. This kind of research is part of the job when writing a book. But when writing application code, I'd probably avoid such scavenger hunts for a single offending line and just write # type: ignore. Sometimes that's the only cost-effective solution.

## Variance notation in other languages

Variance is a difficult topic and Python's type hints syntax is not as good as it could be. This is evidenced by this direct quote from PEP 484:

<span id="page-793-0"></span>*Covariance or contravariance is not a property of a type variable, but a property of a generic class defined using this variable. [17](#page-796-9)*

If that is the case, why are covariance and contravariance declared with TypeVar and not on the generic class?

The authors of PEP 484 worked under the severe self-imposed constraint that type hints should be supported without making any change to the interpreter. This required the introduction of TypeVar to define type variables, and also the abuse of [] to provide Klass[T] syntax for generics—instead of the Klass<T> notation used in other popular languages, including C#, Java, Kotlin, and TypeScript. None of these languages require type variables to be declared before use.

In addition, the syntax of Kotlin and C# makes it clear whether the type parameter is covariant, contravariant or invariant exactly where it makes sense: in the class or interface declaration.

In Kotlin, we could declare the BeverageDispenser like this:

```
class BeverageDispenser<out T> {
 // etc...
}
```

The out modifier in the formal type parameter means T is an "output" type, therefore BeverageDispenser is covariant.

You can probably guess how TrashCan would be declared:

```
class TrashCan<in T> {
 // etc...
}
```

Given T as an "input" formal type parameter, then TrashCan is contravariant.

If neither in nor out appear, then the class is invariant on the parameter.

It's easy to recall the ["Variance Rules of Thumb"](#page-775-0) when out and in are used in the formal type parameters.

This suggests that a good naming convention for covariant and contravariant type variables in Python would be:

```
T_out = TypeVar('T_out', covariant=True)
T_in = TypeVar('T_in', contravariant=True)
```

Then we could define the classes like this:

```
class BeverageDispenser(Generic[T_out]):
 ...
class TrashCan(Generic[T_in]):
 ...
```

Is it too late to change the naming convention established in PEP 484?

## False Positives 147 × False Negatives 19

Many *typeshed* bugs are tagged *false positive* or *false negative*.

It's a *false positive* when the type hints are too restrictive and make type checkers report false errors. That was the case with the statistics.mode type hints which accepted only numbers, while [the function can handle any hashable, as discussed in "Restricted](014-chapter-8-type-hints-in-functions.md#page-430-0) TypeVar".

The max issue [#4051](https://github.com/python/typeshed/issues/4051) discussed before is a *false negative*: the type hints were not strict enough, so type checkers were unable to catch some invalid arguments.

On May 27, 2020, I counted 147 *false positive* issues (41 open) and 19 *false negatives* (8 open) on *typeshed*. That's a ratio of 7.7 *false positive*

for each *false negative*.

In the *typeshed* sample, type hints are strongly biased to raise false alarms. I don't know what causes this. It may be because it's easier to write type hints that are overly restrictive, either due to limitations in Python's type system or due to our collective experience with traditional nominally typed languages that provide less flexible APIs than Python allows.

The Python type hinting PEPs and tools were developed by teams working on some of the largest Python-powered systems in the world. So this *false positive* bias may be intentional: in large systems the cost of detecting and fixing a bug in production may be very high, so it's better for them to err on the side of caution. I wonder if the bias is as good for every Python user as it is for the Web-scale companies that sponsored most of the work on *typeshed* and the static type checkers.

- <span id="page-795-0"></span>[1](#page-738-1) From YouTube video of *A Language Creators' Conversation: Guido van Rossum, James Gosling, Larry Wall & Anders Hejlsberg*, streamed live on April 2, 2019. Quote starts at [1:32:05,](https://www.youtube.com/watch?v=csL8DLXGNlU&t=92m5s) edited for brevity. Full transcript available at *<https://github.com/fluentpython/language-creators>*.
- <span id="page-795-1"></span>[2](#page-742-0) I am grateful to Jelle Zijlstra—a *typeshed* maintainer—who taught me several things, including how to reduce my original 9 overloads to 6.
- <span id="page-795-2"></span>[3](#page-751-1) As of May 2020, pytype allows it. But its [FAQ](https://google.github.io/pytype/faq.html) says it will be disallowed in the future. See question "Why didn't pytype catch that I changed the type of an annotated variable?" in the pytype [FAQ](https://google.github.io/pytype/faq.html).
- <span id="page-795-3"></span>4 I prefer to use the [lxml](https://lxml.de/) package to generate and parse XML: it's easy to get started, fullfeatured, and fast. Unfortunately, lxml and Python's own [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html) don't fit the limited RAM of my hypothetical microcontroller.
- <span id="page-795-4"></span>[5](#page-752-2) The Mypy documentation discusses this in its [Common issues and solutions](https://mypy.readthedocs.io/en/stable/common_issues.html) page, section [Types of empty collections](https://mypy.readthedocs.io/en/stable/common_issues.html#types-of-empty-collections).
- <span id="page-795-5"></span>[6](#page-753-2) Brett Cannon, Guido van Rossum, and others have been discussing how to type hint json.loads() since 2016 in [Mypy issue #182: Define a JSON type](https://github.com/python/typing/issues/182).
- <span id="page-795-6"></span>[7](#page-758-0) The use of enumerate in the example is intended to confuse the type checker. A simpler implementation yielding strings directly instead of going through the enumerate index is correctly analysed by Mypy, and the cast() is not needed.

- <span id="page-796-0"></span>8 I reported *typeshed* [issue #5535](https://github.com/python/typeshed/issues/5535) "Wrong type hint for asyncio.base\_events.Server sockets attribute." and it was quickly fixed by Sebastian Rittau. However, I decided to keep the example because it illustrates a common use case for cast, and the cast I wrote is harmless.
- <span id="page-796-1"></span>[9](#page-759-0) To be honest, I originally appended a # type: ignore comment to the line with server.sockets[0] because after a little research I found similar lines the *asyncio* [documentation](https://docs.python.org/3/library/asyncio-stream.html#tcp-echo-server-using-streams) and in a [test case,](https://github.com/python/cpython/blob/b798ab06937f8bb24b444a49dd42e11fff15e654/Lib/test/test_asyncio/test_server.py#L55) so I suspected the problem was not in my code.
- <span id="page-796-2"></span>[10](#page-759-1) [19 May 2020 message](https://mail.python.org/archives/list/typing-sig@python.org/message/5LCWMN2UY2UQNLC5Z47GHBZKSPZW4I63/) to the typing-sig mailing list.
- <span id="page-796-3"></span>[11](#page-759-2) The syntax # type: ignore[code] allows you to specify which Mypy error code is being silenced, but the codes are not always easy to interpret. See *[error codes](https://mypy.readthedocs.io/en/stable/error_codes.html#error-codes)* in the Mypy documentation
- <span id="page-796-4"></span>[12](#page-763-0) Message *[PEP 563 in light of PEP 649](https://mail.python.org/archives/list/python-dev@python.org/message/ZBJ7MD6CSGM6LZAOTET7GXAVBZB7O77O/)*, posted April 16, 2021.
- <span id="page-796-5"></span>[13](#page-767-0) The terms are from Joshua Bloch's classic book *Effective Java, Third Edition* (Addison Wesley, 2017). The definitions and examples are mine.
- <span id="page-796-6"></span>[14](#page-768-2) I first saw the cafeteria analogy for variance in Erik Meijer's *Foreword* in *The Dart Programming Language* book by Gilad Bracha (Addison-Wesley, 2016).
- <span id="page-796-7"></span>[15](#page-790-0) As a reader of footnotes, so you may recall that I credited Erik Meijer for the cafeteria analogy to explain variance.
- <span id="page-796-8"></span>[16](#page-790-1) That book was written for Dart 1. There are significant changes in Dart 2—including in the type system. Nevertheless, Bracha is an important resarcher in the field of programming language design, and I found the book valuable for his perspective on the design of Dart.
- <span id="page-796-9"></span>[17](#page-793-0) Last paragraph of section *[Covariance and Contravariance](https://www.python.org/dev/peps/pep-0484/#covariance-and-contravariance)* in PEP 484.
