<span id="page-79-1"></span>
<span id="page-79-0"></span>
# Chapter 6: I Don't Have Much Time and I Have to Change It


Let's face facts: The book you are reading right now describes additional work—work that you probably aren't doing now and work that could make it take longer to finish some change you are about to make in your code. You might be wondering whether it's worth doing these things right now.

The truth is, the work that you do to break dependencies and write tests for your changes is going to take some time, but in most cases, you are going to end up saving time—and a lot of frustration. When? Well, it depends on the project. In some cases, you might write tests for some code that you need to change, and it takes you two hours to do that. The change that you make afterward might take 15 minutes. When you look back on the experience, you might say, "I just wasted two hours—was it worth it?" It depends. You don't know how long that work might have taken you if you hadn't written the tests. You also don't know how much time it would've taken you to debug if you made a mistake, time you could have saved if you had tests in place. I'm not only talking about the amount of time you would save if the tests caught the error, but also the amount of time tests save you when you are trying to find an error. With tests around the code, nailing down functional problems is often easier.

Let's assume the worst case. The change was simple, but we got the code around the change under test anyway; we make all of our changes correctly. Were the tests worth it? We don't know when we'll get back to that area of the code and make another change. In the best case, you go back into the code the next iteration, and you start to recoup your investment quickly. In the worst case, it's years before anyone goes back and modifies that code. But, chances are, we'll read it periodically, if only to find out whether we need to make a change there or someplace else. Would it be easier to understand if the classes were smaller and there were unit tests? Chances are, it would. But this is just the worst case. How often does it happen? Typically, changes cluster in systems. **I Don't Have Much Time and I Have to Change It**

![](../assets/_page_80_Picture_1.jpeg)

If you are changing it today, chances are, you'll have a change close by pretty soon.

When I work with teams, I often start by asking them to take part in an experiment. For an iteration, we try to make no change to the code without having tests that cover the change. If anyone thinks that they can't write a test, they have to call a quick meeting in which they ask the group whether it is possible to write the test. The beginnings of those iterations are terrible. People feel that they aren't getting all the work done that they need to. But slowly, they start to discover that they are revisiting better code. Their changes are getting easier, and they know in their gut that this is what it takes to move forward in a better way. It takes time for a team to get over that hump, but if there is one thing that I could instantaneously do for every team in the world, it would be to give them that shared experience, that experience that you can see in their faces: "Boy, we aren't going back to that again."

If you haven't had that experience yet, you need to.

Ultimately, this is going to make your work go faster, and that's important in nearly every development organization. But frankly, as a programmer, I'm just happy that it makes work much less frustrating.

When you get over the hump, life isn't completely rosy, but it is better. When you know the value of testing and you've felt the difference, the only thing that you have to deal with is the cold, mercenary decision of what to do in each particular case.

**I Don't Have Much Time and I Have to Change It**

### It Happens Someplace Every Day

You boss comes in. He says, "Clients are clamoring for this feature. Can we get it done today?"

"I don't know."

You look around. Are there tests in place? No.

You ask, "How bad do you need it?"

You know that you can make the changes inline in all 10 places where you need to change things, and it will be done by 5:00. This is an emergency right? We're going to fix this tomorrow, aren't we?

Remember, code is your house, and you have to live in it.

The hardest thing about trying to decide whether to write tests when you are under pressure is the fact that you just might not know how long it is going to take to add the feature. In legacy code, it is particularly hard to come up with estimates that are meaningful. There are some techniques that can help. Take a <span id="page-81-1"></span>look at Chapter 16, *I Don't Understand the Code Well Enough to Change It*, for details. When you don't really know how long it is going to take to add a feature and you suspect that it will be longer than the amount of time you have, it is tempting to just hack the feature in the quickest way that you can. Then if you have enough time, you can go back and do some testing and refactoring. The hard part is actually going back and doing that testing and refactoring. Before people get over the hump, they often avoid that work. It can be a morale problem. Take a look at Chapter 24, *We Feel Overwhelmed. It Isn't Going to Get Any Better*, for some constructive ways to move forward.

<span id="page-81-0"></span>So far, what I've described sounds like a real dilemma: Pay now or pay more later. Either write tests as you make your changes or live with the fact that it is going to get tougher over time. It can be that tough, but sometimes it isn't.

If you have to make a change to a class right now, try instantiating the class in a test harness. If you can't, take a look at Chapter 9, *I Can't Get This Class into a Test Harness*, or Chapter 10, *I Can't Run This Method in a Test Harness*, first. Getting the code you are changing into a test harness might be easier than you think. If you look at those sections and you decide that you really can't afford to break dependencies and get tests in place now, scrutinize the changes that you need to make. Can you make them by writing fresh code? In many cases, you can. The rest of this chapter contains descriptions of several techniques we can use to do this.

Read about these techniques and consider them, but remember that these techniques have to be used carefully. When you use them, you are adding tested code into your system, but unless you cover the code that calls it, you aren't testing its use. Use caution.

## Sprout Method

When you need to add a feature to a system and it can be formulated completely as new code, write the code in a new method. Call it from the places where the new functionality needs to be. You might not be able to get those call points under test easily, but at the very least, you can write tests for the new code. Here is an example.

```
public class TransactionGate
 public void postEntries(List entries) {
 for (Iterator it = entries.iterator(); it.hasNext(); ) {
 Entry entry = (Entry)it.next();
 entry.postDate();
```

**Sprout Method**

<span id="page-82-0"></span>![](../assets/_page_82_Picture_1.jpeg)

```
 }
 transactionBundle.getListManager().add(entries);
 }
 ...
}
```

We need to add code to verify that none of the new entries are already in transactionBundle before we post their dates and add them. Looking at the code, it seems that this has to happen at the beginning of the method, before the loop. But, actually, it could happen inside the loop. We could change the code to this:

```
public class TransactionGate
{
 public void postEntries(List entries) {
 List entriesToAdd = new LinkedList();
 for (Iterator it = entries.iterator(); it.hasNext(); ) {
 Entry entry = (Entry)it.next();
 if (!transactionBundle.getListManager().hasEntry(entry) {
 entry.postDate();
 entriesToAdd.add(entry);
 }
 }
 transactionBundle.getListManager().add(entriesToAdd);
 }
 ...
}
```

**Sprout Method**

This seems like a simple change, but it was pretty invasive. How do we know we got it right? There isn't any separation between the new code we've added and the old code. Worse, we're making the code a little muddier. We're mingling two operations here: date posting and duplicate entry detection. This method is rather small, but already it is a little less clear, and we've also introduced a temporary variable. Temporaries aren't necessarily bad, but sometimes they attract new code. If the next change that we have to make involves work with all nonduplicated entries before they are added, well, there is only one place in the code that a variable like that exists: right in this method. It will be tempting to just put that code in the method also. Could we have done this in a different way?

Yes. We can treat duplicate entry removal as a completely separate operation. We can use *test-driven development (88)* to create a new method named uniqueEntries:

```
public class TransactionGate
{
 ...
 List uniqueEntries(List entries) {
 List result = new ArrayList();
```

```
 for (Iterator it = entries.iterator(); it.hasNext(); ) {
 Entry entry = (Entry)it.next();
 if (!transactionBundle.getListManager().hasEntry(entry) {
 result.add(entry);
 }
 }
 return result;
 }
 ...
}
```

It would be easy to write tests that would drive us toward code like that for this method. When we have the method, we can go back to the original code and add the call.

```
public class TransactionGate
 ...
 public void postEntries(List entries) {
 List entriesToAdd = uniqueEntries(entries);
 for (Iterator it = entriesToAdd.iterator(); it.hasNext(); ) {
 Entry entry = (Entry)it.next();
 entry.postDate();
 }
 transactionBundle.getListManager().add(entriesToAdd);
 }
 ...
```

We still have a new temporary variable here, but the code is much less cluttered. If we need to add more code that works with the nonduplicated entries, we can make a method for that code also and call it from here. If we end up with yet more code that needs to work with them, we can introduce a class and shift all of those new methods over to it. The net effect is that we end up keeping this method small and we end up with shorter, easier-to-understand methods overall.

That was an example of *Sprout Method*. Here are the steps that you actually take:

- 1. Identify where you need to make your code change.
- 2. If the change can be formulated as a single sequence of statements in one place in a method, write down a call for a new method that will do the work involved and then comment it out. (I like to do this before I even write the method so that I can get a sense of what the method call will look like in context.)

**Sprout Method**

- <span id="page-84-0"></span>3. Determine what local variables you need from the source method, and make them arguments to the call.
- 4. Determine whether the sprouted method will need to return values to source method. If so, change the call so that its return value is assigned to a variable.
- 5. Develop the sprout method using *test-driven development (88)*.
- 6. Remove the comment in the source method to enable the call.

I recommend using *Sprout Method* whenever you can see the code that you are adding as a distinct piece of work or you can't get tests around a method yet. It is far preferable to adding code inline.

Sometimes when you want to use *Sprout Method*, the dependencies in your class are so bad that you can't create an instance of it without faking a lot of constructor arguments. One alternative is to use *Pass Null (111)*. When that won't work, consider making the sprout a public static method. You might have to pass in instance variables of the source class as arguments, but it will allow you to make your change. It might seem weird to make a static for this purpose, but it can be useful in legacy code. I tend to look at static methods on classes as a staging area. Often after you have several statics and you notice that they share some of the same variables, you are able to see that you can make a new class and move the statics over to the new class as instance methods. When they really deserve to be instance methods on the current class, they can be moved back into the class when you finally get it under test.

**Sprout Method**

### Advantages and Disadvantages

*Sprout Method* has some advantages and disadvantages. Let's look at the disadvantages first. What are the downsides of *Sprout Method*? For one thing, when you use it, in effect you essentially are saying that you are giving up on the source method and its class for the moment. You aren't going to get it under test, and you aren't going to make it better—you are just going to add some new functionality in a new method. Giving up on a method or a class is the practical choice sometimes, but it still is kind of sad. It leaves your code in limbo. The source method might contain a lot of complicated code and a single sprout of a new method. Sometimes it isn't clear why only that work is happening someplace else, and it leaves the source method in an odd state. But at least that points to some additional work that you can do when you get the source class under test later.

Although there are some disadvantages, there are a couple of key advantages. When you use *Sprout Method*, you are clearly separating new code from <span id="page-85-1"></span><span id="page-85-0"></span>old code. Even if you can't get the old code under test immediately, you can at least see your changes separately and have a clean interface between the new code and the old code. You see all of the variables affected, and this can make it easier to determine whether the code is right in context.

### Sprout Class

*Sprout Method* is a powerful technique, but in some tangled dependency situations, it isn't powerful enough.

Consider the case in which you have to make changes to a class, but there is just no way that you are going to be able to create objects of that class in a test harness in a reasonable amount of time, so there is no way to sprout a method and write tests for it on that class. Maybe you have a large set of creational dependencies, things that make it hard to instantiate your class. Or you could have many hidden dependencies. To get rid of them, you'd need to do a lot of invasive refactoring to separate them out well enough to compile the class in a test harness.

In these cases, you can create another class to hold your changes and use it from the source class. Let's look at a simplified example.

Here is an ancient method on a C++ class called QuarterlyReportGenerator:

```
std::string QuarterlyReportGenerator::generate()
 std::vector<Result> results = database.queryResults(
 beginDate, endDate);
 std::string pageText;
 pageText += "<html><head><title>"
 "Quarterly Report"
 "</title></head><body><table>";
 if (results.size() != 0) {
 for (std::vector<Result>::iterator it = results.begin();
 it != results.end(); 
 ++it) {
 pageText += "<tr>";
 pageText += "<td>" + it->department + "</td>";
 pageText += "<td>" + it->manager + "</td>";
 char buffer [128];
 sprintf(buffer, "<td>$%d</td>", it->netProfit / 100);
 pageText += std::string(buffer);
 sprintf(buffer, "<td>$%d</td>", it->operatingExpense / 100);
 pageText += std::string(buffer);
 pageText += "</tr>";
 }
```

**Sprout Class**

<span id="page-86-0"></span>![](../assets/_page_86_Picture_1.jpeg)

```
 } else {
 pageText += "No results for this period";
 }
 pageText += "</table>";
 pageText += "</body>";
 pageText += "</html>";
 return pageText;
}
```

Let's suppose that the change that we need to make to the code is to add a header row for the HTML table it's producing. The header row should look something like this:

"<tr><td>Department</td><td>Manager</td><td>Profit</td><td>Expenses</td></tr>"

Furthermore, let's suppose that this is a huge class and that it would take about a day to get the class in a test harness, and this is time that we just can't afford right now.

We could formulate the change as a little class called QuarterlyReportTable-HeaderProducer and develop it using *test-driven development (88).*

**Sprout Class**

```
using namespace std;
class QuarterlyReportTableHeaderProducer
{
public:
 string makeHeader();
};
string QuarterlyReportTableProducer::makeHeader()
{
 return "<tr><td>Department</td><td>Manager</td>"
 "<td>Profit</td><td>Expenses</td>"; 
}
   When we have it, we can create an instance and call it directly in 
QuarterlyReportGenerator::generate():
...
QuarterlyReportTableHeaderProducer producer;
pageText += producer.makeHeader();
...
```

I'm sure that at this point you're looking at this and saying, "He can't be serious. It's ridiculous to create a class for this change! It's just a tiny little class that doesn't give you any benefit in the design. It introduces a completely new concept that just clutters the code." Well, at this point, that is true. The only reason we're doing it is to get out of a bad dependency situation, but let's take a closer look.

What if we'd named the class QuarterlyReportTableHeaderGenerator and gave it this sort of an interface?

```
class QuarterlyReportTableHeaderGenerator
public:
 string generate();
};
```

Now the class is part of a concept that we're familiar with. QuarterlyReportTableHeaderGenerator is a generator, just like QuarterlyReportGenerator. They both have generate() methods that return strings. We can document that commonality in the code by creating an interface class and having them both inherit from it:

```
class HTMLGenerator
public:
 virtual ~HTMLGenerator() = 0;
 virtual string generate() = 0;
};
class QuarterlyReportTableHeaderGenerator : public HTMLGenerator
public:
 ...
 virtual string generate();
 ...
};
class QuarterlyReportGenerator : public HTMLGenerator
public:
 ...
 virtual string generate();
 ...
};
```

As we do more work, we might be able to get QuarterlyReportGenerator under test and change its implementation so that it does most of its work using generator classes.

In this case, we were able to quickly fold the class into the set of concepts that we already had in the application. In many other cases, we can't, but that doesn't mean that we should hold back. Some sprouted classes never fold back into the main concepts in the application. Instead, they become new ones. You **Sprout Class**

might sprout a class and think that it is rather insignificant to your design until you do something similar someplace else and see the similarity. Sometimes you are able to factor out duplicated code in the new classes, and often you have to rename them, but don't expect it all to happen at once.

The way that you look at a sprouted class when you first create it and the way that you look at it after a few months are often significantly different. The fact that you have this odd new class in your system gives you plenty to think about. When you need to make a change close to it, you might start to think about whether the change is part of the new concept or whether the concept needs to change a little. This is all part of the ongoing process of design.

Essentially two cases lead us to *Sprout Class*. In one case, your changes lead you toward adding an entirely new responsibility to one of your classes. For instance, in tax-preparation software, certain deductions might not be possible at certain times of the year. You can see how to add a date check to the TaxCalculator class, but isn't checking that off to the side of TaxCalculator's main responsibility: calculating tax? Maybe it should be a new class. The other case is the one we led off this chapter with. We have a small bit of functionality that we could place into an existing class, but we can't get the class into a test harness. If we could get it to at least compile into a harness, we could attempt to use *Sprout Method*, but sometimes we're not even that lucky.

The thing to recognize about these two cases is that even though the motivation is different, when you look at the results, there isn't really a hard line between them. Whether a piece of functionality is strong enough to be a new responsibility is a judgment call. Moreover, because the code changes over time, the decision to sprout a class often looks better in retrospect.

Here are the steps for *Sprout Class*:

- 1. Identify where you need to make your code change.
- 2. If the change can be formulated as a single sequence of statements in one place in a method, think of a good name for a class that could do that work. Afterward, write code that would create an object of that class in that place, and call a method in it that will do the work that you need to do; then comment those lines out.
- 3. Determine what local variables you need from the source method, and make them arguments to the classes' constructor.
- 4. Determine whether the sprouted class will need to return values to the source method. If so, provide a method in the class that will supply those values, and add a call in the source method to receive those values.
- 5. Develop the sprout class test first (see *test-driven development (88)*).

**Sprout Class**

<span id="page-89-1"></span>6. Remove the comment in the source method to enable the object creation and calls.

#### Advantages and Disadvantages

The key advantage of *Sprout Class* is that it allows you to move forward with your work with more confidence than you could have if you were making invasive changes. In C++, *Sprout Class* has the added advantage that you don't have to modify any existing header files to get your change in place. You can include the header for the new class in the implementation file for the source class. In addition, the fact that you are adding a new header file to your project is a good thing. Over time, you'll put declarations into the new header file that could have ended up in the header of the source class. This decreases the compilation load on the source class. At least you'll know that you aren't making a bad situation worse. At some time later, you might be able to revisit the source class and put it under test.

<span id="page-89-0"></span>The key disadvantage of *Sprout Class* is conceptual complexity. As programmers learn new code bases, they develop a sense of how the key classes work together. When you use *Sprout Class*, you start to gut the abstractions and do the bulk of the work in other classes. At times, this is entirely the right thing to do. At other times, you move toward it only because your back is against the wall. Things that ideally would have stayed in that one class end up in sprouts just to make safe change possible.

**Wrap Method**

## Wrap Method

Adding behavior to existing methods is easy to do, but often it isn't the right thing to do. When you first create a method, it usually does just one thing for a client. Any additional code that you add later is sort of suspicious. Chances are, you're adding it just because it has to execute at the same time as the code you're adding it to. Back in the early days of programming, this was named *temporal coupling*, and it is a pretty nasty thing when you do it excessively. When you group things together just because they have to happen at the same time, the relationship between them isn't very strong. Later you might find that you have to do one of those things without the other, but at that point they might have grown together. Without a seam, separating them can be hard work.

When you need to add behavior, you can do it in a not-so-tangled way. One of the techniques that you can use is *Sprout Method*, but there is another that is very useful at times. I call it *Wrap Method*. Here is a simple example.

![](../assets/_page_90_Picture_1.jpeg)

```
public class Employee
{
 ...
 public void pay() {
 Money amount = new Money();
 for (Iterator it = timecards.iterator(); it.hasNext(); ) {
 Timecard card = (Timecard)it.next();
 if (payPeriod.contains(date)) {
 amount.add(card.getHours() * payRate);
 }
 }
 payDispatcher.pay(this, date, amount);
 }
}
```

In this method, we are adding up daily timecards for an employee and then sending his payment information to a PayDispatcher. Let's suppose that a new requirement comes along. Every time that we pay an employee, we have to update a file with the employee's name so that it can be sent off to some reporting software. The easiest place to put the code is in the pay method. After all, it has to happen at the same time, right? What if we do this instead?

**Wrap Method**

{

}

```
public class Employee
 private void dispatchPayment() {
 Money amount = new Money();
 for (Iterator it = timecards.iterator(); it.hasNext(); ) {
 Timecard card = (Timecard)it.next();
 if (payPeriod.contains(date)) {
 amount.add(card.getHours() * payRate);
 }
 }
 payDispatcher.pay(this, date, amount);
 }
 public void pay() {
 logPayment();
 dispatchPayment();
 }
 private void logPayment() {
 ...
 }
```

In the code, I've renamed pay() as dispatchPayment() and made it private. Next, I created a new pay method that calls it. Our new pay() method logs a payment and then dispatches payment. Clients who used to call pay() don't have to know or care about the change. They just make their call, and everything works out okay.

<span id="page-91-0"></span>This is one form of *Wrap Method*. We create a method with the name of the original method and have it delegate to our old code. We use this when we want to add behavior to existing calls of the original method. If every time a client calls pay() we want logging to occur, this technique can be very useful.

There is another form of *Wrap Method* that we can use when we just want to add a new method, a method that no one calls yet. In the previous example, if we wanted logging to be explicit, we could add a makeLoggedPayment method to Employee like this:

```
public class Employee
 public void makeLoggedPayment() {
 logPayment();
 pay();
 }
 public void pay() {
 ...
 }
 private void logPayment() {
      ...
 }
```

Now users have the option of paying in either way. It was described by Kent Beck in *Smalltalk Patterns: Best Practices* (Pearson Education, 1996).

*Wrap Method* is a great way to introduce seams while adding new features. There are only a couple of downsides. The first is that the new feature that you add can't be intertwined with the logic of the old feature. It has to be something that you do either before or after the old feature. Wait, did I say that is bad? Actually, it isn't. Do it when you can. The second (and more real) downside is that you have to make up a new name for the old code that you had in the method. In this case, I named the code in the pay() method dispatchPayment(). That is a bit of a stretch, and, frankly, I don't like the way the code ended up in this example. The dispatchPayment() method is really doing more than dispatching; it calculates pay also. If I had tests in place, chances are, I'd extract the first part of dispatchPayment() into its own method named calculatePay() and make the pay() method read like this:

**Wrap Method**

```
public void pay() {
 logPayment();
 Money amount = calculatePay();
 dispatchPayment(amount);
}
```

That seems to separate all of the responsibilities well. Here are the steps for the first version of the *Wrap Method*:

- 1. Identify a method you need to change.
- 2. If the change can be formulated as a single sequence of statements in one place, rename the method and then create a new method with the same name and signature as the old method. Remember to *Preserve Signatures (312)* as you do this.
- 3. Place a call to the old method in the new method
- 4. Develop a method for the new feature, test first (see *test-driven development (88)*), and call it from the new method

In the second version, when we don't care to use the same name as the old method, the steps look like this:

- 1. Identify a method you need to change.
- 2. If the change can be formulated as a single sequence of statements in one place, develop a new method for it using *test-driven development (88)*.
- 3. Create another method that calls the new method and the old method.

### Advantages and Disadvantages

*Wrap Method* is a good way of getting new, tested functionality into an application when we can't easily write tests for the calling code. *Sprout Method* and *Sprout Class* add code to existing methods and make them longer by at least one line, but *Wrap Method* does not increase the size of existing methods.

Another advantage of *Wrap Method* is that it explicitly makes the new functionality independent of existing functionality. When you wrap, you are not intertwining code for one purpose with code for another.

The primary disadvantage of *Wrap Method* is that it can lead to poor names. In the previous example, we renamed the pay method dispatchPay() just because we needed a different name for code in the original method. If our code isn't terribly brittle or complex, or if we have a refactoring tool that does *Extract Method (415)* safely, we can do some further extractions and end up with better names. However, in many cases, we are wrapping because we don't have any tests, the code is brittle and those tools aren't available.

**Wrap Method**

<span id="page-93-1"></span>
<span id="page-93-0"></span>
## Wrap Class

The class-level companion to *Wrap Method* is *Wrap Class*. *Wrap Class* uses pretty much the same concept. If we need to add behavior in a system, we can add it to an existing method, but we can also add it to something else that uses that method. In *Wrap Class*, that something else is another class.

Let's take a look at the code from the Employee class again.

```
class Employee
 public void pay() {
 Money amount = new Money();
 for (Iterator it = timecards.iterator(); it.hasNext(); ) {
 Timecard card = (Timecard)it.next();
 if (payPeriod.contains(date)) {
 amount.add(card.getHours() * payRate);
 }
 }
 payDispatcher.pay(this, date, amount);
 }
 ...
```

We want to log the fact that we are paying a particular employee. One thing that we can do is make another class that has a pay method. Objects of that class can hold on to an employee, do the logging work in the pay() method, and then delegate to the employee so that it can perform payment. Often the easiest way to do this, if you can't instantiate the original class in a test harness, is to use *Extract Implementer (356)* or *Extract Interface (362)* on it and have the wrapper implement that interface.

In the following code we've used *Extract Implementer* to turn the Employee class into an interface. Now a new class, LoggingEmployee, implements that class. We can pass any Employee to a LoggingEmployee so that it will log as well as pay.

```
class LoggingEmployee extends Employee
 public LoggingEmployee(Employee e) {
 employee = e;
 }
 public void pay() {
 logPayment();
 employee.pay();
 }
 private void logPayment() {
```

```
 ... 
 }
 ... 
}
```

This technique is called the *decorator pattern*. We create objects of a class that wraps another class and pass them around. The class that wraps should have the same interface as the class it is wrapping so that clients don't know that they are working with a wrapper. In the example, LoggingEmployee is a decorator for Employee. It needs to have a pay() method and any other methods on Employee that are used by the client.

### The Decorator Pattern

Decorator allows you to build up complex behaviors by composing objects at runtime. For example, in an industrial process-control system, we might have a class called ToolController with methods such as raise(), lower(), step(), on(), and off(). If we need to have additional things happen whenever we raise() or lower() (things such as audible alarms to tell people to get out of the way), we could put that functionality right in those methods in the ToolController class. Chances are, though, that wouldn't be the end to the enhancements. Eventually, we might need to log the number of times we turn the controller on and off. We might also need to notify other controllers that are close by when we step so that they can avoid stepping at the same time. The list of things that we can do along with our five simple operations (raise, lower, step, on and off) is endless, and it won't do to just create subclasses for each combination of things. The number of combinations of those behaviors could be endless.

The decorator pattern is an ideal fit for this sort of problem. When you use decorator, you create an abstract class that defines the set of operations you need to support. Then you create a subclass that inherits from that abstract class, accepts an instance of the class in its constructor, and provides a body for each of those methods. Here is that class for the ToolController problem:

```
abstract class ToolControllerDecorator extends ToolController
{
protected ToolController controller;
 public ToolControllerDecorator(ToolController controller) {
 this.controller = controller;
 }
 public void raise() { controller.raise(); }
 public void lower() { controller.lower(); }
 public void step() { controller.step(); }
 public void on() { controller.on(); }
 public void off() { controller.off(); }
}
```

<span id="page-95-0"></span>This class might not look very useful, but it is. You can subclass it and override any or all of the methods to add additional behavior. For example, if we need to notify other controllers when we step, we could have a StepNotifyingController that looks like this:

```
public class StepNotifyingController extends ToolControllerDecorator
 private List notifyees;
 public StepNotifyingController(ToolController controller, 
 List notifyees) {
 super(controller);
 this.notifyees = notifyees;
 }
 public void step() {
 // notify all notifyees here
 ...
 controller.step();
 }
```

The really neat thing is that we can nest the subclasses of ToolControllerDecorator:

```
ToolController controller = new StepNotifyingController(
                       new AlarmingController
                       (new ACMEController()), notifyees);
```

When we perform an operation such as step() on the controller, it notifies all notifyees, issues an alarm, and actually performs the stepping action. That latter part, actually performing the step action, happens in ACMEController, which is a concrete subclass of ToolController, not ToolControllerDecorator. It doesn't pass the buck to anyone else; it just does each of the tool controller actions. When you are using the decorator pattern, you need to have at least one of these "basic" classes that you wrap around.

Decorator is a nice pattern, but it is good to use it sparingly. Navigating through code that contains decorators that decorate other decorators is a lot like peeling away the layers of an onion. It is necessary work, but it does make your eyes water.

This is a fine way of adding functionality when you have many existing callers for a method like pay(). However, there is another way of wrapping that is not so decorator-ish. Let's look at a case where we need to log calls to pay() in only one place. Instead of wrapping in the functionality as a decorator, we can put it in another class that accepts an employee, does payment, and then logs information about it.

Here is a little class that does this:

```
class LoggingPayDispatcher
{
 private Employee e;
```

```
 public LoggingPayDispatcher(Employee e) {
 this.e = e;
 }
 public void pay() {
 employee.pay();
 logPayment();
 }
 private void logPayment() {
 ...
 }
 ...
}
```

Now we can create LogPayDispatcher in the one place where we need to log payments.

The key to *Wrap Class* is that you are able to add new behavior into a system without adding it to an existing class. When there are many calls to the code you want to wrap, it often pays to move toward a decorator-ish wrapper. When you use the *decorator pattern*, you can transparently add new behavior to a set of existing calls like pay() all at once. On the other hand, if the new behavior only has to happen in a couple of places, creating a wrapper that isn't decorator-ish can be very useful. Over time, you should pay attention to the responsibilities of the wrapper and see if the wrapper can become another highlevel concept in your system.

Here are the steps for *Wrap Class*:

- 1. Identify a method where you need to make a change.
- 2. If the change can be formulated as a single sequence of statements in one place, create a class that accepts the class you are going to wrap as a constructor argument. If you have trouble creating a class that wraps the original class in a test harness, you might have to use *Extract Implementer (356)* or *Extract Interface (362)* on the wrapped class so that you can instantiate your wrapper.
- 3. Create a method on that class, using *test-driven development (88)*, that does the new work. Write another method that calls the new method and the old method on the wrapped class.
- 4. Instantiate the wrapper class in your code in the place where you need to enable the new behavior.

The difference between *Sprout Method* and *Wrap Method* is pretty trivial. You are using *Sprout Method* when you choose to write a new method and call

it from an existing method. You are using *Wrap Method* when you choose to rename a method and replace it with a new one that does the new work and calls the old one. I usually use *Sprout Method* when the code I have in the existing method communicates a clear algorithm to the reader. I move toward *Wrap Method* when I think that the new feature I'm adding is as important as the work that was there before. In that case, after I've wrapped, I often end up with a new high-level algorithm, something like this:

```
public void pay() {
 logPayment();
 Money amount = calculatePay();
 dispatchPayment(amount);
```

Choosing to use *Wrap Class* is a whole other issue. There is a higher threshold for this pattern. Generally two cases tip me toward using *Wrap Class*:

- 1. The behavior that I want to add is completely independent, and I don't want to pollute the existing class with behavior that is low level or unrelated.
- 2. The class has grown so large that I really can't stand to make it worse. In a case like this, I wrap just to put a stake in the ground and provide a roadmap for later changes.

The second case is pretty hard to do and get used to. If you have a very large class that has, say, 10 or 15 different responsibilities, it might seem a little odd to wrap it just to add some trivial functionality. In fact, if you can't present a compelling case to your coworkers, you might get beat up in the parking lot or, worse, ignored for the rest of your workdays, so let me help you make that case.

The biggest obstacle to improvement in large code bases is the existing code. "Duh," you might say. But I'm not talking about how hard it is to work in difficult code; I'm talking about what that code leads you to believe. If you spend most of your day wading through ugly code, it's very easy to believe that it will always be ugly and that any little thing that you do to make it better is simply not worth it. You might think, "What does it matter whether I make this little piece nicer if 90 percent of the time I'll still being working with murky slime? Sure, I can make this piece better, but what will that do for me this afternoon? Tomorrow?" Well, if you look at it that way, I'd have to agree with you. Not much. But if you consistently do these little improvements, your system will start to look significantly different over the course of a couple of months. At some point, you'll come to work in the morning expecting to sink your hands into some slime and discover, "Huh, this code looks pretty good. It looks like

<span id="page-98-1"></span><span id="page-98-0"></span>![](../assets/_page_98_Picture_1.jpeg)

someone was in here refactoring recently." At that point, when you feel the difference between good code and bad code in your gut, you are a changed person. You might even find yourself wanting to refactor far in excess of what you need to get the job done, just to make your life easier. It probably sounds silly to you if you haven't experienced it, but I've seen it happen to teams over and over again. The hard part is the initial set of steps because sometimes they look silly. "What? Wrap a class just to add this little feature? It looks worse than it did before. It's more complicated." Yes, it is, for now. But when you really start to break out those 10 or 15 responsibilities in that wrapped class, it will look far more appropriate.

### Summary

*Bigger*, are good places to start.

out getting existing classes under test. From a design point of view, it is hard to know what to think about them. In many cases, they allow us to put some distance between distinct new responsibilities and old ones. In other words, we start to move toward better design. But in other cases, we know that the only reason we've created a class is because we wanted to write new code with tests and we weren't prepared to take the time to get the existing class under test. This is a very real situation. When people do this in projects, you start to see new classes and methods sprouting around the carcasses of the old big classes. But then an interesting thing happens. After a while, people get tired of sidestepping the old carcasses, and they start to get them under test. Part of this is familiarity. If you have to look at this big, untested class repeatedly to figure out where to sprout from it, you get to know it better. It gets less scary. The other part of it is sheer tiredness. You get tired of looking at the trash in your living room, and you want to take it out. Chapter 9*, I Can't Get This Class into a Test*

*Harness,* and Chapter 20*, This Class Is Too Big and I Don't Want It to Get Any*

In this chapter, I outlined a set of techniques you can use to make changes with-

**Summary**
