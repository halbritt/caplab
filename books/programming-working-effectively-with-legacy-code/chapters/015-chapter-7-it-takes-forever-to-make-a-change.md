<span id="page-99-2"></span>
<span id="page-99-0"></span>
# Chapter 7: It Takes Forever to Make a Change


<span id="page-99-1"></span>How long does it take to make changes? The answer varies widely. On projects with terribly unclear code, many changes take a long time. We have to hunt through the code, understand all of the ramifications of a change, and then make the change. In clearer areas of the code, this can be very quick, but in really tangled areas, it can take a very long time. Some teams have it far worse than others. For them, even the simplest code changes take a long time to implement. People on those teams can find out what feature they need to add, visualize exactly where to make the change, go into the code and make the change in five minutes, and still not be able to release their change for several hours.

Let's look at the reasons and some of the possible solutions.

**It Takes Forever to Make a Change**

## Understanding

As the amount of code in a project grows, it gradually surpasses understanding. The amount of time it takes to figure out what to change just keeps increasing.

Part of this is unavoidable. When we add code to a system, we can add it to existing classes, methods, or functions, or we can add new ones. In either case, it is going to take a while to figure out how to make a change if we are unfamiliar with the context.

However, there is one key difference between a well-maintained system and a legacy system. In a well-maintained system, it might take a while to figure out how to make a change, but once you do, the change is usually easy and you feel much more comfortable with the system. In a legacy system, it can take a long time to figure out what to do, and the change is difficult also. You might also feel like you haven't learned much beyond the narrow understanding you had <span id="page-100-1"></span><span id="page-100-0"></span>to acquire to make the change. In the worst cases, it seems like no amount of time will be enough to understand everything you need to do to make a change, and you have to walk blindly into the code and start, hoping that you'll be able to tackle all the problems that you encounter.

Systems that are broken up into small, well-named, understandable pieces enable faster work. If understanding is a big issue on your project, take a look at Chapter 16, *I Don't Understand the Code Well Enough to Change It*, and Chapter 17, *My Application Has No Structure*, to get some ideas about how to proceed.

## Lag Time

Changes often take a long time for another very common reason: lag time. Lag time is the amount of time that passes between a change that you make and the moment that you get real feedback about the change. At the time of this writing, the Mars rover Spirit is crawling across the surface of Mars taking pictures. It takes about seven minutes for signals to get from Earth to Mars. Luckily, Spirit has some onboard guidance software that helps it move around on its own. Imagine what it would be like to drive it manually from Earth. You operate the controls and find out 14 minutes later how far the rover moved. Then you decide what you want to do next, do it, and wait another 14 minutes to find out what happened. It seems ridiculously inefficient, right? Yet, when you think about it, that is exactly the way most of us work right now when we develop software. We make some changes, start a build, and then find out what happened later. Unfortunately, we don't have software that knows how to navigate around obstacles in the build, things such as test failures. What we try to do instead is bundle a bunch of changes and make them all at once so that we don't have to build too often. If our changes are good, we move along, albeit as slow as the Mars rover. If we hit an obstacle, we go even slower.

The sad thing about this way of working is that, in most languages, it is completely unnecessary. It's a complete waste of time. In most mainstream languages, you can always break dependencies in a way that lets you recompile and run tests against whatever code you are working on in less than 10 seconds. If a team is really motivated, its members can get it down to less than five seconds, in most cases. What it comes down to is this: You should be able to compile every class or module in your system separately from the others and in its own test harness. When you have that, you can get very rapid feedback, and that just helps development go faster.

**Lag Time**

<span id="page-101-1"></span>The human mind has some interesting qualities. If we have to perform a short task (5-10 seconds long) and we can only take a step once every minute, we usually do it and then pause. If we have to do some work to figure out what to do at the next step, we start to plan. After we plan, our minds wander until we can do the next step. If we compress the time betwen steps down from a minute to a few seconds, the quality of the mental work becomes different. We can use feedback to try out approaches quickly. Our work becomes more like driving than like waiting at a bus stop. Our concentration is more intense because we aren't constantly waiting for the next chance to do something. Most important, the amount of time that it takes us to notice and correct mistakes is much smaller.

<span id="page-101-0"></span>What keeps us from being able to work this way all the time? Some people can. People who program in interpreted languages can often get near-instantaneous feedback when they work. For the rest of us, who work in compiled languages, the main impediment is dependency, the need to compile something that we don't care about just because we want to compile something else.

## Breaking Dependencies

Dependencies can be problematic, but, fortunately, we can break them. In object-oriented code, often the first step is to attempt to instantiate the classes that we need in a test harness. In the easiest cases, we can do this just by importing or including the declaration of the classes we depend upon. In harder cases, try the techniques in Chapter 9, *I Can't Get This Class into a Test Harness*. When you are able to create an object of a class in a test harness, you might have other dependencies to break if you want to test individual methods. In those cases, see Chapter 10, *I Can't Run This Method in a Test Harness*.

When you have a class that you need to change in a test harness, generally, you can take advantage of very fast edit-compile-link-test times. Usually, the execution cost for most methods is relatively low compared to the costs of the methods that they call, particularly if the calls are calls to external resources such as the database, hardware, or the communications infrastructure. The times when this doesn't happen are usually cases in which the methods are very calculation-intensive. The techniques I've outlined in Chapter 22, *I Need to Change a Monster Method and I Can't Write a Test for It*, can help.

In many cases, change can be this straightforward, but often people working in legacy code are stopped dead in their tracks by the first step: attempting to get a class into a test harness. This can be a very large effort in some systems. Some classes are very huge; others have so many dependencies that they seem to **Breaking Dependencies** <span id="page-102-0"></span>overwhelm the functionality that you want to work on entirely. In cases like these, it pays to see if you can cut out a larger chunk of the code and put it under test. See Chapter 12, *I Need to Make Many Changes in One Area. Do I Have to Break Dependencies for All the Classes Involved?* That chapter contains a set of techniques that you can use to find *pinch points (180)*, places where test writing is easier.

In the rest of this chapter, I describe how you can go about changing the way that your code is organized to make builds easier.

### Build Dependencies

In an object-oriented system, if you have a cluster of classes that you want to build more quickly, the first thing that you have to figure out is which dependencies will get in the way. Generally, that is rather easy: You just attempt to use the classes in a test harness. Nearly every problem that you run into will be the result of some dependency that you should break. After the classes run in a test harness, there are still some dependencies that can affect compile time. It pays to look at everything that depends upon what you've been able to instantiate. Those things will have to recompile when you rebuild the system. How can you minimize this?

The way to handle this is to extract interfaces for the classes in your cluster that are used by classes outside the cluster. In many IDEs, you can extract an interface by selecting a class and making a menu selection that shows you a list of all of the methods in the class and allows you to choose which ones you want to be part of the new interface. Afterward, the tools allow you to provide the name of the new interface. They also give you the option of letting it replace references to the class with references to the interface everywhere it can in the code base. It's an incredibly useful feature. In C++, *Extract Implementer (356)* is a little easier than *Extract Interface (362)*. You don't have to change the names of references all over the place, but you do have to change the places that create instances of the old class (see *Extract Implementer (356)* for details).

When we have these clusters of classes under test, we have the option of changing the physical structure of our project to make builds easier. We do this by moving the clusters off to a new package or library. Builds do become more complex when we do this, but here is the key: As we break dependencies and section off classes into new packages or libraries, the overall cost of a rebuild of the entire system grows, but the average time for a build can decrease.

**Breaking Dependencies**

Let's look at an example. Figure 7.1 shows a small set of collaborating classes, all in the same package.

![](../assets/_page_103_Figure_3.jpeg)

**Figure 7.1** *Opportunity handling classes.*

We want to make some changes to the AddOpportunityFormHandler class, but it would be nice if we could make our build faster, too. The first step is to try to instantiate an AddOpportunityFormHandler. Unfortunately, all of the classes it depends upon are concrete. AddOpportunityFormHandler needs a ConsultantSchedulerDB and an AddOpportunityXMLGenerator. It could very well be the case that both of those classes depend on other classes that aren't in the diagram.

If we attempt to instantiate an AddOpportunityFormHandler, who knows how many classes we'll end up using? We can get past this by starting to break dependencies. The first dependency we encounter is ConsultantSchedulerDB. We need to create one to pass to the AddOpportunityFormHandler constructor. It would be awkward to use that class because it connects to the database, and we don't want to do that during testing. However, we could use *Extract Implementer (356)* and break the dependency as shown in Figure 7.2.

**Breaking Dependencies**

<span id="page-104-0"></span>![](../assets/_page_104_Figure_2.jpeg)

**Figure 7.2** *Extracting an implementer on* ConsultantSchedulerDB*.* 

Now that ConsultantSchedulerDB is an interface, we can create an AddOpportunityFormHandler using a fake object that implements the ConsultantSchedulerDB interface. Interestingly, by breaking that dependency, we've made our build faster under some conditions. The next time that we make a modification to ConsultantSchedulerDBImpl, AddOpportunityFormHandler doesn't have to recompile. Why? Well, it doesn't directly depend on the code in ConsultantSchedulerDBImpl anymore. We can make as many changes as we want to the ConsultantSchedulerD-BImpl file, but unless we do something that forces us to change the ConsultantSchedulerDB interface, we won't have to rebuild the AddOpportunityForm-Handler class.

If we want, we can isolate ourselves from forced recompilation even further, as shown in Figure 7.3. Here is another design for the system that we arrive at by using *Extract Implementer (356)* on the OpportunityItem class.

**Breaking Dependencies**

![](../assets/_page_105_Figure_2.jpeg)

**Figure 7.3** *Extracting an implementer on* OpportunityItem*.*

Now AddOpportunityFormHandler doesn't depend on the original code in OpportunityItem at all. In a way, we've put a "compilation firewall" in the code. We can make as many changes as we want to ConsultantSchedulerDBImpl and OpportunityItemImpl, but that won't force AddOpportunityFormHandler to recompile, and it won't force any users of AddOpportunityFormHandler to recompile. If we wanted to make this very explicit in the package structure of the application, we could break up our design into the separate packages shown in Figure 7.4.

**Breaking Dependencies**

![](../assets/_page_105_Figure_6.jpeg)

**Figure 7.4** *Refactored package structure.* 

<span id="page-106-0"></span>Now we have a package, OpportunityProcessing, that really has no dependencies on the database implementation. Whatever tests we write and place in the package should compile quickly, and the package itself doesn't have to recompile when we change code in the database implementation classes.

#### The Dependency Inversion Principle

When your code depends on an interface, that dependency is usually very minor and unobtrusive. Your code doesn't have to change unless the interface changes, and interfaces typically change far less often than the code behind them. When you have an interface, you can edit classes that implement that interface or add new classes that implement the interface, all without impacting code that uses the interface.

For this reason, it is better to depend on interfaces or abstract classes than it is to depend on concrete classes. When you depend on less volatile things, you minimize the chance that particular changes will trigger massive recompilation.

So far, we've done a few things to prevent AddOpportunityFormHandler from being recompiled when we modify classes it depends upon. That does make builds faster, but it is only half of the issue. We can also make builds faster for code that depends on AddOpportunityFormHandler. Let's look at the package design again, in Figure 7.5.

![](../assets/_page_106_Figure_7.jpeg)

![](../assets/_page_106_Figure_8.jpeg)

**Figure 7.5** *Package structure.* 

<span id="page-107-1"></span>AddOpportunityFormHandler is the only public production (non-test) class in OpportunityProcessing. Any classes in other packages that depend on it have to recompile when we change it. We can break that dependency also by using *Extract Interface (362)* or *Extract Implementer (356)* on AddOpportunityForm Handler. Then, classes in other packages can depend on the interfaces. When we do that, we've effectively shielded all of the users of this package from recompilation when we make most changes.

<span id="page-107-0"></span>We can break dependencies and allocate classes across different packages to make build time faster, and doing it is very worthwhile. When you can rebuild and run your tests very quickly, you can get greater feedback as you develop. In most cases, that means fewer errors and less aggravation. But it isn't free. There is some conceptual overhead in having more interfaces and packages. Is that a fair price to pay compared to the alternative? Yes. At times, it can take a little longer to find things when you have more packages and interfaces, but when you do, you can work with them very easily.

When you introduce more interfaces and packages into your design to break dependencies, the amount of time it takes to rebuild the entire system goes up slightly. There are more files to compile. But the average time for a make, a build based on what *needs* to be recompiled, can go down dramatically.

When you start to optimize your average build time, you end up with areas of code that are very easy to work with. It might be a bit of a pain to get a small set of classes compiling separately and under test, but the important thing to remember is that you have to do it only once for that set of classes; afterward, you get to reap the benefits forever.

**Summary**

### Summary

The techniques I've shown in this chapter can be used to speed up build time for small clusters of classes, but this is only a small portion of what you can do using interfaces and packages to manage dependencies. Robert C. Martin's book *Agile Software Development: Principles, Patterns, and Practices* (Pearson Education, 2002) presents more techniques along these lines that every software developer should know.

![](../assets/_page_108_Picture_0.jpeg)
