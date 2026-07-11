<span id="page-67-2"></span>
<span id="page-67-1"></span>
<span id="page-67-0"></span>
# Chapter 5: Tools


What tools do you need when you work with legacy code? You need an editor (or an IDE) and your build system, but you also need a testing framework. If there are refactoring tools for your language, they can be very helpful as well.

In this chapter, I describe some of the tools that are currently available and the role that they can play in your legacy code work.

## Automated Refactoring Tools

Refactoring by hand is fine, but when you have a tool that does some refactoring for you, you have a real time saver. In the 1990s, Bill Opdyke started work on a C++ refactoring tool as part of his thesis work on refactoring. Although it never became commercially available, to my knowledge, his work inspired many other efforts in other languages. One of the most significant was the Smalltalk refactoring browser developed by John Brant and Don Roberts at the University of Illinois. The Smalltalk refactoring browser supported a very large number of refactorings and has served as a state-of-the-art example of automated refactoring technology for a long while. Since then, there have been many attempts to add refactoring support to various languages in wider use. At the time of this writing, many Java refactoring tools are available; most are integrated into IDEs, but a few are not. There are also refactoring tools for Delphi and some relatively new ones for C++. Tools for C# refactoring are under active development at the time of this writing.

With all of these, tools it seems that refactoring should be much easier. It is, in some environments. Unfortunately, the refactoring support in many of these tools varies. Let's remember what refactoring is again. Here is Martin Fowler's definition from *Refactoring: Improving the Design of Existing Code* (Addison-Wesley 1999):

**refactoring** (n.). A change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its existing behavior.

**Tools**

**Automated Refactoring Tools**

<span id="page-68-0"></span>A change is a refactoring only if it doesn't change behavior. Refactoring tools should verify that a change does not change behavior, and many of them do. This was a cardinal rule in the Smalltalk refactoring browser, Bill Opdyke's work, and many of the early Java refactoring tools. At the fringes, however, some tools don't really check—and if they don't check, you could be introducing subtle bugs when you refactor.

It pays to choose your refactoring tools with care. Find out what the tool developers say about the safety of their tool. Run your own tests. When I encounter a new refactoring tool, I often run little sanity checks. When you attempt to extract a method and give it the name of a method that already exists in that class, does it flag that as an error? What if it is the name of a method in a base class—does the tool detect that? If it doesn't, you could mistakenly override a method and break code.

In this book, I discuss work with and without automated refactoring support. In the examples, I mention whether I am assuming the availability of a refactoring tool.

In all cases, I assume that the refactorings supplied by the tool preserve behavior. If you discover that the ones supplied by your tool don't preserve behavior, don't use the automated refactorings. Follow the advice for cases in which you don't have a refactoring tool—it will be safer.

### Tests and Automated Refactoring

When you have a tool that does refactorings for you, it's tempting to believe that you don't have to write tests for the code you are about to refactor. In some cases, this is true. If your tool performs safe refactorings and you go from one automated refactoring to another without doing any other editing, you can assume that your edits haven't changed behavior. However, this isn't always the case.

```
Here is an example:
public class A {
 private int alpha = 0;
 private int getValue() {
 alpha++;
 return 12;
 }
 public void doSomething() {
 int v = getValue();
 int total = 0;
 for (int n = 0; n < 10; n++) {
  total += v;
 }
 }
}
```

<span id="page-69-1"></span>In at least two Java refactoring tools, we can use a refactoring to remove the v variable from doSomething. After the refactoring, the code looks like this:

```
public class A {
 private int alpha = 0;
 private int getValue() {
 alpha++;
 return 12;
 }
 public void doSomething() {
 int total = 0;
 for (int n = 0; n < 10; n++) {
 total += getValue();
 }
 }
```

<span id="page-69-0"></span>See the problem? The variable was removed, but now the value of alpha is incremented 10 times rather than 1. This change clearly didn't preserve behavior.

It is a good idea to have tests around your code before you start to use automated refactorings. You can do some automated refactoring without tests, but you have to know what the tool is checking and what it isn't. When I start to use a new tool, the first thing that I do is put its support for extracting methods through its paces. If I can trust it well enough to use it without tests, I can get the code into a much more testable state.

**Mock Objects**

## Mock Objects

One of the big problems that we confront in legacy code work is dependency. If we want to execute a piece of code by itself and see what it does, often we have to break dependencies on other code. But it's hardly ever that simple. If we remove the other code, we need to have something in its place that supplies the right values when we are testing so that we can exercise our piece of code thoroughly. In object-oriented code, these are often called mock objects.

Several mock object libraries are freely available. The web site [www.m](https://www.mockobjects.com)ock[objects.com](www.mockobjects.com) is a good place to find references for most of them.

<span id="page-70-1"></span>
<span id="page-70-0"></span>
## Unit-Testing Harnesses

Testing tools have a long and varied history. Not a year goes by that I don't run into four or five teams that have bought some expensive license-per-seat testing tool that ends up not living up to its price. In fairness to tool vendors, testing is a tough problem, and people are often seduced by the idea that they can test through a GUI or web interface without having to do anything special to their application. It can be done, but it is usually more work than anyone on a team is prepared to admit. In addition, a user interface often isn't the best place to write tests. UIs are often volatile and too far from the functionality being tested. When UI-based tests fail, it can be hard to figure out why. Regardless, people often spend considerable money trying to do all of their testing with those sorts of tools.

**Unit-Testing Harnesses**

The most effective testing tools I've run across have been free. The first one is the xUnit testing framework. Originally written in Smalltalk by Kent Beck and then ported to Java by Kent Beck and Erich Gamma, xUnit is a small, powerful design for a unit-testing framework. Here are its key features:

- It lets programmers write tests in the language they are developing in.
- All tests run in isolation.
- Tests can be grouped into suites so that they can be run and rerun on demand.

The xUnit framework has been ported to most major languages and quite a few small, quirky ones.

The most revolutionary thing about xUnit's design is its simplicity and focus. It allows us to write tests with little muss and fuss. Although it was originally designed for unit testing, you can use it to write larger tests because xUnit really doesn't care how large or small a test is. If the test can be written in the language you are using, xUnit can run it.

In this book, most of the examples are in Java and C++. In Java, JUnit is the preferred xUnit harness, and it looks very much like most of the other xUnits. In C++, I often use a testing harness I wrote named CppUnitLite. It looks quite a bit different, and I describe it in this chapter also. By the way, I'm not slighting the original author of CppUnit by using CppUnitLite. I was that guy a long time ago, and I discovered only after I released CppUnit that it could be quite a bit smaller, easier to use, and far more portable if it used some C idioms and only a bare subset of the C++ language.

<span id="page-71-0"></span>
### JUnit

In JUnit, you write tests by subclassing a class named TestCase.

```
import junit.framework.*;
public class FormulaTest extends TestCase {
 public void testEmpty() {
 assertEquals(0, new Formula("").value());
 }
 public void testDigit() {
 assertEquals(1, new Formula("1").value());
 }
```

Each method in a test class defines a test if it has a signature of this form: void testXXX(), where XXX is the name you want to give the test. Each test method can contain code and assertions. In the previous testEmpty method, there is code to create a new Formula object and call its value method. There is also assertion code that checks to see if that value is equal to 0. If it is, the test passes. If it isn't, the test fails.

In a nutshell, here is what happens when you run JUnit tests. The JUnit test runner loads a test class like the one shown previously, and then it uses reflection to find all of the test methods. What it does next is kind of sneaky. It creates a completely separate object for each one of those test methods. From the previous code, it creates two of them: an object whose only job is to run the testEmpty method, and an object whose only job is to run the testDigit object. If you are wondering what the classes of the objects are, in both cases, it is the same: FormulaTest. Each object is configured to run exactly one of the test methods on FormulaTest. The key thing is that we have a completely separate object for each method. There is no way that they can affect each other. Here is an example.

```
public class EmployeeTest extends TestCase {
 private Employee employee;
 protected void setUp() {
 employee = new Employee("Fred", 0, 10);
 TDate cardDate = new TDate(10, 10, 2000);
 employee.addTimeCard(new TimeCard(cardDate,40));
 }
 public void testOvertime() {
 TDate newCardDate = new TDate(11, 10, 2000);
 employee.addTimeCard(new TimeCard(newCardDate, 50));
 assertTrue(employee.hasOvertimeFor(newCardDate));
```

**Unit-Testing Harnesses**

**Unit-Testing Harnesses**

```
 }
 public void testNormalPay() {
 assertEquals(400, employee.getPay());
 }
}
```

In the EmployeeTest class, we have a special method named setUp. The setUp method is defined in TestCase and is run in each test object before the test method is run. The setUp method allows us to create a set of objects that we'll use in a test. That set of objects is created the same way before each test's execution. In the object that runs testNormalPay, an employee created in setUp is checked to see if it calculates pay correctly for one timecard, the one added in setUp. In the object that runs testOvertime, an employee created in setUp for that object gets an additional timecard, and there is a check to verify that the second timecard triggers an overtime condition. The setUp method is called for each object of the class EmployeeTest, and each of those objects gets its own set of objects created via setUp. If you need to do anything special after a test finishes executing, you can override another method named tearDown, defined in TestCase. It runs after the test method for each object

When you first see an xUnit harness, it is bound to look a little strange. Why do test-case classes have setUp and tearDown at all? Why can't we just create the objects we need in the constructor? Well, we could, but remember what the test runner does with test case classes. It goes to each test case class and creates a set of objects, one for each test method. That is a large set of objects, but it isn't so bad if those objects haven't allocated what they need yet. By placing code in setUp to create what we need just when we need it, we save quite a bit on resources. In addition, by delaying setUp, we can also run it at a time when we can detect and report any problems that might happen during setup.

#### CppUnitLite

When I did the initial port of CppUnit, I tried to keep it as close as I could to JUnit. I figured it would be easier for people who'd seen the xUnit architecture before, so it seemed to be the better thing to do. Almost immediately, I ran into a series of things that were hard or impossible to implement cleanly in C++ because of differences in C++ and Java's features. The primary issue was C++'s lack of reflection. In Java, you can hold on to a reference to a derived class's methods, find methods at runtime, and so on. In C++, you have to write code to register the method you want to access at runtime. As a result, CppUnit became a little bit harder to use and understand. You had to write your own suite function on a test class so that the test runner could run objects for individual methods.

```
Test *EmployeeTest::suite() 
 TestSuite *suite = new TestSuite;
 suite.addTest(new TestCaller<EmployeeTest>("testNormalPay",
 testNormalPay));
 suite.addTest(new TestCaller<EmployeeTest>("testOvertime",
 testOvertime));
 return suite;
```

Needless to say, this gets pretty tedious. It is hard to maintain momentum writing tests when you have to declare test methods in a class header, define them in a source file, and register them in a suite method. A variety of macro schemes can be used to get past these issues, but I choose to start over. I ended up with a scheme in which someone could write a test just by writing this source file:

```
#include "testharness.h"
#include "employee.h"
#include <memory>
using namespace std;
TEST(testNormalPay,Employee)
 auto_ptr<Employee> employee(new Employee("Fred", 0, 10));
 LONGS_EQUALS(400, employee->getPay());
}
```

This test used a macro named LONGS\_EQUAL that compares two long integers for equality. It behaves the same way that assertEquals does in JUnit, but it's tailored for longs.

The TEST macro does some nasty things behind the scenes. It creates a subclass of a testing class and names it by pasting the two arguments together (the name of the test and the name of the class being tested). Then it creates an instance of that subclass that is configured to run the code in braces. The instance is static; when the program loads, it adds itself to a static list of test objects. Later a test runner can rip through the list and run each of the tests.

After I wrote this little framework, I decided not to release it because the code in the macro wasn't terribly clear, and I spend a lot of time convincing people to write clearer code. A friend of mine, Mike Hill, ran into some of the same issues before we met and created a Microsoft-specific testing framework called TestKit that handled registration the same way. Emboldened by Mike, I started to reduce the number of late C++ features used in my little framework, and then I released it. (Those issues had been a big issue in CppUnit. Nearly **Unit-Testing Harnesses**

<span id="page-74-0"></span>every day I received e-mail from people who couldn't use templates or the standard library, or who had exceptions with their C++ compiler.)

Both CppUnit and CppUnitLite are adequate as testing harnesses. Tests written using CppUnitLite are a little briefer, so I use it for the C++ examples in this book.

#### NUnit

End Class

Imports NUnit.Framework

NUnit is a testing framework for the .NET languages. You can write tests for C# code, VB.NET code, or any other language that runs on the .NET platform. NUnit is very close in operation to JUnit. The one significant difference is that it uses attributes to mark test methods and test classes. The syntax of attributes depends upon the .NET language the tests are written in.

Here is an NUnit test written in VB.NET:

**Unit-Testing Harnesses**

```
<TestFixture()> Public Class LogOnTest
 Inherits Assertion
 <Test()> Public Sub TestRunValid()
 Dim display As New MockDisplay()
 Dim reader As New MockATMReader()
 Dim logon As New LogOn(display, reader)
 logon.Run()
 AssertEquals("Please Enter Card", display.LastDisplayedText)
 AssertEquals("MainMenu",logon.GetNextTransaction().GetType.Name)
 End Sub
```

<TestFixture()> and <Test()> are attributes that mark LogonTest as a test class and TestRunValid as a test method, respectively.

#### Other xUnit Frameworks

There are many ports of xUnit to many different languages and platforms. In general, they support the specification, grouping, and running of unit tests. If you need to find an xUnit port for your platform or language, go to <www.xprogramming.com>and look in the Downloads section. This site is run by Ron Jeffries, and it is the de facto repository for all of the xUnit ports.

<span id="page-75-1"></span>
<span id="page-75-0"></span>
## General Test Harnesses

The xUnit frameworks I described in the preceding section were designed to be used for unit testing. They can be used to test several classes at a time, but that sort of work is more properly the domain of FIT and Fitnesse.

### Framework for Integrated Tests (FIT)

FIT is a concise and elegant testing framework that was developed by Ward Cunningham. The idea behind FIT is simple and powerful. If you can write documents about your system and embed tables within them that describe inputs and outputs for your system, and if those documents can be saved as HTML, the FIT framework can run them as tests.

FIT accepts HTML, runs tests defined in HTML tables in it, and produces HTML output. The output looks the same as the input, and all text and tables are preserved. However, the cells in the tables are colored green to indicate values that made a test pass and red to indicate values that caused a test to fail. You also can use options to have test summary information placed in the resulting HTML.

The only thing you have to do to make this work is to customize some tablehandling code so that it knows how to run chunks of your code and retrieve results from them. Generally, this is rather easy because the framework provides code to support a number of different table types.

One of the very powerful things about FIT is its capability to foster communication between people who write software and people who need to specify what it should do. The people who specify can write documents and embed actual tests within them. The tests will run, but they won't pass. Later developers can add in the features, and the tests will pass. Both users and developers can have a common and up-to-date view of the capabilities of the system.

There is far more to FIT than I can describe here. There is more information about FIT at [http://fit.c2.com.](http://fit.c2.com)

#### Fitnesse

Fitnesse is essentially FIT hosted in a wiki. Most of it was developed by Robert Martin and Micah Martin. I worked on a little bit of it, but I dropped out to concentrate on this book. I'm looking forward to getting back to work on it soon.

**General Test Harnesses**

Fitnesse supports hierarchical web pages that define FIT tests. Pages of test tables can be run individually or in suites, and a multitude of different options make collaboration easy across a team. Fitnesse is available at [http://www.fitnesse.org.](http://www.fitnesse.org) Like all of the other testing tools described in this chapter, it is free and supported by a community of developers.

**General Test Harnesses**
