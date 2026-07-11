# Chapter 5: Toward a Catalog of Refactorings

Chapters 5 to 12 form an initial catalog of refactorings. They've grown from the notes I've made in refactoring over the last few years. This catalog is by no means comprehensive or watertight, but it should provide a solid starting point for your own refactoring work.

## Format of the Refactorings

As I describe the refactorings in this and other chapters, I use a standard format. Each refactoring has five parts, as follows:

- · I begin with a **name.** The name is important to building a vocabulary of refactorings. This is the name I use elsewhere in the book.
- · I follow the name with a short **summary** of the situation in which you need the refactoring and a summary of what the refactoring does. This helps you find a refactoring more quickly.
- · The **motivation** describes why the refactoring should be done and describes circumstances in which it shouldn't be done.
- · The **mechanics** are a concise, step-by-step description of how to carry out the refactoring.
- · The **examples** show a very simple use of the refactoring to illustrate how it works.

The summary includes a short statement of the problem that the refactoring helps you with, a short description of what you do, and a sketch that shows you a simple before and after example. Sometimes I use code for the sketch and sometimes Unified Modeling Language (UML), depending on which seems to best convey the essence of the refactoring. (All UML diagrams in this book are drawn from the implementation perspective [Fowler, UML].) If you've seen the refactoring before, the sketch should give you a good idea what the refactoring is about. If not you'll probably need to work through the example to get a better idea.

The mechanics come from my own notes to remember how to do the refactoring when I haven't done it for a while. As such they are somewhat terse, usually without explanations of why the steps are done that way. I give more expansive explanations in the example. This way the mechanics are short notes you can refer to easily when you know the refactoring but need to look up the steps (at least this is how I use them). You'll probably need to read the example when you first do the refactoring.

I've written the mechanics in such a way that each step of each refactoring is as small as possible. I emphasize the safe way of doing the refactoring, which is to take very small steps and test after every one. At work I usually take larger steps than some of the baby steps described, but if I run into a bug, I back out the step and take the smaller steps. The steps include a number of references to special cases. The steps thus also function as a checklist; I often forget these things myself.

The examples are of the laughably simple textbook kind. My aim with the example is to help explain the basic refactoring with minimal distractions, so I hope you'll forgive the simplicity. (They are certainly not examples of good business object design.) I'm sure you'll be able to apply them to your rather more complex situations. Some very simple refactorings don't have examples because I didn't think an example would add much.

In particular, remember that the examples are included only to illustrate the one refactoring under discussion. In most cases, there are still problems with the code at the end, but fixing these

problems requires other refactorings. In a few cases in which refactorings often go together, I carry examples from one refactoring to another. In most cases I leave the code as it is after the single refactoring. I do this to make each refactoring self-contained, because the primary role of the catalog is as a reference.

Don't take any of these examples as suggestions for how to design employee or order objects. These examples are there only to illustrate the refactorings, nothing more. In particular you'll notice that in the examples I use double to represent monetary values. I've done this only to make the examples simpler, as the representation is not important to the refactoring. I strongly advise against using doubles for money in commercial software. When I represent money I use the Quantity pattern [Fowler, AP].

When I was writing this book, Java 1.1; was the version that was mostly used in commercial work. Hence most of my examples use Java 1.1; this is most noticeable in my use of collections. As I reached the end of the book Java 2 became more available. I don't feel it is necessary to change all the examples, as the collections are secondary to the refactoring. However there are some refactorings, such as Encapsulate Collection, that are different in Java 2. In such cases I've explained both the Java 2 and Java 1.1 cases.

I use **boldface code** to highlight changed code where it is buried among code that has not been changed and may be difficult to spot. I do not use boldface type for all changed code, because too much defeats the purpose.

### Finding References

Many of the refactorings call for you to find all references to a method, a field, or a class. When you do this, enlist the computer to help you. By using the computer you reduce your chances of missing a reference and can usually do the search much more quickly than you would if you were simply to eyeball the code.

Most languages treat computer programs as text files. Your best help here is a suitable text search. Many programming environments allow you to text search a single file or a group of files. The access control of the feature you are looking for will tell you the range of files you need to look for.

Don't just search and replace blindly. Inspect each reference to ensure it really refers to the thing you are replacing. You can be clever with your search pattern, but I always check mentally to ensure I am making the right replacement. If you can use the same method name on different classes or methods of different signatures on the same class, there are too many chances you will get it wrong.

In a strongly typed language, you can let the compiler help you do the hunting. You can often remove the old feature and let the compiler find the dangling references. The good thing about this is that the compiler will catch every dangling reference. However, there are problems with this technique.

First, the compiler will become confused when a feature is declared more than once in an inheritance hierarchy. This is particularly true when you are looking at a method that is overridden several times. If you are working in a hierarchy, use the text search to see whether any other class declares the method you are manipulating.

The second problem is that the compiler may be too slow to be effective. If so, use a text search first; at least the compiler double-checks your work. This only works when you intend to remove

the feature. Often you want to look at all the uses to decide what to do next. In these cases you have to use the text search alternative.

A third problem is that the compiler can't catch uses of the reflection API. This is one reason to be wary of using reflection. If your system uses reflection you will have to use text searches to find things and put additional weight on your testing. In a number of places I suggest compiling without testing in situations in which the compiler usually catches errors. If you use reflection, all such bets are off, and you should test with many of these compiles.

Some Java environments, notably IBM's VisualAge, are following the example of the Smalltalk browser. With these you use menu options to find references rather than using text searches. These environments do not use text files to hold the code; they use an in-memory database. Get used to using these menu items and you will find them often superior to the unavailable text search.

### How Mature Are These Refactorings?

Any technical author has the problem of deciding when to publish. The earlier you publish, the quicker people can take advantage of the ideas. However, people are always learning. If you publish half-baked ideas too early, the ideas can be incomplete and even lead to problems for those who try to use them.

The basic technique of refactoring, taking small steps and testing often, has been well tested over many years, especially in the Smalltalk community. So I'm confident that the basic idea of refactoring is very stable.

The refactorings in this book are my notes about the refactorings I use. I have used them all. However, there is a difference between using a refactoring and boiling it down into the mechanical steps I give herein. In particular, you occasionally see problems that crop up only in very specific circumstances. I cannot say that I have had a lot of people work from these steps to spot many of these kinds of problems. As you use the refactorings, be aware of what you are doing. Remember that like working with a recipe, you have to adapt the refactorings to your circumstances. If you run into an interesting problem, drop me an e-mail, and I'll try to pass on these circumstances for others.

Another aspect to remember about these refactorings is that they are described with singleprocess software in mind. In time, I hope to see refactorings described for use with concurrent and distributed programming. Such refactorings will be different. For example, in single-process software you never need to worry how often you call a method; method calls are cheap. With distributed software, however, round trips have to be minimized. There are different refactorings for those flavors of programming, but those are topics for another book.

Many of the refactorings, such as Replace Type Code with State/Strategy and Form Template Method are about introducing patterns into a system. As the essential Gang of Four book says, "Design Patterns … provide targets for your refactorings." There is a natural relation between patterns and refactorings. Patterns are where you want to be; refactorings are ways to get there from somewhere else. I don't have refactorings for all known patterns in this book, not even for all the Gang of Four patterns [Gang of Four]. This is another aspect of the incompleteness of this catalog. I hope someday the gap will be closed.

As you use the refactorings bear in mind that they are a starting point. You will doubtless find gaps in them. I'm publishing them now because although they are not perfect, I do believe they are useful. I believe they will give you a starting point that will improve your ability to refactor efficiently. That is what they do for me.

As you use more refactorings, I hope you will start developing your own. I hope the examples herein will motivate you and give you a starting point as to how to do that. I'm conscious of the fact that there are many more refactorings than the ones I described. If you do come up with some, please drop me an e-mail.
