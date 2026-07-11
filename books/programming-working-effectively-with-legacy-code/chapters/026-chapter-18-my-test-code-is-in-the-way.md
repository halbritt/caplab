<span id="page-249-2"></span>
<span id="page-249-0"></span>
# Chapter 18: My Test Code Is in the Way

<span id="page-249-1"></span>When you first start writing unit tests, it might feel unnatural. One thing that people commonly encounter is a sense that their tests are just in the way. They browse around their project and sometimes forget whether they are looking at test code or production code. The fact that you start to end up with a lot of test code doesn't help. Unless you start to establish some conventions, you can end up swamped.

## Class Naming Conventions

One of the first things to establish is a class naming convention. Generally, you'll have at least one unit test class for each class that you work on, so it makes sense to make the unit test class name a variation of the class name. A couple of conventions are used. The most common ones are to use the word *Test* as a prefix or a suffix of the class name. So, if we have a class named DBEngine, we could call our test class TestDBEngine or DBEngineTest. Does it matter? Not really. Personally, I like the *Test* suffix convention. If you have an IDE that lists classes alphabetically, each class lines up next to its test class, and that makes it easier to navigate among them.

What other classes come up in testing? Often it's useful to fake classes for some of the collaborators of the classes in a package or directory. The convention I use for those is to use the prefix *Fake*. This groups all of them together alphabetically in a browser but somewhat away from the main classes in the package. This is convenient because often the fake classes are subclasses of classes in other directories.

One other kind of class, the *testing subclass*, is often used in testing. A *testing subclass* is a class that you write just because you want to test a class, but it has some dependencies that you want to separate out. It's the subclass that you write when you use *Subclass and Override Method (401)*. The naming convention that I use for testing subclasses is the name of the class prefixed by the **My Test Code Is in the Way**

<span id="page-250-1"></span>![](../assets/_page_250_Picture_1.jpeg)

word *Testing*. If classes in a package or directory are listed alphabetically, all of the testing subclasses are grouped together.

Here is an example listing of a directory for a small accounting package:

- CheckingAccount
- CheckingAccountTest
- FakeAccountOwner
- FakeTransaction
- SavingsAccount
- SavingsAccountTest
- TestingCheckingAccount
- TestingSavingsAccount

Notice that each production class is next to its test class. The fakes group together and the testing subclasses group together.

I'm not dogmatic about this arrangement. It works in many cases, but there are lots of variations and reasons to vary it. The key thing to remember is that ergonomics is important. It's important to consider how easy it will be to navigate back and forth between your classes and your tests.

<span id="page-250-0"></span>**Test Location**

## Test Location

So far in this chapter, I've been making the assumption that you'll place your testing code and your production code in the same directories. Generally, this is the easiest way to structure a project, but there are definitely some things that you have to consider when you decide whether to do this.

The main thing to consider is whether there are size constraints on your application's deployment. An application that runs on a server that you control might not have many constraints. If you can stand taking up essentially twice the amount of space in the deployment (the binaries for the production code and its tests), it is easy enough to keep the code and the tests in the same directories and to deploy all of the binaries.

On the other hand, if the software is a commercial product and runs on someone else's computer, the size of the deployment could be a problem. You can attempt to keep all of the testing code separate from the production source, but consider whether this affects how you navigate your code.

<span id="page-251-0"></span>Sometimes it doesn't make any difference, as this example shows. In Java, a package can span two different directories:

```
source
 com
 orderprocessing
 dailyorders
test
 com
 orderprocessing
 dailyorders
```

We can put the production classes in the dailyorders directory under source, and test classes in the dailyorders directory under test, and they can be seen as being in the same package. Some IDEs actually show you classes in those two directories in the same view so that you don't have to care where they are physically located.

In many other languages and environments, location does make a difference. If you have to navigate up and down directory structures to go back and forth between your code and its tests, it is like paying a tax as you work. People will just stop writing tests, and the work will go slower.

An alternative is to keep the production code and the test code in the same location but to use scripts or build settings to remove the test code from the deployment. If you use good naming conventions for your classes, this can work out fine.

Above all, if you choose to separate test and production code, make sure it is for a good reason. Quite often teams separate the code for aesthetic reasons: They just can't stand the idea of putting their production code and tests together. Later that navigation in the project is painful. You can get used to having tests right next to your production source. After a period of time working that way, it just feels normal.

**Test Location**

![](../assets/_page_252_Picture_0.jpeg)
