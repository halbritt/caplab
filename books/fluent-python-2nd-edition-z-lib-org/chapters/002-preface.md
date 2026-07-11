<span id="page-5-1"></span>
# Preface

<span id="page-5-0"></span>
## WARNING

The Preface has not been updated from the *First Edition*. This will be the last part of the book to be updated for the *Second Edition*.

*Here's the plan: when someone uses a feature you don't understand, simply shoot them. This is easier than learning something new, and before too long the only living coders will be writing in an easily understood, tiny subset of Python 0.9.6 <wink>. [1](003-acknowledgments.md#page-18-0)*

> —Tim Peters, Legendary core developer and author of The Zen of Python

"Python is an easy to learn, powerful programming language." Those are the first words of the [official Python Tutorial](https://docs.python.org/3/tutorial/). That is true, but there is a catch: because the language is easy to learn and put to use, many practicing Python programmers leverage only a fraction of its powerful features.

An experienced programmer may start writing useful Python code in a matter of hours. As the first productive hours become weeks and months, a lot of developers go on writing Python code with a very strong accent carried from languages learned before. Even if Python is your first language, often in academia and in introductory books it is presented while carefully avoiding language-specific features.

As a teacher introducing Python to programmers experienced in other languages, I see another problem that this book tries to address: we only miss stuff we know about. Coming from another language, anyone may guess that Python supports regular expressions, and look that up in the docs. But if you've never seen tuple unpacking or descriptors before, you will probably not search for them, and may end up not using those features just because they are specific to Python.

<span id="page-6-0"></span>This book is not an A-to-Z exhaustive reference of Python. Its emphasis is on the language features that are either unique to Python or not found in many other popular languages. This is also mostly a book about the core language and some of its libraries. I will rarely talk about packages that are not in the standard library, even though the Python package index now lists more than 60,000 libraries and many of them are incredibly useful.

## Who This Book Is For

This book was written for practicing Python programmers who want to become proficient in Python 3. If you know Python 2 but are willing to migrate to Python 3.4 or later, you should be fine. At the time of this writing, the majority of professional Python programmers are using Python 2, so I took special care to highlight Python 3 features that may be new to that audience.

However, *Fluent Python* is about making the most of Python 3.4, and I do not spell out the fixes needed to make the code work in earlier versions. Most examples should run in Python 2.7 with little or no changes, but in some cases, backporting would require significant rewriting.

Having said that, I believe this book may be useful even if you must stick with Python 2.7, because the core concepts are still the same. Python 3 is not a new language, and most differences can be learned in an afternoon. [What's New in Python 3.0](https://docs.python.org/3.0/whatsnew/3.0.html) is a good starting point. Of course, there have been changes since Python 3.0 was released in 2009, but none as important as those in 3.0.

<span id="page-7-0"></span>If you are not sure whether you know enough Python to follow along, review the topics of the official [Python Tutorial](https://docs.python.org/3/tutorial/). Topics covered in the tutorial will not be explained here, except for some features that are new in Python 3.

## Who This Book Is Not For

<span id="page-8-0"></span>If you are just learning Python, this book is going to be hard to follow. Not only that, if you read it too early in your Python journey, it may give you the impression that every Python script should leverage special methods and metaprogramming tricks. Premature abstraction is as bad as premature optimization.

## How This Book Is Organized

The core audience for this book should not have trouble jumping directly to any chapter in this book. However, each of the six parts forms a book within the book. I conceived the chapters within each part to be read in sequence.

I tried to emphasize using what is available before discussing how to build your own. For example, in [Part II,](006-part-ii-data-structures.md#page-50-0) [Chapter 2](007-chapter-2-an-array-of-sequences.md#page-51-0) covers sequence types that are ready to use, including some that don't get a lot of attention, like collections.deque. Building user-defined sequences is only addressed in [Part IV](017-part-iv-classes-and-protocols.md#page-532-0), where we also see how to leverage the abstract base classes (ABCs) from collections.abc. Creating your own ABCs is discussed even later in [Part IV,](017-part-iv-classes-and-protocols.md#page-532-0) because I believe it's important to be comfortable using an ABC before writing your own.

This approach has a few advantages. First, knowing what is ready to use can save you from reinventing the wheel. We use existing collection classes more often than we implement our own, and we can give more attention to the advanced usage of available tools by deferring the discussion on how to create new ones. We are also more likely to inherit from existing ABCs than to create a new ABC from scratch. And finally, I believe it is easier to understand the abstractions after you've seen them in action.

The downside of this strategy are the forward references scattered throughout the chapters. I hope these will be easier to tolerate now that you know why I chose this path.

Here are the main topics in each part of the book:

## Part I, Prologue

A single chapter about the Python Data Model explaining how the special methods (e.g., \_\_repr\_\_) are the key to the consistent behavior of objects of all types—in a language that is admired for its consistency. Understanding various facets of the data model is the subject of most of the rest of the book, but [Chapter 1](005-chapter-1-the-python-data-model.md#page-20-0) provides a highlevel overview.

## Part II, Data Structures

The chapters in this part cover the use of collection types: sequences, mappings, and sets, as well as the str versus bytes split—the cause of much celebration among Python 3 users and much pain for Python 2 users who have not yet migrated their codebases. The main goals are to recall what is already available and to explain some behavior that is sometimes surprising, like the reordering of dict keys when we are not looking, or the caveats of locale-dependent Unicode string sorting. To achieve these goals, the coverage is sometimes high level and wide (e.g., when many variations of sequences and mappings are presented) and sometimes deep (e.g., when we dive into the hash tables underneath the dict and set types).

## Part III, Functions as Objects

Here we talk about functions as first-class objects in the language: what that means, how it affects some popular design patterns, and how to implement function decorators by leveraging closures. Also covered here is the general concept of callables in Python, function attributes, introspection, parameter annotations, and the new nonlocal declaration in Python 3.

## Part IV, Classes and Protocols

Now the focus is on building classes. In [Part II](006-part-ii-data-structures.md#page-50-0), the class declaration appears in few examples; [Part IV](017-part-iv-classes-and-protocols.md#page-532-0) presents many classes. Like any object-oriented (OO) language, Python has its particular set of features that may or may not be present in the language in which you and I learned class-based programming. The chapters explain how references work, what mutability really means, the lifecycle of instances, how to build your own collections and ABCs, how to cope with multiple inheritance, and how to implement operator overloading—when that makes sense.

*[Link to Come]*

Covered in this part are the language constructs and libraries that go beyond sequential control flow with conditionals, loops, and subroutines. We start with generators, then visit context managers and coroutines, including the challenging but powerful new yield from syntax. [Link to Come] closes with a high-level introduction to modern concurrency in Python with collections.futures (using threads and processes under the covers with the help of futures) and doing event-oriented I/O with asyncio (leveraging futures on top of coroutines and yield from).

## [Link to Come]

This part starts with a review of techniques for building classes with attributes created dynamically to handle semi-structured data such as JSON datasets. Next, we cover the familiar properties mechanism, before diving into how object attribute access works at a lower level in Python using descriptors. The relationship between functions, methods, and descriptors is explained. Throughout [Link to Come], the step-bystep implementation of a field validation library uncovers subtle issues that lead to the use of the advanced tools of the final chapter: class decorators and metaclasses.

<span id="page-11-0"></span>
## Hands-On Approach

Often we'll use the interactive Python console to explore the language and libraries. I feel it is important to emphasize the power of this learning tool, particularly for those readers who've had more experience with static, compiled languages that don't provide a read-eval-print loop (REPL).

One of the standard Python testing packages, [doctest](https://docs.python.org/3/library/doctest.html), works by simulating console sessions and verifying that the expressions evaluate to the responses shown. I used doctest to check most of the code in this book, including the console listings. You don't need to use or even know about doctest to follow along: the key feature of doctests is that they

look like transcripts of interactive Python console sessions, so you can easily try out the demonstrations yourself.

Sometimes I will explain what we want to accomplish by showing a doctest before the code that makes it pass. Firmly establishing what is to be done before thinking about how to do it helps focus our coding effort. Writing tests first is the basis of test driven development (TDD) and I've also found it helpful when teaching. If you are unfamiliar with doctest, take a look at its [documentation](https://docs.python.org/3/library/doctest.html) and this book's [source code repository.](https://github.com/fluentpython/example-code) You'll find that you can verify the correctness of most of the code in the book by typing python3 -m doctest example\_script.py in the command shell of your OS.

<span id="page-12-0"></span>
## Hardware Used for Timings

The book has some simple benchmarks and timings. Those tests were performed on one or the other laptop I used to write the book: a 2011 MacBook Pro 13″ with a 2.7 GHz Intel Core i7 CPU, 8GB of RAM, and a spinning hard disk, and a 2014 MacBook Air 13″ with a 1.4 GHz Intel Core i5 CPU, 4GB of RAM, and a solid-state disk. The MacBook Air has a slower CPU and less RAM, but its RAM is faster (1600 versus 1333 MHz) and the SSD is much faster than the HD. In daily usage, I can't tell which machine is faster.

<span id="page-12-1"></span>
## Soapbox: My Personal Perspective

I have been using, teaching, and debating Python since 1998, and I enjoy studying and comparing programming languages, their design, and the theory behind them. At the end of some chapters, I have added "Soapbox" sidebars with my own perspective about Python and other languages. Feel free to skip these if you are not into such discussions. Their content is completely optional.

<span id="page-13-0"></span>
## Python Jargon

I wanted this to be a book not only about Python but also about the culture around it. Over more than 20 years of communications, the Python community has developed its own particular lingo and acronyms. Here you'll see that some words—like "decorator", "descriptor", and "protocol"—have special meaning among Pythonistas. You'll also get fluent with Python slang like "dunder", "listcomp", and "genexp".

<span id="page-13-1"></span>
## Python Version Covered

I tested all the code in the book using Python 3.4—that is, CPython 3.4, the most popular Python implementation written in C. There is only one exception: "Using @ [as an infix operator"](023-chapter-16-operator-overloading-doing-it-right.md#page-813-0) shows the @ operator, which is only supported by Python 3.5.

Almost all code in the book should work with any Python 3.x–compatible interpreter, including PyPy3 2.4.0, which is compatible with Python 3.2.5. The notable exceptions are the examples using yield from and asyncio, which are only available in Python 3.3 or later.

Most code should also work with Python 2.7 with minor changes, except the Unicode-related examples in [Chapter 4,](009-chapter-4-text-versus-bytes.md#page-201-0) and the exceptions already noted for Python 3 versions earlier than 3.3.

<span id="page-13-2"></span>
## Conventions Used in This Book

The following typographical conventions are used in this book:

*Italic*

Indicates new terms, URLs, email addresses, filenames, and file extensions.

*Constant width*

Used for program listings, as well as within paragraphs to refer to program elements such as variable or function names, databases, data types, environment variables, statements, and keywords.

Note that when a line break falls within a constant\_width term, a hyphen is not added—it could be misunderstood as part of the term.

## Constant width bold

Shows commands or other text that should be typed literally by the user.

## Constant width italic

Shows text that should be replaced with user-supplied values or by values determined by context.

**TIP**

This element signifies a tip or suggestion.

**NOTE**

This element signifies a general note.

**WARNING**

This element indicates a warning or caution.

<span id="page-14-0"></span>
## Using Code Examples

Every script and most code snippets that appear in the book are available in [the Fluent Python code repository](https://github.com/fluentpython/example-code) on GitHub.

We appreciate, but do not require, attribution. An attribution usually includes the title, author, publisher, and ISBN. For example: "*Fluent Python* by Luciano Ramalho (O'Reilly). Copyright 2015 Luciano Ramalho, 978-1- 491-94600-8."

<span id="page-15-0"></span>
## How to Contact Us

Please address comments and questions concerning this book to the publisher:

O'Reilly Media, Inc.

1005 Gravenstein Highway North

Sebastopol, CA 95472

800-998-9938 (in the United States or Canada)

707-829-0515 (international or local)

707-829-0104 (fax)

We have a web page for this book, where we list errata, examples, and any [additional information. You can access this page at](http://bit.ly/fluent-python) *http://bit.ly/fluentpython*.

To comment or ask technical questions about this book, send email to *[bookquestions@oreilly.com](mailto:bookquestions@oreilly.com)*.

For more information about our books, courses, conferences, and news, see our website at *[http://www.oreilly.com](http://www.oreilly.com/)*.

Find us on Facebook: *<http://facebook.com/oreilly>*

Follow us on Twitter: *<http://twitter.com/oreillymedia>*

Watch us on YouTube: *<http://www.youtube.com/oreillymedia>*
