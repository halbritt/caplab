<span id="page-923-1"></span>
# Chapter 18: Context Managers and else Blocks

## A NOTE FOR EARLY RELEASE READERS

With Early Release ebooks, you get books in their earliest form—the author's raw and unedited content as they write—so you can take advantage of these technologies long before the official release of these titles.

This will be the 18th chapter of the final book. Please note that the GitHub repo will be made active later on.

If you have comments about how we might improve the content and/or examples in this book, or if you notice missing material within this chapter, please reach out to the author at [fluentpython2e@ramalho.org.](mailto:fluentpython2e@ramalho.org)

*Context managers may end up being almost as important as the subroutine itself. We've only scratched the surface with them. […] Basic has a with statement, there are with statements in lots of languages. But they don't do the same thing, they all do something very shallow, they save you from repeated dotted [attribute] lookups, they don't do setup and tear down. Just because it's the same name don't think it's the same thing. The with statement is a very big deal. [1](#page-952-0)*

<span id="page-923-0"></span>—Raymond Hettinger, Eloquent Python evangelist

In this chapter, we will discuss control flow features that are not so common in other languages, and for this reason tend to be overlooked or underused in Python. They are:

- The with statement and context managers.
- The else clause in for, while, and try statements.

Pattern matching with match/case.

The with statement sets up a temporary context and reliably tears it down, under the control of a context manager object. This prevents errors and reduces boilerplate code, making APIs at the same time safer and easier to use. Python programmers are finding lots of uses for with blocks beyond automatic file closing.

## XXX

The else clause is completely unrelated to with. But this is [Link to Come]—Control Flow. I couldn't find another place for covering else, and I wouldn't have a one-page chapter about it, so here it is.

Pattern matching appeared in several previous chapters, but here you'll see a more extensive example in ["Pattern Matching: a Case Study"](#page-940-0).

<span id="page-924-0"></span>
## What's new in this chapter

The only updates are in ["The contextlib Utilities",](#page-933-0) mentioning features of the contextlib module added since Python 3.5.

Let's review the smaller topic to get to the real substance of this chapter.

<span id="page-924-1"></span>
## Do This, Then That: else Blocks Beyond if

This is no secret, but it is an underappreciated language feature: the else clause can be used not only in if statements but also in for, while, and try statements.

The semantics of for/else, while/else, and try/else are closely related, but very different from if/else. Initially the word else actually hindered my understanding of these features, but eventually I got used to it.

Here are the rules:

*for*

The else block will run only if and when the for loop runs to completion (i.e., not if the for is aborted with a break).

## while

The else block will run only if and when the while loop exits because the condition became *falsy* (i.e., not if the while is aborted with a break).

## try

The else block will only run if no exception is raised in the try block. The [official docs](http://bit.ly/1MMa1YB) also state: "Exceptions in the else clause are not handled by the preceding except clauses."

In all cases, the else clause is also skipped if an exception or a return, break, or continue statement causes control to jump out of the main block of the compound statement.

## NOTE

I think else is a very poor choice for the keyword in all cases except if. It implies an excluding alternative, like "Run this loop, otherwise do that," but the semantics for else in loops is the opposite: "Run this loop, then do that." This suggests then as a better keyword—which would also make sense in the try context: "Try this, then do that." However, adding a new keyword is a breaking change to the language—not an easy decision to make.

Using else with these statements often makes the code easier to read and saves the trouble of setting up control flags or coding extra if statements.

The use of else in loops generally follows the pattern of this snippet:

```
for item in my_list:
 if item.flavor == 'banana':
 break
```

```
else:
 raise ValueError('No banana flavor found!')
```

In the case of try/except blocks, else may seem redundant at first. After all, the after\_call() in the following snippet will run only if the dangerous\_call() does not raise an exception, correct?

```
try:
 dangerous_call()
 after_call()
except OSError:
 log('OSError...')
```

However, doing so puts the after\_call() inside the try block for no good reason. For clarity and correctness, the body of a try block should only have the statements that may generate the expected exceptions. This is much better:

```
try:
 dangerous_call()
except OSError:
 log('OSError...')
else:
 after_call()
```

Now it's clear that the try block is guarding against possible errors in dangerous\_call() and not in after\_call(). It's also more obvious that after\_call() will only execute if no exceptions are raised in the try block.

In Python, try/except is commonly used for control flow, and not just for error handling. There's even an acronym/slogan for that documented in the [official Python glossary](https://docs.python.org/3/glossary.html#term-eafp):

## EAFP

*Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false. This clean and fast style is characterized by the presence of many try and except statements. The technique contrasts with the LBYL style common to many other languages such as C.*

The glossary then defines LBYL:

## LBYL

*Look before you leap. This coding style explicitly tests for preconditions before making calls or lookups. This style contrasts with the EAFP approach and is characterized by the presence of many if statements. In a multi-threaded environment, the LBYL approach can risk introducing a race condition between "the looking" and "the leaping". For example, the code, if key in mapping: return mapping[key] can fail if another thread removes key from mapping after the test, but before the lookup. This issue can be solved with locks or by using the EAFP approach.*

Given the EAFP style, it makes even more sense to know and use well else blocks in try/except statements.

Now let's address the main topic of this chapter: the powerful with statement.

<span id="page-927-0"></span>
## Context Managers and with Blocks

Context manager objects exist to control a with statement, just like iterators exist to control a for statement.

The with statement was designed to simplify the try/finally pattern, which guarantees that some operation is performed after a block of code,

even if the block is aborted because of an exception, a return or sys.exit() call. The code in the finally clause usually releases a critical resource or restores some previous state that was temporarily changed.

The context manager interface consists of the \_\_enter\_\_ and \_\_exit\_\_ methods. At the start of the with, \_\_enter\_\_ is invoked on the context manager object. The role of the finally clause is played by a call to \_\_exit\_\_ on the context manager object at the end of the with block.

The most common example is making sure a file object is closed. See [Example 18-1](#page-928-0) for a detailed demonstration of using with to close a file.

<span id="page-928-0"></span>
## Example 18-1. Demonstration of a file object as a context manager

```
>>> with open('mirror.py') as fp: 
... src = fp.read(60) 
...
>>> len(src)
60
>>> fp 
<_io.TextIOWrapper name='mirror.py' mode='r' encoding='UTF-8'>
>>> fp.closed, fp.encoding 
(True, 'UTF-8')
>>> fp.read(60) 
Traceback (most recent call last):
 File "<stdin>", line 1, in <module>
ValueError: I/O operation on closed file.
```

- fp is bound to the opened file because the file's \_\_enter\_\_ method returns self.
- Read some data from fp.
- <span id="page-928-1"></span>The fp variable is still available. [2](#page-952-1)
- You can read the attributes of the fp object.
- But you can't perform I/O with fp because at the end of the with block, the TextIOWrapper.\_\_exit\_\_ method is called and closes

the file.

The first callout in [Example 18-1](#page-928-0) makes a subtle but crucial point: the context manager object is the result of evaluating the expression after with, but the value bound to the target variable (in the as clause) is the result of calling \_\_enter\_\_ on the context manager object.

It just happens that in [Example 18-1,](#page-928-0) the open() function returns an instance of TextIOWrapper, and its \_\_enter\_\_ method returns self. But the \_\_enter\_\_ method may also return some other object instead of the context manager.

When control flow exits the with block in any way, the \_\_exit\_\_ method is invoked on the context manager object, not on whatever is returned by \_\_enter\_\_.

The as clause of the with statement is optional. In the case of open, you'll always need it to get a reference to the file, but some context managers return None because they have no useful object to give back to the user.

[Example 18-2](#page-929-0) shows the operation of a perfectly frivolous context manager designed to highlight the distinction between the context manager and the object returned by its \_\_enter\_\_ method.

<span id="page-929-0"></span>*Example 18-2. Test driving the LookingGlass context manager class*

```
 >>> from mirror import LookingGlass
 >>> with LookingGlass() as what: 
 ... print('Alice, Kitty and Snowdrop') 
 ... print(what)
 ...
 pordwonS dna yttiK ,ecilA 
 YKCOWREBBAJ
 >>> what 
 'JABBERWOCKY'
 >>> print('Back to normal.') 
 Back to normal.
```

The context manager is an instance of LookingGlass; Python calls \_\_enter\_\_ on the context manager and the result is bound to what.

- Print a str, then the value of the target variable what.
- The output of each print comes out backward.
- Now the with block is over. We can see that the value returned by \_\_enter\_\_, held in what, is the string 'JABBERWOCKY'.
- Program output is no longer backward.

[Example 18-3](#page-930-0) shows the implementation of LookingGlass.

<span id="page-930-0"></span>*Example 18-3. mirror.py: code for the LookingGlass context manager class* **class LookingGlass**:

```
 def __enter__(self): 
 import sys
 self.original_write = sys.stdout.write 
 sys.stdout.write = self.reverse_write 
 return 'JABBERWOCKY' 
 def reverse_write(self, text): 
 self.original_write(text[::-1])
 def __exit__(self, exc_type, exc_value, traceback): 
 import sys 
 sys.stdout.write = self.original_write 
 if exc_type is ZeroDivisionError: 
 print('Please DO NOT divide by zero!')
 return True
```

- Python invokes \_\_enter\_\_ with no arguments besides self.
- Hold the original sys.stdout.write method in an instance attribute for later use.

Monkey-patch sys.stdout.write, replacing it with our own method.

- Return the 'JABBERWOCKY' string just so we have something to put in the target variable what.
- Our replacement to sys.stdout.write reverses the text argument and calls the original implementation.
- Python calls \_\_exit\_\_ with None, None, None if all went well; if an exception is raised, the three arguments get the exception data, as described next.
- It's cheap to import modules again because Python caches them.
- Restore the original method to sys.stdout.write.
- If the exception is not None and its type is ZeroDivisionError, print a message…
- …and return True to tell the interpreter that the exception was handled.
- If \_\_exit\_\_ returns None or anything but True, any exception raised in the with block will be propagated.

## TIP

When real applications take over standard output, they often want to replace sys.stdout with another file-like object for a while, then switch back to the original. The [contextlib.redirect\\_stdout](http://bit.ly/1MM7Sw6) context manager does exactly that: just pass it the file-like object that will stand in for sys.stdout.

The interpreter calls the \_\_enter\_\_ method with no arguments—beyond the implicit self. The three arguments passed to \_\_exit\_\_ are: *exc\_type*

The exception class (e.g., ZeroDivisionError).

## exc\_value

The exception instance. Sometimes, parameters passed to the exception constructor—such as the error message—can be found in exc\_value.args.

## traceback

<span id="page-932-1"></span>A traceback object. [3](#page-952-2)

For a detailed look at how a context manager works, see [Example 18-4](#page-932-0), where LookingGlass is used outside of a with block, so we can manually call its \_\_enter\_\_ and \_\_exit\_\_ methods.

<span id="page-932-0"></span>
## Example 18-4. Exercising LookingGlass without a with block

```
 >>> from mirror import LookingGlass
 >>> manager = LookingGlass() 
 >>> manager
 <mirror.LookingGlass object at 0x2a578ac>
 >>> monster = manager.__enter__() 
 >>> monster == 'JABBERWOCKY' 
 eurT
 >>> monster
 'YKCOWREBBAJ'
 >>> manager
 >ca875a2x0 ta tcejbo ssalGgnikooL.rorrim<
 >>> manager.__exit__(None, None, None) 
 >>> monster
 'JABBERWOCKY'
```

- Instantiate and inspect the manager instance.
- Call the context manager \_\_enter\_\_() method and store result in monster.
- Monster is the string 'JABBERWOCKY'. The True identifier appears reversed because all output via stdout goes through the write method we patched in \_\_enter\_\_.

Call manager.\_\_exit\_\_ to restore previous stdout.write.

Context managers are a fairly novel feature and slowly but surely the Python community is finding new, creative uses for them. Some examples from the standard library are:

- Managing transactions in the sqlite3 module; see "12.6.7.3. [Using the connection as a context manager".](http://bit.ly/1MM89PC)
- Holding locks, conditions, and semaphores in threading code; [see "17.1.10. Using locks, conditions, and semaphores in the](http://bit.ly/1MM8guy) with statement".
- Setting up environments for arithmetic operations with Decimal objects; see the [decimal.localcontext](http://bit.ly/1MM8eTw) documentation.
- Applying temporary patches to objects for testing; see the [unittest.mock.patch](http://bit.ly/1MM8imk) function.

The standard library also includes the contextlib utilities, covered next.

<span id="page-933-0"></span>
## The contextlib Utilities

Before rolling your own context manager classes, take a look at "contextlib — Utilities for with[-statement contexts"](http://bit.ly/1HGqZpJ) in *The Python Standard Library*. Maybe what you are about to build already exists, or there is a class or some callable that will make your job easier.

Besides the redirect\_stdout context manager mentioned in [Example 18-3](#page-930-0), redirect\_stderr was added in Python 3.5—it does the same as the former, but for output directed to stderr.

The contextlib package also includes: *closing*

A function to build context managers out of objects that provide a close() method but don't implement the \_\_enter\_\_/\_\_exit\_\_ interface.

## suppress

A context manager to temporarily ignore exceptions given as arguments.

## nullcontext

A context manager wrapper that does nothing, to simplify conditional logic around objects that may or may not implement a suitable context manager (since Python 3.7).

The contextlib module provides classes and a decorator that are more widely applicable than those above:

## @contextmanager

A decorator that lets you build a context manager from a simple generator function, instead of creating a class and implementing the interface. See ["Using @contextmanager"](#page-935-0).

## AbstractContextManager

An ABC that formalizes the context manager interface, and makes it a bit easier to create context manager classes by subclassing (since Python 3.6).

## ContextDecorator

A base class for defining class-based context managers that can also be used as function decorators, running the entire function within a managed context.

## ExitStack

A context manager that lets you enter a variable number of context managers. When the with block ends, ExitStack calls the stacked context managers' \_\_exit\_\_ methods in LIFO order (last entered, first exited). Use this class when you don't know beforehand how many context managers you need to enter in your with block; for example, when opening all files from an arbitrary list of files at the same time.

With Python 3.7, contextlib added AbstractAsyncContextManager, @asynccontextmanager, and AsyncExitStack. They are similar to the equivalent utilities without the async part of the name, but designed for use with the new async with statement, covered in [Chapter 22](029-chapter-22-asynchronous-programming.md#page-1122-0).

The most widely used of these utilities is surely the @contextmanager decorator, so it deserves more attention. That decorator is also intriguing because it shows a use for the yield statement unrelated to iteration. This paves the way to the concept of a coroutine, the theme of the next chapter.

<span id="page-935-0"></span>
## Using @contextmanager

from [Example 18-3](#page-930-0) with a generator function.

| The @contextmanager decorator reduces the boilerplate of creating a<br>context manager: instead of writing a whole class with<br>enter/exit methods, you just implement a generator with a<br>single yield that should produce whatever you want theenter<br>method to return.                             |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| In a generator decorated with @contextmanager, yield splits the<br>body of the function in two parts: everything before the yield will be<br>executed at the beginning of the with block when the interpreter calls<br>enter; the code after yield will run whenexit is called at<br>the end of the block. |
| Here is an example. Example 18-5 replaces the LookingGlass class                                                                                                                                                                                                                                           |

<span id="page-936-0"></span>
## Example 18-5. mirror\_gen.py: a context manager implemented with a generator

```
import contextlib
```

```
@contextlib.contextmanager 
def looking_glass():
 import sys
 original_write = sys.stdout.write 
 def reverse_write(text): 
 original_write(text[::-1])
 sys.stdout.write = reverse_write 
 yield 'JABBERWOCKY' 
 sys.stdout.write = original_write
```

- Apply the contextmanager decorator.
- Preserve original sys.stdout.write method.
- Define custom reverse\_write function; original\_write will be available in the closure.
- Replace sys.stdout.write with reverse\_write.
- Yield the value that will be bound to the target variable in the as clause of the with statement. This function pauses at this point while the body of the with executes.
- When control exits the with block in any way, execution continues after the yield; here the original sys.stdout.write is restored.

[Example 18-6](#page-936-1) shows the looking\_glass function in operation.

<span id="page-936-1"></span>
## Example 18-6. Test driving the looking\_glass context manager function

```
 >>> from mirror_gen import looking_glass
 >>> with looking_glass() as what: 
 ... print('Alice, Kitty and Snowdrop')
 ... print(what)
```

```
 ...
 pordwonS dna yttiK ,ecilA
 YKCOWREBBAJ
 >>> what
 'JABBERWOCKY'
```

The only difference from [Example 18-2](#page-929-0) is the name of the context manager: looking\_glass instead of LookingGlass.

Essentially the contextlib.contextmanager decorator wraps the function in a class that implements the \_\_enter\_\_ and \_\_exit\_\_ methods. [4](#page-952-3)

<span id="page-937-0"></span>The \_\_enter\_\_ method of that class:

- 1. Invokes the generator function and holds on to the generator object —let's call it gen.
- 2. Calls next(gen) to make it run to the yield keyword.
- 3. Returns the value yielded by next(gen), so it can be bound to a target variable in the with/as form.

When the with block terminates, the \_\_exit\_\_ method:

- 1. Checks an exception was passed as exc\_type; if so, gen.throw(exception) is invoked, causing the exception to be raised in the yield line inside the generator function body.
- 2. Otherwise, next(gen) is called, resuming the execution of the generator function body after the yield.

[Example 18-5](#page-936-0) has a serious flaw: if an exception is raised in the body of the with block, the Python interpreter will catch it and raise it again in the yield expression inside looking\_glass. But there is no error handling there, so the looking\_glass function will abort without ever restoring the original sys.stdout.write method, leaving the system in an invalid state.

[Example 18-7](#page-938-0) adds special handling of the ZeroDivisionError [exception, making it functionally equivalent to the class-based Example 18-](#page-930-0) 3.

<span id="page-938-0"></span>*Example 18-7. mirror\_gen\_exc.py: generator-based context manager [implementing exception handling—same external behavior as Example 18-](#page-930-0) 3*

```
import contextlib
@contextlib.contextmanager
def looking_glass():
 import sys
 original_write = sys.stdout.write
 def reverse_write(text):
 original_write(text[::-1])
 sys.stdout.write = reverse_write
 msg = '' 
 try:
 yield 'JABBERWOCKY'
 except ZeroDivisionError: 
 msg = 'Please DO NOT divide by zero!'
 finally:
 sys.stdout.write = original_write 
 if msg:
 print(msg)
```

- Create a variable for a possible error message; this is the first change in relation to [Example 18-5](#page-936-0).
- Handle ZeroDivisionError by setting an error message.
- Undo monkey-patching of sys.stdout.write.
- Display error message, if it was set.

Recall that the \_\_exit\_\_ method tells the interpreter that it has handled the exception by returning True; in that case, the interpreter suppresses the exception. On the other hand, if \_\_exit\_\_ does not explicitly return a

value, the interpreter gets the usual None, and propagates the exception. With @contextmanager, the default behavior is inverted: the \_\_exit\_\_ method provided by the decorator assumes any exception sent into the generator is handled and should be suppressed. You must explicitly re-raise an exception in the decorated function if you don't want @contextmanager to suppress it. [5](#page-952-4) [6](#page-952-5)

<span id="page-939-3"></span>
<span id="page-939-2"></span>
<span id="page-939-1"></span>
## TIP

Having a try/finally (or a with block) around the yield is an unavoidable price of using @contextmanager, because you never know what the users of your context manager are going to do inside their with block. [7](#page-952-6)

An interesting real-life example of @contextmanager outside of the standard library is Martijn Pieters' [in-place file rewriting context manager](http://bit.ly/1MM96aR). [Example 18-8](#page-939-0) shows how it's used.

<span id="page-939-0"></span>*Example 18-8. A context manager for rewriting files in place*

```
import csv
with inplace(csvfilename, 'r', newline='') as (infh, outfh):
 reader = csv.reader(infh)
 writer = csv.writer(outfh)
 for row in reader:
 row += ['new', 'columns']
 writer.writerow(row)
```

The inplace function is a context manager that gives you two handles infh and outfh in the example—to the same file, allowing your code to read and write to it at the same time. It's easier to use than the standard library's [fileinput.input](http://bit.ly/1HGr6Sq) function (which also provides a context manager, by the way).

If you want to study Martijn's inplace source code (listed in [the post\)](http://bit.ly/1MM96aR), find the yield keyword: everything before it deals with setting up the context, which entails creating a backup file, then opening and yielding

references to the readable and writable file handles that will be returned by the \_\_enter\_\_ call. The \_\_exit\_\_ processing after the yield closes the file handles and restores the file from the backup if something went wrong.

Note that the use of yield in a generator used with the @contextmanager decorator has nothing to do with iteration. In the examples shown in this section, the generator function is operating more like a coroutine: a procedure that runs up to a point, then suspends to let the client code run until the client wants the coroutine to proceed with its job. [Chapter 19](026-chapter-19-classic-coroutines.md#page-953-0) is all about coroutines.

<span id="page-940-0"></span>
## Pattern Matching: a Case Study

XXX missing introduction

Before looking at the Python code, let's learn the bare minimum of Scheme so you can make sense of this case study—in case you haven't studied Scheme or Lisp before.

<span id="page-940-3"></span>
## Scheme Syntax

Everything in Scheme is an expression—there is no distinction between expressions and statements, like we have in Python.

Scheme has no infix operators. Expressions with arithmetic and logic operators all use prefix notation like (+ x 13). The same syntax is used for function calls—e.g. (gcd x 13)—and special forms—e.g. (define x 13), which we'd write as x = 13 in Python. [8](#page-952-7)

<span id="page-940-2"></span>Here is a simple example in Scheme:

<span id="page-940-1"></span>*Example 18-9. Greatest common divisor in Scheme. The last result of this code is 9, the GCD of 18 and 45.*

```
(define (mod m n)
 (- m (* n (// m n))))
(define (gcd m n)
```

```
 (if (= n 0)
 m
 (gcd n (mod m n))))
(gcd 18 45)
```

[Example 18-9](#page-940-1) shows two function definitions—mod and gcd—and a call to gcd. Here is the same code in Python (quicker than an English explanation):

*Example 18-10. Same as [Example 18-9,](#page-940-1) written in Python.*

```
def mod(m, n):
 return m - (m // n * n)
def gcd(m, n):
 if n == 0:
 return m
 else:
 return gcd(m, mod(m, n))
gcd(18, 45) # returns 9
```

At its core, Scheme has no iterative control flow forms like while or for. [Iteration is always implemented with recursion, as you saw in Example 18-](#page-940-1) 9. Scheme implementations are required to implement tail call optimization (TCO) to make iteration through recursion efficient and practical. Norvig's *lispy.py* interpreter has TCO, but his simpler *lis.py* does not.

<span id="page-941-0"></span>
## The Parser

The first part of Norvig's code is a parser that reads a string of Scheme source code, splits it into syntactic tokens, and returns a Python object representing the code.

Here are some examples from a doctest:

*Example 18-11. parse takes a string and returns numbers, symbols, and/or lists.*

```
>>> parse('1.5') 
1.5
>>> parse('set!') 
'set!'
```

```
>>> parse('(gcd 18 44)') 
['gcd', 18, 44]
>>> parse('(- m (* n (// m n)))') 
['-', 'm', ['*', 'n', ['//', 'm', 'n']]]
```

- A token that looks like a number is parsed as a number—float or int.
- Anything else that doesn't start with '(' is parsed as a *symbol*—a str to be used as an identifier.
- Expressions inside '(' and ')' are parsed as lists of numbers or symbols or…
- …nested lists that may contain numbers, symbols, and more nested lists.

The simplest tokens—numbers and symbols—are called *atoms*. Using Python terminology, the output of parse is an AST (Abstract Syntax Tree): the nested lists form a tree-like structure, where the outermost list is the trunk, the inner lists are the branches, and the atoms are the leaves.

<span id="page-942-1"></span>
## An Expression Evaluator

Now we are ready to see the beauty of pattern matching applied to interpreting Scheme expressions. The evaluate function in Example 18- [12 is the most important part of the interpreter.](#page-942-0)

<span id="page-942-0"></span>*Example 18-12. evaluate takes an expression from parse and computes its value.*

```
def evaluate(exp: Expression, env: Environment) -> Any:
 "Evaluate an expression in an environment."
 match exp:
 case int(x) | float(x):
 return x
 case Symbol(var):
 return env[var]
 case []:
 return []
 case ['quote', exp]:
```

```
 return exp
 case ['if', test, consequence, alternative]:
 if evaluate(test, env):
 return evaluate(consequence, env)
 else:
 return evaluate(alternative, env)
 case ['define', Symbol(var), value_exp]:
 env[var] = evaluate(value_exp, env)
 case ['define', [Symbol(name), *parms], *body]:
 env[name] = Procedure(parms, body, env)
 case ['lambda', [*parms], *body]:
 return Procedure(parms, body, env)
 case [op, *args]:
 proc = evaluate(op, env)
 values = [evaluate(arg, env) for arg in args]
 return proc(*values)
 case _:
 raise SyntaxError(repr(exp))
```

The two arguments of evaluate are:

*exp*

numbers, symbols or lists returned by parse;

*env*

an envirnoment—a mapping of names to values.

When the interpreter makes the initial call to evaluate, env gets a dict with dozens of names mapped to Python functions. This is a small sample of items in the initial environment:

```
{
 '+': op.add,
 '-': op.sub,
 'abs': abs,
 'append': lambda *args: list(itertools.chain(*args)),
 'length': len,
 'number?': lambda x: isinstance(x, (int, float)),
}
```

The body of evaluate is a single match statement with an expression exp as the subject. The 10 case patterns express the syntax and semantics of Scheme with amazing clarity.

Let's study each case in turn. On top of each case, I added a sample of Scheme code that would produce a subject exp matching that pattern, and a Python object that could be the value of that expression.

```
 # 1.5
 case int(x) | float(x): 
 return x
```

If subject is an int or float, just return it.

```
 # count
 case Symbol(var): 
 return env[var]
```

If subject is a Symbol (a str used as an identifier), get its value from env and return it.

Now, the sequence patterns:

```
 # ()
 case []: 
 return []
```

If subject is an empty list, return it.

```
 # (quote (1.1 is not 1))
 case ['quote', exp]: 
 return exp
```

If subject is a list starting with 'quote', followed by one exp, then return exp without evaluating it. Given the Scheme code in the

comment, the Python object returned would be [1.1, 'is', 'not', 1].

```
 # (if (> n 0) n (- 0 n))
 case ['if', test, consequence, alternative]: 
 if evaluate(test, env):
 return evaluate(consequence, env)
 else:
 return evaluate(alternative, env)
```

If subject is a list starting with 'if' followed by three expressions, then evaluate test; if true, evaluate consequence and return it; otherwise, evaluete alternative and return it.

```
 # (define half (/ 1 2))
 case ['define', Symbol(var), value_exp]: 
 env[var] = evaluate(value_exp, env)
```

If subject is a list starting with 'define', followed by a symbol var and an expression, then evaluate the expression and add its value to env, using the var as key.

The next case also matches a sequence starting with define, but with a different structure.

```
 # (define (double x) (* x 2))
 case ['define', [Symbol(name), *parms], body]: 
 env[name] = Procedure(parms, body, env)
```

If subject is a list starting with 'define' and two other items, the first being a list starting with a symbol name, followed by 0 or more parameter names, the second being an expression body, then create a new Procedure with those parameters, body, and the current environment, and add it to the env using name as the key.

The previous case is a named function definition. The next is an anonymous function definition.

```
 # (lambda (a b) (* (/ a b) 100))
 case ['lambda', [*parms], body]: 
 return Procedure(parms, body, env)
```

If subject is a list starting with 'lambda' and two other items, the first being a list of parameter names, the second being an expression body, then create a new Procedure with those parameters, body, and the current environment, and return it.

Now we get to a function call.

```
 # (gcd 210 84)
 case [op, *args]: 
 proc = evaluate(op, env)
 values = [evaluate(arg, env) for arg in args]
 return proc(*values)
```

If subject is a list with one or more items, then evaluate the first to obtain a function proc, evaluate each of the remaining items to build a list of argument values, then call proc with the values as separate arguments.

```
 case _: 
 raise SyntaxError(repr(exp))
```

If subject did not match any previous pattern, it matches the wildcard \_. Raise SyntaxError.

To wrapt up the coverage of pattern matching in this chapter, let's talk about OR-patterns.

<span id="page-946-0"></span>
## OR-patterns

## NOTE

An OR-pattern can be built from any other patterns, not only class patterns.

In [Example 2-11](007-chapter-2-an-array-of-sequences.md#page-86-0) we saw part of Peter Norvig's *lis.py* evaluate function refactored to use match/case. Here are the first case clauses of that function, which I previously ommitted:

<span id="page-947-0"></span>*Example 18-13. Pattern matching with match/case—requires Python ≥ 3.10.*

```
def evaluate(exp, env):
 "Evaluate an expression in an environment."
 match exp:
 case int(x) | float(x): 
 return x
 case Symbol(var): 
 return env[var]
 case ...: # sequence patterns omitted
 ...
 case _:
 raise SyntaxError(repr(exp))
```

- Match if subject is an instance of int or float.
- Match is subject is an instance of Symbol—which is an alias for str in *lis.py*.

A series of patterns separated by | is an [OR-pattern:](https://www.python.org/dev/peps/pep-0634/#or-patterns) it succeeds if any of the subpatterns succeed. All subpatterns must use the same variables. This restriction is necessary to ensure that the case body can rely on all the variables if there is a match.

## WARNING

In the context of a case clause, the | operator has a special meaning. It does not trigger the \_\_or\_\_ special method which handles expressions like a | b in other contexts, where it is overloaded to perform operations such as set union or integer bitwise-or.

<span id="page-948-0"></span>[Example 18-13](#page-947-0) illustrates the simplest form of class pattern, exemplified by int(x), which matches if isinstance(x, int) returns True. XXX

## Chapter Summary

This chapter started easily enough with discussion of else blocks in for, while, and try statements. Once you get used to the peculiar meaning of the else clause in these statements, I believe else can clarify your intentions.

We then covered context managers and the meaning of the with statement, quickly moving beyond its common use to automatically close opened files. We implemented a custom context manager: the LookingGlass class with the \_\_enter\_\_/\_\_exit\_\_ methods, and saw how to handle exceptions in the \_\_exit\_\_ method. A key point that Raymond Hettinger made in his PyCon US 2013 keynote is that with is not just for resource management, but it's a tool for factoring out common setup and teardown code, or any pair of operations that need to be done before and after another procedure ([slide 21, What Makes Python Awesome?\)](http://bit.ly/1MM9pCm).

Finally, we reviewed functions in the contextlib standard library module. One of them, the @contextmanager decorator, makes it possible to implement a context manager using a simple generator with one yield—a leaner solution than coding a class with at least two methods. We reimplemented the LookingGlass as a looking\_glass generator function, and discussed how to do exception handling when using @contextmanager.

The @contextmanager decorator is an elegant and practical tool that brings together three distinctive Python features: a function decorator, a generator, and the with statement.

<span id="page-949-0"></span>
## Further Reading

[Chapter 8, "Compound Statements,"](http://bit.ly/1MMa1YB) in *The Python Language Reference* says pretty much everything there is to say about else clauses in if, for, while, and try statements. Regarding Pythonic usage of try/except, with or without else, Raymond Hettinger has a brilliant answer to the

question ["Is it a good practice to use try-except-else in Python?"](http://bit.ly/1MMa2Mp) in StackOverflow. Alex Martelli's *[Python in a Nutshell, 2E](http://shop.oreilly.com/product/9780596100469.do)* (O'Reilly), has a chapter about exceptions with an excellent discussion of the EAFP style, crediting computing pioneer Grace Hopper for coining the phrase "It's easier to ask forgiveness than permission."

The *Python Standard Library*, Chapter 4, "Built-in Types," has a section devoted to [Context Manager Types](http://bit.ly/1MMacTS). The \_\_enter\_\_/\_\_exit\_\_ special methods are also documented in *The Python Language Reference* in "3.3.8. [With Statement Context Managers". Context managers were introduced in](http://bit.ly/1MMab2e) [PEP 343 — The "with" Statement.](https://www.python.org/dev/peps/pep-0343/) This PEP is not easy reading because it spends a lot of time covering corner cases and arguing against alternative proposals. That's the nature of PEPs.

Raymond Hettinger highlighted the with statement as a "winning language feature" in his [PyCon US 2013 keynote](http://bit.ly/1MM9pCm). He also showed some interesting [applications of context managers in his talk "Transforming Code into](http://bit.ly/1MMagmB) Beautiful, Idiomatic Python" at the same conference.

Jeff Preshing' blog post "The Python with [Statement by Example"](http://bit.ly/1MMakmm) is interesting for the examples using context managers with the pycairo graphics library.

Beazley and Jones devised context managers for very different purposes in their *[Python Cookbook, 3E](http://shop.oreilly.com/product/0636920027072.do)* (O'Reilly). "Recipe 8.3. Making Objects Support the Context-Management Protocol" implements a LazyConnection class whose instances are context managers that open and close network connections automatically in with blocks. "Recipe 9.22. Defining Context Managers the Easy Way" introduces a context manager for timing code, and another for making transactional changes to a list object: within the with block, a working copy of the list instance is made, and all changes are applied to that working copy. Only when the with block completes without an exception, the working copy replaces the original list. Simple and ingenious.

## SOAPBOX

## Factoring Out the Bread

In his PyCon US 2013 keynote, ["What Makes Python Awesome,"](http://pyvideo.org/video/1669/keynote-3) Raymond Hettinger says when he first saw the with statement proposal he thought it was "a little bit arcane." Initially, I had a similar reaction. PEPs are often hard to read, and PEP 343 is typical in that regard.

Then—Hettinger told us—he had an insight: subroutines are the most important invention in the history of computer languages. If you have sequences of operations like A;B;C and P;B;Q, you can factor out B in a subroutine. It's like factoring out the filling in a sandwich: using tuna with different breads. But what if you want to factor out the bread, to make sandwiches with wheat bread, using a different filling each time? That's what the with statement offers. It's the complement of the subroutine. Hettinger went on to say:

*The with statement is a very big deal. I encourage you to go out and take this tip of the iceberg and drill deeper. You can probably do profound things with the with statement. The best uses of it have not been discovered yet. I expect that if you make good use of it, it will be copied into other languages and all future languages will have it. You can be part of discovering something almost as profound as the invention of the subroutine itself.*

Hettinger admits he is overselling the with statement. Nevertheless, it is a very useful feature. When he used the sandwich analogy to explain how with is the complement to the subroutine, many possibilities opened up in my mind.

If you need to convince anyone that Python is awesome, you should watch Hettinger's keynote. The bit about context managers is from 23:00 to 26:15. But the entire keynote is excellent.

- <span id="page-952-0"></span>[1](#page-923-0) PyCon US 2013 keynote: ["What Makes Python Awesome"](http://pyvideo.org/video/1669/keynote-3); the part about with starts at 23:00 and ends at 26:15.
- <span id="page-952-1"></span>[2](#page-928-1) with blocks don't define a new scope, as functions and modules do.
- <span id="page-952-2"></span>[3](#page-932-1) The three arguments received by self are exactly what you get if you call [sys.exc\\_info\(\)](http://bit.ly/1MM82Uc) in the finally block of a try/finally statement. This makes sense, considering that the with statement is meant to replace most uses of try/finally, and calling sys.exc\_info() was often necessary to determine what clean-up action would be required.
- <span id="page-952-3"></span>[4](#page-937-0) The actual class is named \_GeneratorContextManager. If you want to see exactly how it works, read its [source code](http://bit.ly/1MM8AJJ) in *Lib/contextlib.py* in the Python 3.4 distribution.
- <span id="page-952-4"></span>[5](#page-939-1) [The exception is sent into the generator using the](026-chapter-19-classic-coroutines.md#page-967-0) throw method, covered in "Coroutine Termination and Exception Handling".
- <span id="page-952-5"></span>[6](#page-939-2) This convention was adopted because when context managers were created, generators could not return values, only yield. They now can, as explained in "Returning a Value from a [Coroutine". As you'll see, returning a value from a generator does involve an exception.](026-chapter-19-classic-coroutines.md#page-971-0)
- <span id="page-952-6"></span>[7](#page-939-3) This tip is quoted literally from a comment by Leonardo Rochael, one of the tech reviewers for this book. Nicely said, Leo!
- <span id="page-952-7"></span>[8](#page-940-2) People complain about the overuse of parenthesis, but the main readability problem of Lisp and its dialects is using the same (foo ...) syntax for function calls and special forms like (define ...), (if ...), and macros that don't behave at all like function calls.
