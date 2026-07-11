<span id="page-267-1"></span>
<span id="page-267-0"></span>
# Chapter 20: This Class Is Too Big and I Don't Want It to Get Any Bigger


Many of the features that people add to systems are little tweaks. They require the addition of a little code and maybe a few more methods. It's tempting to just make these changes to an existing class. Chances are, the code that you need to add must use data from some existing class, and the easiest thing is to just add code to it. Unfortunately, this easy way of making changes can lead to some serious trouble. When we keep adding code to existing classes, we end up with long methods and large classes. Our software turns into a swamp, and it takes more time to understand how to add new features or even just understand how old features work.

I visited a team once that had what looked like a nice architecture on paper. They told me what the primary classes were and how they communicated with each other in the normal cases. Then, they showed me a couple of nice UML diagrams that showed the structure. I was surprised when I started to look at the code. Each of their classes could really be broken out into about 10 or so, and doing that would help them get past their most pressing problems.

What are the problems with big classes? The first is confusion. When you have 50 or 60 methods on a class, it's often hard to get a sense of what you have to change and whether it is going to affect anything else. In the worst cases, big classes have an incredible number of instance variables, and it is hard to know what the effects are of changing a variable. Another problem is task scheduling. When a class has 20 or so responsibilities, chances are, you'll have an incredible number of reasons to change it. In the same iteration, you might have several programmers who have to do different things to the class. If they are working concurrently, this can lead to some serious thrashing, particularly because of the third problem: Big classes are a pain to test. Encapsulation is a good thing, right? Well, don't ask testers about that; they are liable to bite your **This Class Is Too Big and I Don't Want It to Get Any Bigger**

<span id="page-268-0"></span>![](../assets/_page_268_Picture_1.jpeg)

head off. Classes that are too big often hide too much. Encapsulation is great when it helps us reason about our code and when we know that certain things can be changed only under certain circumstances. However, when we encapsulate too much, the stuff inside rots and festers. There isn't any easy way to sense the effects of change, so people fall back on *Edit and Pray (9)* programming. At that point, either changes take far too long or the bug count increases. You have to pay for the lack of clarity somehow.

The first issue to confront when we have big classes is this: How can we work without making things worse? The key tactics we can use here are *Sprout Class (63)* and *Sprout Method (59)*. When we have to make changes, we should consider putting the code into a new class or a new method. *Sprout Class (63)* really keeps things from getting much worse. When you put new code into a new class, sure, you might have to delegate from the original class, but at least you aren't making it much bigger. *Sprout Method (59)* helps also, but in a more subtle way. If you add code in a new method, yes, you will have an additional method, but at the very least, you are identifying and naming another thing that the class does; often the names of methods can give you hints about how to break down a class into smaller pieces.

The key remedy for big classes is refactoring. It helps to break down classes into sets of smaller classes. But the biggest issue is figuring out what the smaller classes should look like. Fortunately, we have some guidance.

### Single-Responsibility Principle (SRP)

Every class should have a single responsibility: It should have a single purpose in the system, and there should be only one reason to change it.

**This Class Is Too Big and I Don't Want It to Get Any Bigger**

The single-responsibility principle is kind of hard to describe because the idea of a responsibility is kind of nebulous. If we look at it in a very naïve way, we might say, "Oh, that means that every class should have only a single method, right?" Well, methods can be seen as responsibilities. A Task is responsible for running using its run method, for telling us how many subtasks it has with taskCount method, and so on. But what we mean by a responsibility really comes into focus when we talk about *main purpose*. Figure 20.1 shows an example.

<span id="page-269-0"></span>
#### **RuleParser** - current : string - variables : HashMap - currentPosition : int + evaluate(string) : int - branchingExpression(Node left, Node right) : int - causalExpression(Node left, Node right) int - variableExpression(Node node) : int - valueExpression(Node node) : int - nextTerm() : string - hasMoreTerms() : boolean + addVariable(string name, int value)

**Figure 20.1** *Rule parser.*

We have a little class here that evaluates strings containing rule expressions in some obscure language. What responsibilities does it have? We can look at the name of the class to find one responsibility: It parses. But is that its main purpose? Parsing doesn't seem to be it. It seems that it evaluates also.

What else does it do? It holds on to a current string, the string that it is parsing. It also holds on to a field that indicates the current position while it is parsing. Both of those mini-responsibilities seem to fit under the category of parsing.

Let's take a look at the other variable, the variables field. It holds on to a set of variables that the parser uses so that it can evaluate arithmetic expressions in rules such as a + 3. If someone calls the method addVariable with the arguments a and 1, the expression a + 3 will evaluate to 4. So, it seems that there is this other responsibility, variable management, in this class.

Are there more responsibilities? Another way to find them is to look at method names. Is there a natural way to group the names of the methods? It seems that the methods kind of fall into these groups:

**This Class Is Too Big and I Don't Want It to Get Any Bigger**

| evaluate | branchingExpression | nextTerm     | addVariable |
|----------|---------------------|--------------|-------------|
|          | causalExpression    | hasMoreTerms |             |
|          | variableExpression  |              |             |
|          | valueExpression     |              |             |

The evaluate method is an entry point of the class. It is one of only two public methods, and it denotes a key responsibility of the class: evaluation. All of the

<span id="page-270-0"></span>![](../assets/_page_270_Picture_1.jpeg)

methods that end with the *Expression* suffix are kind of the same. Not only are they named similarly, but they all accept Nodes as arguments and return an int that indicates the value of a subexpression. The nextTerm and hasMoreTerms methods are similar, too. They seem to be about some special form of tokenization for terms. As we said earlier, the addVariable method is concerned with variable management.

To summarize, it seems that Parser has the following responsibilities:

- Parsing
- Expression evaluation
- Term tokenization
- Variable management

If we had to come up with a design from scratch that separated all of these responsibilities, it might look something like Figure 20.2.

Is this overkill? It could be. Often people who write little language interpreters merge parsing and expression evaluation; they just evaluate as they parse. But although that can be convenient, often it doesn't scale well as a language grows. Another responsibility that is kind of meager is that of SymbolTable. If the only responsibility of SymbolTable is to map variable names to integers, the class isn't giving us much advantage over just using a hash table or a list. Nice design, but guess what? It is pretty hypothetical. Unless we are choosing to rewrite this part of the system, our little multiclass design is a castle in the sky.

**This Class Is Too Big and I Don't Want It to Get Any Bigger**

![](../assets/_page_270_Figure_11.jpeg)

**Figure 20.2** *Rule classes with responsibilities separated.*

<span id="page-271-1"></span><span id="page-271-0"></span>In real-world cases of big classes, the key is to identify the different responsibilities and then figure out a way to incrementally move toward more focused responsibilities.

## Seeing Responsibilities

In the RuleParser example in the last section, I showed a particular decomposition of a class into smaller classes. When I did that breakdown, I did it pretty much by rote. I listed all of the methods and started to think about what their purposes were. The key questions I asked were "Why is this method here?" and "What is it doing for the class?" Then I grouped them into lists, putting together methods that had a similar reason for being there.

I call this way of seeing responsibilities method grouping. It's only one of many ways of seeing responsibilities in existing code.

Learning to see responsibilities is a key design skill, and it takes practice. It might seem odd to talk about a design skill in this context of working with legacy code, but there really is little difference between discovering responsibilities in existing code and formulating them for code that you haven't written yet. The key thing is to be able to see responsibilities and learn how to separate them well. If anything, legacy code offers far more possibilities for the application of design skill than new features do. It is easier to talk about design tradeoffs when you can see the code that will be affected, and it is also easier to see whether structure is appropriate in a given context because the context is real and right in front of us.

This section describes a set of heuristics that we can use to see responsibilities in existing code. Note that we are not inventing responsibilities; we're just discovering what is there. Regardless of what structure legacy code has, its pieces do identifiable things. Sometimes they are hard to see, but these techniques can help. Try to apply them even with code that you don't have to change immediately. The more you start noticing the responsibilities inherent in code, the more you learn about it.

### Heuristic #1: Group Methods

Look for similar method names. Write down all of the methods on a class, along with their access types (public, private, and so on), and try to find ones that seem to go together.

This technique, method grouping, is a pretty good start, particularly with very large classes. The important thing is to recognize that you don't have to

<span id="page-272-0"></span>![](../assets/_page_272_Picture_1.jpeg)

categorize all of the names into new classes. Just see if you can find some that look like they are part of a common responsibility. If you can identify some of these responsibilities that are a bit off to the side of the main responsibility of the class, you have a direction in which you can take the code over time. Wait until you have to modify one of the methods you've categorized, and then decide whether you want to extract a class at that point.

Method grouping is a great team exercise also. Put up poster boards in your team room with lists of the method names for each of your major classes. Team members can mark up the posters over time, showing different groupings of methods. The whole team can hash out which groupings are better and decide on directions for the code to go in.

#### Heuristic #2: Look at Hidden Methods

Pay attention to private and protected methods. If a class has many of them, it often indicates that there is another class in the class dying to get out.

Big classes can hide too much. This question comes up over and over again from people new to unit testing: "How do I test private methods?" Many people spend a lot of time trying to figure out how to get around this problem, but, as I mentioned in an earlier chapter, the real answer is that if you have the urge to test a private method, the method shouldn't be private; if making the method public bothers you, chances are, it is because it is part of a separate responsibility. It should be on another class.

The RuleParser class earlier in this section is the quintessential example of this. It has two public methods: evaluate and addVariable. Everything else is private. What would the RuleParser class be like if we made nextTerm and has-MoreTerms public? Well, it would seem pretty odd. Users of the parser might get the idea that they have to use those two methods along with evaluate to parse and evaluate expressions. It would be odd to have those methods public on the RuleParser class, but it is far less odd—and, actually, perfectly fine to make them public methods on a TermTokenizer class. This doesn't make RuleParser any less encapsulated. Even though nextTerm and hasMoreTerms are public on TermTokenizer, they are accessed privately in a parser. This is shown in Figure 20.3.

<span id="page-273-0"></span>![](../assets/_page_273_Figure_2.jpeg)

**Figure 20.3** RuleParser *and* TermTokenizer*.*

#### Heuristic #3: Look for Decisions That Can Change

Look for decisions—not decisions that you are making in the code, but decisions that you've already made. Is there some way of doing something (talking to a database, talking to another set of objects, and so on) that seems hard-coded? Can you imagine it changing?

When you are trying to break up a big class, it's tempting to pay a lot of attention to the names of the methods. After all, they are one of the most noticeable things about a class. But the names of methods don't tell the whole story. Often big classes house methods that do many things at many different levels of abstraction. For instance, a method named updateScreen()might generate text for a display, format it, and send it to several different GUI objects. Looking at the method name alone, you'd have no idea how much work is going on and how many responsibilities are nestled in that code.

For this reason, it pays to do a little extract method refactoring before really settling on classes to extract. What methods should you extract? I handle this by looking for decisions. How many things are assumed in the code? Is the code calling methods from a particular API? Is it assuming that it will always be accessing the same database? If the code is doing these things, it's a good idea to extract methods that reflect what you intend at a high level. If you are getting particular information from a database, extract a method named after the information you are getting. When you do these extractions, you have many more methods, but you also might find that method grouping is easier. Better than that, you might find that you completely encapsulated some resource behind a set of methods. When you extract a class for them, you'll have broken some dependencies on low-level details.

#### Heuristic #4: Look for Internal Relationships

Look for relationships between instance variables and methods. Are certain instance variables used by some methods and not others?

{

<span id="page-274-0"></span>It's really hard to find classes in which all the methods use all of the instance variables. Usually there is some sort of "lumping" in a class. Two or three methods might be the only ones that use a set of three variables. Often the names help you see this. For instance, in the RulerParser class, there is a collection named variables and a method named addVariable. That shows us that there is an obvious relationship between that method and that variable. It doesn't tell us that there aren't other methods that access that variable, but at least we have a place to start looking.

Another technique we can use to find these "lumps" is to make a little sketch of the relationships inside a class. These are called *feature sketches*. They show which methods and instance variables each method in a class uses, and they are pretty easy to make. Here is an example:

```
class Reservation
 private int duration;
 private int dailyRate;
 private Date date;
 private Customer customer;
 private List fees = new ArrayList();
 public Reservation(Customer customer, int duration,
 int dailyRate, Date date) {
 this.customer = customer;
 this.duration = duration;
 this.dailyRate = dailyRate;
 this.date = date;
 }
 public void extend(int additionalDays) {
 duration += additionalDays;
 }
 public void extendForWeek() {
 int weekRemainder = RentalCalendar.weekRemainderFor(date);
 final int DAYS_PER_WEEK = 7;
 extend(weekRemainder);
 dailyRate = RateCalculator.computeWeekly(
 customer.getRateCode())
 / DAYS_PER_WEEK;
 }
 public void addFee(FeeRider rider) {
 fees.add(rider);
 }
 int getAdditionalFees() {
 int total = 0;
```

```
 for(Iterator it = fees.iterator(); it.hasNext(); ) {
 total += ((FeeRider)(it.next())).getAmount(); 
 }
 return total;
 }
 int getPrincipalFee() {
 return dailyRate 
 * RateCalculator.rateBase(customer) 
 * duration;
 }
 public int getTotalFee() {
 return getPrincipalFee() + getAdditionalFees();
 }
```

The firststep is to draw circles for each of the variables, as shown in Figure 20.4.

Next, we look at each method and put down a circle for it. Then we draw a line from each method circle to the circles for any instance variables and methods that it accesses or modifies. It's usually okay to skip the constructors. Generally, they modify each instance variable.

![](../assets/_page_275_Picture_5.jpeg)

**Figure 20.4** Variables in the Reservation *class.*

<span id="page-276-0"></span>![](../assets/_page_276_Picture_1.jpeg)

Figure 20.5 shows the diagram after we've added a circle for the extend method:

![](../assets/_page_276_Picture_3.jpeg)

**Figure 20.5** extend *uses duration.*

**Seeing Responsibilities** If you've already read the chapters that describe effect sketching, you might notice that these *feature sketches* look a lot like *effect sketches (155)*. Essentially, they are pretty close. The main difference is that the arrows are reversed. In *feature sketches*, arrows point in the direction of a method or variable that is used by another method or variable. In *effect sketches*, the arrow points toward methods or variables that are impacted by other methods and variables.

These are two different, completely legitimate ways of looking at interactions in a system. *Feature sketches* are great for mapping the internal structure of classes. *Effect sketches (155)* are great for reasoning forward from a point of change.

Is it confusing that they look somewhat the same? Not really. These sketches are disposable tools. They are the sort of thing that you sit down and draw up with a partner for about 10 minutes before you make your changes. Afterward you throw them away. There is little value in keeping them around, so there is little likelihood that they will be confused with each other.

<span id="page-277-0"></span>Figure 20.6 shows the sketch after we've added circles for each feature and lines for all of the features they use:

![](../assets/_page_277_Picture_3.jpeg)

**Figure 20.6** *Feature sketch for* Reservation*.*

What can we learn from this sketch? One obvious thing is that there is a little bit of clustering in this class. The duration, dailyRate, date, and customer variables are used primarily by getPrincipalFee, extend, and extendForWeek. Are any of these methods public? Yes, extend and extendForWeek are, but getPrincipalFee isn't. What would our system be like if we made this cluster into its own class (see Figure 20.7)?

<span id="page-278-0"></span>![](../assets/_page_278_Figure_2.jpeg)

**Seeing** 

**Responsibilities Figure 20.7** *A cluster in* Reservation*.*

The big bubble in the diagram could be a new class. It would need to have extend, extendForWeek, and getPrincipalFee as public methods, but all of the other methods could be private. We could keep fees, addFee, getAdditionalFees, and get-TotalFee in the Reservation class and delegate to the new class (see Figure 20.8).

<span id="page-279-0"></span>![](../assets/_page_279_Figure_2.jpeg)

**Figure 20.8** Reservation *using a new class.*

The key thing to figure out before attempting this is whether this new class has a good, distinct responsibility. Can we come up with a name for it? It seems to do two things: extend a reservation and calculate its principal fee. It seems that Reservation is a good name, but we are already using it for the original class.

Here's another possibility. We could flip things around. Instead of extracting all of the code in the big circle, we can extract the other code, as in Figure 20.9.

We can call the class that we extract FeeCalculator. That could work, but the getTotalFee method needs to call getPrincipalFee on Reservation—or does it?

![](../assets/_page_280_Picture_2.jpeg)

**Seeing Responsibilities**

**Figure 20.9** *Seeing* Reservation *in another way.*

What if we call getPrincipalFee in Reservation and then pass that value to the FeeCalculator? Here is a sketch of the code:

```
public class Reservation
 ...
 private FeeCalculator calculator = new FeeCalculator();
 private int getPrincipalFee() {
 ...
 }
 public Reservation(Customer customer, int duration,
 int dailyRate, Date date) {
 this.customer = customer;
 this.duration = duration;
 this.dailyRate = dailyRate;
 this.date = date;
 }
 ...
 public void addFee(FeeRider fee) {
 calculator.addFee(fee);
 }
 public getTotalFee() {
 int baseFee = getPrincipalFee();
 return calculator.getTotalFee(baseFee);
 }
```

Our structure ends up looking like Figure 20.10.

}

We can even consider moving getPrincipalFee over to FeeCalculator to make the responsibilities align with the class names better, but considering that getPrincipalFee depends on a number of variables in Reservation, it might be better to keep it where it is.

![](../assets/_page_281_Figure_6.jpeg)

**Figure 20.10** *Reservation using* FeeCalculator*.*

<span id="page-282-0"></span>![](../assets/_page_282_Picture_1.jpeg)

Feature sketches are a great tool for finding separate responsibilities in classes. We can try to group the features and figure out what classes we can extract based upon the names. But in addition to helping us find responsibilities, feature sketches allow us to see the dependency structure inside classes, and that can often be just as important as responsibility when we are deciding what to extract. In this example, there were two strong clusters of variables and methods. The only connection between them is the call of getPrincipalFee inside getTotalFee. In feature sketches, we often see these connections as a small set of lines connecting larger clusters. I call this a *pinch point (180)*, and I talk about them more in Chapter 12, *I Need to Make Many Changes in One Area. Do I Have to Break Dependencies for All the Classes Involved?*

Sometimes when you draw a sketch, you don't find any pinch points. They aren't always there. But at the very least, seeing the names and the dependencies among the features can help.

When you have the sketch, you can play around with different ways of breaking up the class. To do this, circle groups of features. When you circle features, the lines that you cross can define the interface of a new class. As you circle, try to come up with a class name for each group. Frankly, aside from anything that you choose to do or not do when you extract classes, this is a great way of increasing your naming skill. It's also a good way of exploring design alternatives.

#### Heuristic #5: Look for the Primary Responsibility

Try to describe the responsibility of the class in a single sentence.

The *Single Responsibility Principle* tells us that classes should have a single responsibility. If that's the case, it should be easy to write it down in a single sentence. Try it with one of the big classes in your system. As you think of what the clients need and expect from the class, add clauses to the sentence. The class does this, and this, and this, and that. Is there any one thing that seems more important than anything else? If there is, you might have found the key responsibility of the class. The other responsibilities should probably be factored out into other classes.

There are two ways to violate the *Single Responsibility Principle*. It can be violated at the interface level and at the implementation level. SRP is violated at the interface level when a class presents an interface that makes it appear that it is responsible for a very large number of things. For instance, the interface to this class (see Figure 20.11) looks like it can be broken into three or four classes.

#### ScheduledJob

- + addPredecessor(ScheduledJob)
- + addSuccessor(ScheduledJob)
- + getDuration() : int
- + show();
- + refesh() + run()
- + postMessage() : void
- + isVisible() : boolean
- + isModified() : boolean
- + persist()
- + acquireResources()
- + releaseResources()
- + isRunning()
- + getElapsedTime()
- + pause()
- + resume()
- + getActivities()

**Figure 20.11** *The* ScheduledJob *class.*

The SRP violation that we care most about is violation at the implementation level. Plainly put, we care whether the class really does all of that stuff or whether it just delegates to a couple of other classes. If it delegates, we don't have a large monolithic class; we just have a class that is a facade, a front end for a bunch of little classes and that can be easier to manage.

Figure 20.12 shows the ScheduledJob class with responsibilities delegated to a few other classes.

<span id="page-284-0"></span>![](../assets/_page_284_Figure_2.jpeg)

**Figure 20.12** ScheduledJob *with extracted classes.*

The *Single Responsibility Principle* is still violated at the interface level, but at the implementation level things are a bit better.

How would we solve the problem at the interface level? That's a bit harder. The general approach is to see if some of the classes we delegate to can actually be used directly by clients. For instance, if only some clients are interested in running ScheduledJobs, we could refactor toward something like this:

<span id="page-285-0"></span>![](../assets/_page_285_Figure_2.jpeg)

**Figure 20.13** *A client-specific interface for* ScheduledJob*.*

Now clients that are concerned only with controlling jobs can accept ScheduledJobs as JobControllers. This technique of making an interface for a particular set of clients keeps the design in line with the *Interface Segregation Principle*.

#### Interface Segregation Principle (ISP)

When a class is large, rarely do all of its clients use all of its methods. Often we can see different groupings of methods that particular clients use. If we create an interface for each of these groupings and have the large class implement those interfaces, each client can see the big class through that particular interface. This helps us hide information and also decreases dependency in the system. The clients no longer have to recompile whenever the large class does.

When we have interfaces for particular sets of clients, we can often start to move code from the big class to a new class that uses the original class, as you can see in Figure 20.14.

<span id="page-286-0"></span>![](../assets/_page_286_Picture_1.jpeg)

![](../assets/_page_286_Figure_2.jpeg)

**Figure 20.14** *Segregating the interface of* ScheduledJob*.*

Instead of having ScheduledJob delegate to a JobController, we've made a JobController delegate to ScheduledJob. Now whenever a client wants to run a ScheduledJob, it creates a JobController, passing it a ScheduledJob, and uses the JobController to handle its execution.

This sort of refactoring is nearly always tougher than it sounds. Often to do it, you have to expose more methods in the public interface of the original class (ScheduledJob) so that the new front (StandardJobController) has access to everything it needs to do its work. Often it takes quite a bit of work to make a change like this. Client code now has to be changed to use the new class rather than the old one; to do that safely, you need to have tests around those clients. The nice thing about this refactoring, though, is that it does allow you to whittle away at the interface of a big class. Notice that ScheduledJob no longer has the methods that are on JobController.

#### Heuristic #6: When All Else Fails, Do Some Scratch Refactoring

If you are having a lot of trouble seeing responsibilities in a class, do some scratch refactoring.

<span id="page-287-2"></span><span id="page-287-0"></span>*Scratch refactoring (212)* is a powerful tool. Just remember that it is an artificial exercise. The things you see when you "scratch" are not necessarily the things you'll end up with when you refactor.

#### Heuristic #7: Focus on the Current Work

Pay attention to what you have to do right now. If you are providing a different way of doing anything, you might have identified a responsibility that you should extract and then allow substitution for.

<span id="page-287-1"></span>It is easy to become overwhelmed by the number of distinct responsibilities you can identify in a class. Remember that the changes you currently are making are telling you about some particular way that the software can change. Often just recognizing that way of changing is enough to see the new code you write as a separate responsibility.

## Other Techniques

The heuristics for identifying responsibilities can really help you dig in and find new abstractions in old classes, but they are just tricks. The way to really get better at identification is to read more. Read books about design patterns. More important, read other people's code. Look at open-source projects, and just take some time to browse and see how other people do things. Pay attention to how classes are named and the correspondence between class names and the names of methods. Over time, you'll get better at identifying hidden responsibilities, and you'll just start to see them when you browse unfamiliar code.

**Moving Forward**

### Moving Forward

When you've identified a bunch of different responsibilities in a large class, there are only two other issues to deal with: strategy and tactics. Let's talk about strategy first.

### Strategy

What should we do when we've identified all of these separate responsibilities? Should we take a week and start to whack at the big classes in the system? Should we break them all down into little bits? If you have time to do that, it's

<span id="page-288-0"></span>![](../assets/_page_288_Picture_1.jpeg)

great, but it's rare. It can also be risky. In nearly every case that I've seen, when teams go on a large refactoring binge, system stability breaks down for a little while, even if they are being careful and writing tests as they go. If you are early in your release cycle, are willing to accept the risk, and have time, a refactoring binge can be fine. Just don't let the bugs dissuade you from other refactoring.

The best approach to breaking down big classes is to identify the responsibilities, make sure that everyone else on the team understands them, and then break down the class on an as-needed basis. When you do that, you spread out the risk of the changes and can get other work done as you go.

#### Tactics

In most legacy systems, the most that you can hope for in the beginning is to start to apply the SRP at the implementation level: Essentially, extract classes from your big class and delegate to them. Introducing SRP at the interface level requires more work. The clients of your class have to change, and you need tests for them. Nicely, introducing SRP at the implementation level makes it easier to introduce it at the interface level later. Let's look at the implementation case first.

The techniques that you use to extract classes depend upon a number of factors. One is how easily you can get tests around the methods that could be affected. It pays to take a look at the class and list all of the instance variables and methods that you'll have to move. From this, you should get a good idea of what methods you should write tests for. In the case of the RuleParser class that we looked at previously, if we were considering breaking out a TermTokenizer class, we'd want to move the string field named current and the currentPosition field, as well as hasMoreTerms and nextTerm. The fact that hasMoreTerms and nextTerm are private means that we can't really write tests directly for them. We could make them public (after all, we are going to move them anyway), but it might be just as easy to create a RuleParser in a test harness and give it a set of strings to evaluate. If we do that, we'll have tests that cover hasMoreTerms and nextTerm, and we'll be able to move them to a new class safely.

Unfortunately, many big classes are hard to instantiate in test harnesses. See Chapter 9, *I Can't Get This Class into a Test Harness*, for a set of tips that you can use to move forward. If you are able to get the class instantiated, you might have to use the tips in Chapter 10, *I Can't Run This Method in a Test Harness*, to get tests in place also.

If you are able to get tests in place, you can start to extract a class in a very straightforward way, using the *Extract Class* refactoring described in Martin Fowler's book *Refactoring: Improving the Design of Existing Code* (Addison-

**Moving Forward**

Wesley, 1999). However, if you aren't able to get tests in place, you can still move forward, albeit in a slightly riskier way. This is a very conservative approach, and it works regardless of whether you have a refactoring tool. Here are the steps:

- 1. Identify a responsibility that you want to separate into another class.
- 2. Figure out whether any instance variables will have to move to the new class. If so, move them to a separate part of the class declaration, away from the other instance variables.
- 3. If you have whole methods that you want to move to the new class, extract the bodies of each of them to new methods. The name of each new method should be the same as its old name, but with a unique common prefix in front of the name, something like MOVING, all in capital letters. If you are not using a refactoring tool, remember to *Preserve Signatures (312)* when you extract the methods. As you extract each method, put it in that separate part of the class declaration, next to the variables you are moving.
- 4. If parts of methods should go to the other class, extract them from the original methods. Use that prefix MOVING again for their names, and put them in the separate section.
- 5. At this point, you should have a section of your class that has instance variables that you need to move, along with a bunch of methods that you want to move also. Do a text search of the current class and all of its subclasses, to make sure that none of the variables that you are going to move is used outside of the methods you are going to move. It is important not to *Lean on the Compiler (315)* in this step. In many OO languages, a derived class can declare variables with the same name as variables in a base class. Often this is called *shadowing*. If your class shadows any variables and other uses of the variables are hanging around, you could change the behavior of your code when you move the variables. Likewise, if you *Lean on the Compiler (315)* to find uses of a variable that is shadowing another, you won't find all of the places it is being used. Commenting out the declaration of a shadowed variable just makes the one that it shadows visible.
- 6. At this point, you can move all of the instance variables and methods you've separated directly to the new class. Create an instance of the new class in the old class, and *Lean on the Compiler (315)* to find places where the moved methods have to be called on the instance rather than on the old class.

**Moving Forward**

<span id="page-290-1"></span>![](../assets/_page_290_Picture_1.jpeg)

7. After you've done the move and the code compiles, you can start to remove the MOVING prefix on all of the moved methods. *Lean on the Compiler (315)* to navigate to the places where you need to change the names.

The steps for this refactoring are rather involved, but if you are in a very complex piece of code, they are necessary if you want to extract classes safely without tests.

<span id="page-290-0"></span>There are a couple of things that can go wrong when you extract classes without tests. The most subtle bugs that we can inject are bugs related to inheritance. Moving a method from one class to another is pretty safe. You can *Lean on the Compiler (xx)* to aid your work, but in most languages all bets are off if you attempt to move a method that overrides another method. If you do, callers of the method on the original class will now call a method with the same name from a base class. A similar situation can occur with variables. A variable in a subclass can hide a variable with the same name in a superclass. Moving it just makes the one that was hidden visible.

To get past these problems, we don't move the original methods at all. We create new methods by extracting the bodies of the old ones. The prefix is just a mechanical way of generating a new name and making sure that it doesn't clash with other names before the move. Instance variables are a little trickier: We have that manual step of searching for uses of variables before we use them. It is possible to make mistakes with this. Be very careful, and do it with a partner.

## After Extract Class

**After Extract Class**

Extracting classes from a big class is often a good first step. In practice, the biggest danger for teams doing this is getting overambitious. You might have done a *Scratch refactoring (212)* or developed some other view of what the system *should* look like. But remember, the structure you have in your application works. It supports the functionality; it just might not be tuned toward moving forward. Sometimes the best thing that you can do is formulate a view of how a large class is going to look after refactoring and then just forget about it. You did it to discover what is possible. To move forward, you have to be sensitive to what is there and move that not necessarily toward the ideal design, but at least in a better direction.
