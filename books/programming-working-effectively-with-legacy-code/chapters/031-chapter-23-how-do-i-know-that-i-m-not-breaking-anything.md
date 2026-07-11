<span id="page-331-0"></span>
# Chapter 23: How Do I Know That I'm Not Breaking Anything?


Code is a strange sort of building material. Most materials that you can make things from, such as metal, wood, and plastic, fatigue. They break when you use them over time. Code is different. If you leave it alone, it never breaks. Short of the stray cosmic ray flipping a bit on your storage media, the only way it gets a fault is for someone to edit it. Run a machine made of metal over and over again, and it will eventually break. Run the same code over and over again, and, well, it will just run over and over again.

This puts a large burden on us as developers. Not only are we the primary agents that introduce faults in software, but it's also pretty easy to do so. How easy is it to change code? Mechanically, it is pretty simple. Anyone can open a text editor and spew the most arcane nonsense into it. Type in a poem. Some of them compile (go to <www.ioccc.org>and see the Obfuscated C code contest for details). Humor aside, it really is amazing how easy it is to break software. Have you ever tracked down a mysterious bug only to discover that it was some stray character that you accidentally typed? Some character that was entered when the cover of a book dropped down as you passed it to someone over your keyboard? Code is pretty fragile material.

In this chapter, we discuss a variety of ways to reduce risk when we edit. Some of them are mechanical and some are psychological (ouch!), but focusing on them is important, especially as we break dependencies in legacy code to get tests in place.

> **How Do I Know That I'm Not Breaking Anything?**

<span id="page-332-1"></span><span id="page-332-0"></span>![](../assets/_page_332_Picture_1.jpeg)

## Hyperaware Editing

What do we do when we edit code, really? What are we trying to accomplish? We usually have large goals. We want to add a feature or fix a bug. It's great to know what those goals are, but how do we translate them into action?

When we sit down at a keyboard, we can classify every keystroke that we make into one of two categories. The keystroke either changes the behavior of the software or it doesn't. Typing text in a comment? That doesn't change behavior. Typing text in a string literal? That does, most of the time. If the string literal is in code that is never called, behavior won't change. The keystroke that you do later to finish a method call that uses that string literal, well, that one changes behavior. So technically, holding down the spacebar when you are formatting your code is refactoring in a very micro sense. Sometimes typing code is refactoring also. Changing a numeric literal in an expression that is used in your code isn't refactoring; it's a *functional change,* and it's important to know that when you are typing.

This is the meat of programming, knowing exactly what each of our keystrokes does. This doesn't mean that we have to be omniscient, but anything that helps us know—really know—how we are affecting software when we type can help us reduce bugs. *Test-driven development (88)* is very powerful in this way. When you can get your code into a test harness and run tests against it in less than a second, you can run the tests whenever you need to incredibly fast and really know what the effects of a change are.

If it isn't out by the time this book is released, I suspect that someone will soon develop an IDE that allows you to specify a set of tests that will run at every keystroke. It would be an incredible way of closing the feedback loop.

It has to happen. It just seems inevitable. There are already IDEs that check syntax on each keystroke and change the color of code when there are errors. Edit-triggered testing is the next step.

Tests foster hyperaware editing. Pair programming does also. Does hyperaware-editing sound exhausting? Well, too much of anything is exhausting. The key thing is that it isn't frustrating. Hyperaware editing is a flow state, a state in which you can just shut out the world and work sensitively with the code. It can actually be very refreshing. Personally, I get far more tired when I'm not getting any feedback. At that point, I get scared that I'm breaking the code without knowing it. I'm struggling to maintain all of this state in my head, remembering what I've changed and what I haven't, and thinking about how I'll be able to convince myself later that I've really done what I set out to do.

**Hyperaware Editing**

<span id="page-333-1"></span>
<span id="page-333-0"></span>
## Single-Goal Editing

I don't expect that everyone's first impressions of the computer industry are the same, but when I first thought about becoming a programmer, I was really captivated by stories about super-smart programmers, those guys and gals who could keep the state of an entire system in their heads, write correct code on the fly, and know immediately whether some change was right or wrong. It's true that people vary widely in their ability to hold on to large amounts of arcane detail in their heads. I can do that, to some degree. I used to know many of the obscure parts of the C++ programming language, and, at one point, I had decent recall of the details of the UML metamodel before I realized that being a programmer and knowing that much about the details of UML was really pointless and somewhat sad.

The truth is, there are many different kinds of "smart." Holding on to a lot of state mentally can be useful, but it doesn't really make us better at decisionmaking. At this point in my career, I think I'm a much better programmer than I used to be, even though I know less about the details of each language I work in. Judgment is a key programming skill, and we can get into trouble when we try to act like super-smart programmers.

Has this ever happened to you? You start to work on one thing, and then you think, "Hmm, maybe I should clean this up." So you stop to refactor a bit, but you start to think about what the code should really look like, and then you pause. That feature you were working on still needs to be done, so you go back to the original place where you were editing code. You decide that you need to call a method, and then you hop over to where the method is, but you discover that the method is going to need to do something else, so you start to change it while the original change was pending and (catching breath) your pair partner is next to you yelling "Yeah, yeah, yeah! Fix that and then we'll do this." You feel like a racehorse running down the track, and your partner isn't really helping. He's riding you like a jockey or, worse, a gambler in the stands.

Well, that's how it goes on some teams. A pair has an exciting programming episode, but the last three quarters of it involve fixing all of the code they broke in the previous quarter. Sounds horrible, right? But, no, sometimes it's fun. You and your partner get to saunter away from the machine like heroes. You met the beast in its lair and killed it. You're top dog.

Is it worth it? Let's look at another way of doing this.

You need to make a change to a method. You already have the class in a test harness, and you start to make the change. But then you think, "Hey, I'll need to change this other method over here," so you stop and you navigate to it. It **Single-Goal Editing**

<span id="page-334-1"></span>![](../assets/_page_334_Picture_1.jpeg)

looks messy, so you start to reformat a line or two to see what is going on. Your partner looks at you and says, "What are you doing?" You say, "Oh, I was checking to see if we'll have to change method X." Your partner says, "Hey let's do one thing at a time." Your partner writes down the name of method X on a piece of paper next to the computer, and you go back and finish the edit. You run your tests and notice that all of them pass. Then you go over and look at the other method. Sure enough, you have to change it. You start to write another test. After a bit more programming, you run your tests and start to integrate. You and your partner look over to the other side of the table. There you see two other programmers. One is yelling "Yeah, yeah, yeah! Fix that and then we'll do this." They've been working on that task for hours, and they look pretty exhausted. If history is any guide, they'll fail integration and spend a few more hours working together.

<span id="page-334-0"></span>I have this little mantra that I repeat to myself when I'm working: "Programming is the art of doing one thing at a time." When I'm pairing, I always ask my partner to challenge me on that, to ask me "What are you doing?" If I answer more than one thing, we pick one. I do the same for my partner. Frankly, it's just faster. When you are programming, it is pretty easy to pick off too big of a chunk at a time. If you do, you end up thrashing and just trying things out to make things work rather than working very deliberately and really knowing what your code does.

### Preserve Signatures

When we edit code there are many ways we can make mistakes. We can misspell things, we can use the wrong data type, we can type one variable and mean another—the list is endless. Refactoring is particularly error-prone. Often it involves very invasive editing. We copy things around and make new classes and methods; the scale is much larger than just adding in a new line of code.

In general, the way to handle the situation is to write tests. When we have tests in place, we're able to catch many of the errors that we make when we change code. Unfortunately, in many systems, we have to refactor a bit just to make the system testable enough to refactor more. These initial refactorings (the dependency-breaking techniques in the catalog in Chapter 25) are meant to be done without tests, and they have to be particularly conservative.

When I first started using these techniques, it was tempting to do too much. When I needed to extract the entire body of a method, rather than just copying and pasting the arguments when I declared a method, I did other cleanup work

**Preserve Signatures** as well. For example, when I had to extract the body of a method and make it static (*Expose Static Method (345)*), like this:

```
public void process(List orders, 
 int dailyTarget, 
 double interestRate, 
 int compensationPercent) {
 ...
 // complicated code here
 ...
```

I extracted it like this, creating a couple of helper classes along the way.

```
public void process(List orders,
                  int dailyTarget,
                  double interestRate, 
                  int compensationPercent) {
 processOrders(new OrderBatch(orders),
 new CompensationTarget(dailyTarget,
                   interestRate * 100,
                   compensationPercent));
```

I had good intentions. I wanted to make the design better as I was breaking dependencies, but it didn't work out very well. I ended up making foolish mistakes, and with no tests to catch them, often they were found far later than they needed to be.

When you are breaking dependencies for test, you have to apply extra care. One thing that I do is *Preserve Signatures* whenever I can. When you avoid changing signatures at all, you can cut/copy and paste entire method signatures from place to place and minimize any chances of errors.

In the previous example, I would end up with code like this:

```
public void process(List orders,
              int dailyTarget,
              double interestRate, 
              int compensationPercent) {
 processOrders(orders, dailyTarget, interestRate, 
 compensationPercent);
private static void processOrders(List orders,
 int dailyTarget, 
 double interestRate, 
 int compensationPercent) {
 ...
```

**Preserve Signatures**

<span id="page-336-0"></span>![](../assets/_page_336_Picture_1.jpeg)

The argument editing that I had to perform to do this was very easy. Essentially, only a couple of steps were involved:

1. I copied the entire argument list into my cut/copy paste buffer:

```
List orders, 
 int dailyTarget, 
 double interestRate, 
 int compensationPercent
       2. Then I typed the new method declaration:
private void processOrders() {
}
       3. I pasted the buffer into the new method declaration:
private void processOrders(List orders, 
 int dailyTarget, 
                      double interestRate, 
                      int compensationPercent) {
}
       4. I then typed the call for the new method:
processOrders();
       5. I pasted the buffer into the call:
processOrders(List orders, 
 int dailyTarget, 
 double interestRate, 
 int compensationPercent);
       6. Finally, I deleted the types, leaving the names of the arguments:
processOrders(orders, 
 dailyTarget,
```

When you do these moves over and over again, they become automatic and you can feel more confidence in your changes. You can concentrate on some of the other lingering issues that can cause errors when you break dependencies. For instance, is your new method hiding a method with the same name signature in a base class?

 **interestRate, compensationPercent);**

A couple of different scenarios exist for *Preserve Signatures.* You can use the technique to make new method declarations. You can also use it to create a set of instance methods for all of the arguments to a method when you are doing the *Break out Method Object* refactoring. See *Break out Method Object (330)* for details.

**Preserve Signatures**

<span id="page-337-1"></span>
<span id="page-337-0"></span>
### Lean on the Compiler

The primary purpose of a compiler is to translate source code into some other form, but in statically typed languages, you can do much more with a compiler. You can take advantage of its type checking and use it to identify changes you need to make. I call this practice *leaning on the compiler*. Here is an example of how to do it.

In a C++ program, I have a couple of global variables.

```
double domestic_exchange_rate;
double foreign_exchange_rate;
```

A set of methods in the same file uses the variables, but I want to find some way to change them under test so I use the *Encapsulate Global References (339)* technique from the catalog.

To do this, I write a class around the declarations and declare a variable of that class.

```
class Exchange
public:
 double domestic_exchange_rate;
 double foreign_exchange_rate;
};
```

Exchange exchange;

Now I compile to find all of the places where the compiler can't find domestic\_exchange\_rate and foreign\_exchange\_rate, and I change them so that they are accessed off the exchange object. Here are before and after shots of one of those changes:

```
 total = domestic_exchange_rate * instrument_shares;
   becomes:
 total = exchange.domestic_exchange_rate * instrument_shares;
```

The key thing about this technique is that you are letting the compiler guide you toward the changes you need to make. This doesn't mean that you stop thinking about what you need to change; it just means that you can let the compiler do the legwork for you, in some cases. It's just very important to know what the compiler is going to find and what it isn't so that we aren't lulled into false confidence.

**Lean on the Compiler**

<span id="page-338-0"></span>![](../assets/_page_338_Picture_1.jpeg)

#### *Lean on the Compiler* involves two steps:

- 1. Altering a declaration to cause compile errors
- 2. Navigating to those errors and making changes.

You can lean on the compiler to make structural changes to your program, as we did in the *Encapsulate Global References (339)* example. You can also use it to initiate type changes. One common case is changing the type of a variable declaration from a class to an interface, and using the errors to determine which methods need to be on the interface.

Leaning on the compiler isn't always practical. If your builds take a long time, it might be more practical to search for the places where you need to make changes. See Chapter 7, *It Takes Forever to Make a Change*, for ways of getting past that problem. But when you can do it, *Lean on the Compiler* is a useful practice. But be careful; you can introduce subtle bugs if you do it blindly.

The language feature that gives us the most possibility for error when we lean is inheritance. Here's an example:

We have a class method named getX() in a Java class:

```
public int getX() {
 return x;
}
   We want to find all occurrences of it so that we comment it out:
/*
public int getX() {
 return x;
} */
```

Now we recompile.

Guess what? We didn't get any errors. Does this mean that getX() is an unused method? Not necessarily. If getX() is declared as a concrete method in a superclass, commenting out getX in our current class will just cause the one in the superclass to be used. A similar situation can occur with variables and inheritance.

*Lean on the Compiler* is a powerful technique, but you have to know what its limits are; if you don't, you can end up making some serious mistakes.

#### Pair Programming

**Lean on the Compiler**

Chances are, you've already heard of *Pair Programming*. If you are using Extreme Programming (XP) as your process you are probably doing it. Good. It is a remarkably good way to increase quality and spread knowledge around a team.

If you aren't pair programming right now, I suggest that you try it. In particular, I insist that you pair when you use the dependency-breaking techniques I've described in this book.

It's easy to make a mistake and have no idea that you've broken the software. A second set of eyes definitely helps. Let's face it, working in legacy code is surgery, and doctors never operate alone.

For more information about pair programming, see *Pair Programming Illuminated* by Laurie Williams and Robert Kessler (Addison-Wesley 2002) and visit [www.pairprogramming.com.](https://www.pairprogramming.com)

> **Lean on the Compiler**

![](../assets/_page_340_Picture_0.jpeg)
