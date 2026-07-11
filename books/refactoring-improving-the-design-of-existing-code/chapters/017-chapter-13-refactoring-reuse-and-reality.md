# Chapter 13: Refactoring, Reuse, and Reality

*by William Opdyke*

Martin Fowler and I first met in Vancouver during OOPSLA 92. A few months earlier, I had completed my doctoral dissertation on refactoring object-oriented frameworks[1] at the University of Illinois. While I was considering continuing my research into refactoring, I was also exploring other options, such as medical informatics. Martin was working on a medical informatics application at the time, which is what brought us together to chat over breakfast in Vancouver. As Martin relates earlier in this book, we spent a few minutes discussing my refactoring research. He had limited interest in the topic at the time, but as you are now aware, his interest in the topic has grown.

At first glance, it might appear that refactoring began in academic research labs. In reality, it began in the software development trenches, where object-oriented programmers, then using Smalltalk, encountered situations in which techniques were needed to better support the process of framework development or, more generally, to support the process of change. This spawned research that has matured to the point at which we feel it is "ready for prime time"—the point at which a broader set of software professionals can experience the benefits of refactoring.

When Martin offered me the opportunity to write a chapter in this book, several ideas came to mind. I could describe the early refactoring research, the era in which Ralph Johnson and I came together from very different technical backgrounds to focus on support for change in objectoriented software. I could discuss how to provide automated support for refactoring, an area of my research quite different from the focus of this book. I could share some of the lessons I have learned about how refactoring relates to the day-to-day concerns of software professionals, especially those who work on large projects in industry.

Many of the insights I gained during my refactoring research have been useful in a wide range of areas—in assessing software technologies and formulating product evolution strategies, in developing prototypes and products in the telecommunication industry, and in training and consulting with product development groups.

I decided to focus briefly on many of these issues. As the title of this chapter implies, many of the insights regarding refactoring apply more generally to issues such as software reuse, product evolution, and platform selection. Although parts of this chapter briefly touch on some of the more interesting theoretical aspects of refactoring, the primary focus is on practical, real-world concerns and how they can be addressed.

If you want to explore refactoring further, see Resources and References for Refactoring later in this chapter.

## A Reality Check

I worked at Bell Labs for several years before I decided to pursue my doctoral studies. Most of that time was spent working in a part of the company that developed electronic switching systems. Such products have very tight constraints with respect to both reliability and the speed with which they handle phone calls. Thousands of staff-years have been invested in developing and evolving such systems. Product lifetimes have spanned decades. Most of the cost of developing these systems comes not in developing the initial release but in changing and adapting the systems over time. Ways to make such changes easier and less costly would result in a big win for the company.

Because Bell Labs was funding my doctoral studies, I wanted a field of research that was not only technically interesting but also related to a practical business need. In the late 1980s, objectoriented technology was just beginning to emerge from the research labs. When Ralph Johnson proposed a research topic that focused both on object-oriented technology and on supporting the process of change and software evolution, I grabbed it.

I've been told that when people finish their doctoral studies, they rarely are neutral about their topic. Some are sick of the topic and quickly move on to something else. Others remain enthusiastic about the topic. I was in the latter camp.

When I returned to Bell Labs after receiving my degree, a strange thing happened. The people around me were not nearly as excited about refactoring as I was.

I can vividly recall presenting a talk in early 1993 at a technology exchange forum for staff at AT&T Bell Labs and NCR (we were all part of the same company at the time). I was given 45 minutes to speak on refactoring. At first the talk seemed to go well. My enthusiasm for the topic came across. But at the end of the talk, there were very few questions. One of the attendees came up afterward to learn more; he was beginning his graduate work and was fishing around for a research topic. I had hoped to see some members of development projects show eagerness in applying refactoring to their jobs. If they were eager, they didn't express it at the time.

People just didn't seem to get it.

Ralph Johnson taught me an important lesson about research: if someone (a reviewer of a paper, an attendee at a talk) comments, "I don't understand" or just doesn't get it, it's *our* fault. It is *our* responsibility to work hard to develop and communicate our ideas.

Over the next couple years, I had numerous opportunities to talk about refactoring at AT&T Bell Labs internal forums and at outside conferences and workshops. As I talked more with developers in the trenches, I started to understand why my earlier messages didn't come across clearly. The disconnect was caused partly by the newness of object-oriented technology. Those who had worked with it had rarely progressed beyond the initial release and hence had not yet faced the tough evolution problems refactoring can help solve. This was the typical researcher's dilemma—the state of the art was beyond the state of common practice. However, there was another, troubling cause for the disconnect. There were several commonsense reasons developers, even if they bought into the benefits of refactoring, were reluctant to refactor *their* programs. These concerns had to be addressed before refactoring could be embraced by the development community.

## Why Are Developers Reluctant to Refactor Their Programs?

Suppose you are a software developer. If your project is a fresh start (with no backward compatibility concerns) *and* if you understand the problem your system is intended to solve *and* if your funder is willing to pay until *you* are satisfied with the results, consider yourself very fortunate. Although such a scenario may be ideal for applying object-oriented techniques, for most of us such a scenario is only a dream.

More often you are asked to extend an existing piece of software. You have a less-than-complete understanding of what you are doing. You are under schedule pressure to produce. What can you do?

You can rewrite the program. You can leverage your design experience and correct the ills of the past and be creative and have fun. Who will foot the bill? How can you be sure that the new system does everything the old system used to do?

You can copy and modify parts of the existing system to extend its capabilities. This may seem expedient and may even be viewed as a way to demonstrate reuse; you don't even have to understand what you are reusing. However, over time, errors propagate themselves, programs become bloated, program design becomes corrupted, and the incremental cost of change escalates.

Refactoring is a middle ground between the two extremes. It is a way to restructure software to make design insights more explicit, to develop frameworks and extract reusable components, to clarify the software architecture, and to prepare to make additions easier. Refactoring can help you leverage your past investment, reduce duplication, and streamline a program.

Suppose you as a developer buy into these advantages. You agree with Fred Brooks that dealing with change is one of the "essential complexities" of developing software.[2] You agree that in the abstract refactoring can provide the stated advantages.

Why might you still not refactor *your* programs? Here are four possible reasons:

- 1. You might not understand how to refactor.
- 2. If the benefits are long-term, why exert the effort now? In the long term, you might not be with the project to reap the benefits.
- 3. Refactoring code is an overhead activity; you're paid to write *new* features.
- 4. Refactoring might break the existing program.

These are all valid concerns. I have heard them expressed by staff at telecommunication and at high technology companies. Some of these are technical concerns; others are management concerns. All must be addressed before developers will consider refactoring their software. Let's deal with each of these issues in turn.

### Understanding How and Where to Refactor

How can you learn how to refactor? What are the tools and techniques? How can they be combined to accomplish something useful? When should we apply them? This book defines several dozen refactorings that Martin found useful in his work. It presents examples of how the refactorings can be applied to support significant changes to programs.

In the Software Refactory project at the University of Illinois, we chose a minimalist approach. We defined a smaller set of refactorings[1], [3] and showed how they could be applied. We based our collection of refactorings on our own programming experiences. We evaluated the structural evolution of several object-oriented frameworks, mostly in C++, and talked with and read the retrospectives of several experienced Smalltalk developers. Most of our refactorings are low level, such as creating or deleting a class, variable, or function; changing attributes of variables and functions, such as their access permissions (e.g., public or protected) and function arguments; or moving variables and functions between classes. A smaller set of high-level refactorings are used for operations such as creating an abstract superclass, simplifying a class by means of subclassing and simplifying conditionals, or splitting off part of an existing class to create a new, reusable component class (often converting between inheritance and delegation or aggregation). The more complex refactorings are defined in terms of the low-level refactorings. Our approach was motivated by concern for automated support and safety, which I discuss later.

Given an existing program, what refactorings should you apply? That depends, of course, on your goals. One common reason, which is the focus of this book, is to restructure a program to make it easier to add (near term) a new feature. I discuss this in the next section. There are, however, other reasons why you might apply refactorings.

Experienced object-oriented programmers and those who have been trained in design patterns and good design techniques have learned that several desirable structural qualities and characteristics of programs have been shown to support extensibility and reuse.[4], [5], [6] Object-oriented design techniques such as CRC[7] focus on defining classes and their protocols. Although the focus is on upfront design, there are ways to evaluate existing programs against such guidelines.

An automated tool can be used to identify structural weaknesses in a program, such as functions that have an excessively large number of arguments or are excessively long. These are candidates for refactoring. An automated tool also can identify structural similarities that may indicate redundancies. For example, if two functions are nearly identical (as often happens when a copy-and-modify process is applied to a first function to produce a second), such similarities can be detected and refactorings suggested that can move common code to one place. If two variables in different parts of a program have the same name, they sometimes can be replaced with a single variable that is inherited in both places. These are a few very simple examples. Many other, more complex cases can be detected and corrected with an automated tool. These structural abnormalities or structural similarities don't always mean that you'd want to apply a refactoring, but often they do.

Much of the work on design patterns has focused on good programming style and on useful patterns of interactions among parts of a program that can be mapped into structural characteristics and into refactoring. For example, the applicability section of the template method pattern[8] refers to our abstract superclass refactoring.[9]

I have listed[1] some of the heuristics that can help identify candidates for refactoring in a C++ program. John Brant and Don Roberts[10],[11] have created a tool that applies an extensive set of heuristics to automatically analyze Smalltalk programs. They suggest refactorings that might improve the program design and where to apply them.

Applying such a tool to analyze your program is somewhat analogous to applying lint to a C or C++ program. The tool isn't smart enough to understand the meaning of the program. Only some of the suggestions it makes on the basis of structural program analysis may be changes you really want to make. As a programmer, you make the call. You decide which recommendations to apply to your program. Those changes should improve the structure of your program and better support changes down the road.

Before programmers can convince themselves that they ought to refactor their code, they need to understand how and where to refactor. There is no substitute for experience. We leveraged the insights of experienced object-oriented developers in our research to obtain a set of useful refactorings and insights about where they ought to be applied. Automated tools can analyze the structure of a program and suggest refactorings that might improve that structure. As with most disciplines, tools and techniques can help *but only if you use them.* As programmers refactor their code, their understanding grows.

| Refactoring C++ Programs |  |  |
|--------------------------|--|--|
| Bill Opdyke              |  |  |

When Ralph Johnson and I began our refactoring research in 1989, the C++ programming language was evolving and was becoming very popular within the object-oriented community. The importance of refactoring had first been recognized within the Smalltalk community. We felt that demonstrating its applicability to C++ programs would interest a broader community of object-oriented developers.

C++ has language features, most notably its static type checking, that simplify some program analysis and refactoring tasks. On the other hand, the C++ language is complex, largely because of its history and evolution from the C programming language. Some programming styles allowable in C++ make it difficult to refactor and evolve a program.

### Language Features and Programming Styles That Support Refactoring

The static typing features of C++ make it relatively easy to narrow possible references to the part of the program that you might want to refactor. To pick a simple but frequent case, suppose you want to rename a member function of a C++ class. To correctly apply the renaming, you must change the function declaration and all references to that function. Finding and changing the references can be difficult if the program is large.

Compared with Smalltalk, C++ has class inheritance and protectionaccess control mode (public, protected, private) features that make it easier to determine where references to the function being renamed might be. If the function to be renamed is declared private to the class, then references to that function can occur only within the class itself or in classes that are declared as friends of that class. If the function is declared protected, references can be found only in the class, its subclasses (and their descendents), and in friends of the class. If the function is declared public (the least restrictive protection mode), the analysis is still limited to the classes listed for "protected" functions and operations on instances of the class that contains the function, its subclasses, and its descendents.

In some very large programs, functions with the same name might be declared in different places in the program. In some cases, two or more functions with the same name might be better replaced with a single function; there are refactorings that can often be applied to make this change. On the other hand, it is sometimes the case that one of the functions ought to be renamed while the other function is kept the same. In a multiperson project, two or more programmers might have given the same name to functions that are independent of each other. In C++, when changing the name of one of these functions it is almost always

easy to determine which references refer to the function being renamed and which refer to the other function. In Smalltalk, that analysis is more difficult.

Because C++ uses subclassing to implement subtyping, the scope to a variable or function usually can be generalized or specialized by moving it up or down an inheritance hierarchy. The efforts to analyze a program and perform the refactoring are fairly straightforward.

Several good design principles applied during initial development and throughout the software development process ease the process of refactoring and make it easier to evolve software. Defining member variables and most member functions as private or protected is an abstraction technique that often makes it easier to refactor the internals of a class while minimizing changes made elsewhere in a program. Using inheritance to model generalization and specialization hierarchies (as is natural in C++) makes it fairly straightforward to later generalize or specialize the scope of member variables or functions using refactorings to move these members within inheritance hierarchies.

Features in C++ environments support refactoring. If while refactoring a program a programmer introduces a bug, often the C++ compiler flags the error. Many C++ software development environments provide powerful capabilities for cross referencing and code browsing.

### Language Features and Programming Styles

### That Complicate Refactoring

The compatibility C++ with C is, as most of you well know, a doubleedged sword. Many programs have been written in C and many programmers have been training in C, which (on the surface, at least) makes it easier to migrate to C++ than to other object-oriented languages. However, C++ supports many programming styles, some of which violate the principles of sound design.

Programs that use C++ language features such as pointers, cast operations, and sizeof(object) are difficult to refactor. Pointers and cast operations introduce aliasing, which makes it difficult to determine all references to an object that you might want to refactor. Each of these features exposes the internal representation of an object, which violates principles of abstraction.

For example, C++ uses a V-table mechanism for representing member variables in the executable program. The set of inherited member variables appears first followed by the locally defined member variables. One generally safe refactoring is to move a variable to a superclass. Because the variable now is inherited rather than locally defined in the subclass, the physical location of the variable in the executable is likely to have changed as a result of refactoring. If all variable references in the program are through the class interface, such a reordering of physical locations of the variable will not change the program's behavior.

On the other hand, if the variable was referenced through pointer arithmetic (for example, a programmer had a pointer to an object, used to know that the variable was in the fifth byte, and assigned a value to the fifth byte of the object using pointer arithmetic), then moving the variable to the superclass will likely change the program's behavior. Similarly, if a programmer wrote a conditional of the form if (sizeof(object)==15)), and refactored the program to remove an unreferenced variable from a class, the size of instances of that class would change, and a conditional that once tested true would test false.

It might seem absurd for someone to write programs that do conditional tests based on the size of objects or to use pointer arithmetic when C++ provides a much cleaner interface to class variables. My point is that these features (and others that depend on the physical layout of an object) are provided in C++, and there are programmers experienced in using them. Migrating from C to C++ does not an object-oriented programmer or designer make.

Because C++ is such a complicated language (compared with Smalltalk and, to a lesser extent, Java), it is much more difficult to create the kinds of representations of program structure that are useful for automating support for checking whether a refactoring is safe and, if it is, for performing the refactoring.

Because C++ resolves most references at compile time, refactoring a program usually requires recompiling at least part of a program and linking the executable before testing of the effects of a change. By contrast, Smalltalk and CLOS (Common Lisp Object System) provide environments for interpretation and incremental compilation. Whereas applying (and possibly backing out) a series of incremental refactorings is fairly natural for Smalltalk and CLOS, the cost per iteration (in terms of recompilation and retesting) is higher for C++ programs; thus programmers tend to be less willing to make these small changes.

Many applications use a database. Changes to the structure of objects in a C++ program may require that corresponding schematic changes be made to the database. (Many of the ideas I applied in my refactoring work came from research into object-oriented database schema

evolution.)

Another limitation, which may interest software researchers more than many software practitioners, is that C++ does not provide support for metalevel program analysis and change. There is nothing analogous to the metaobject protocol available for CLOS. The metaobject protocol of CLOS, for example, supports a sometimes useful refactoring for changing selected instances of a class into instances of a different class while having all references to the old objects automatically point to the new objects. Fortunately, the cases in which I wanted or needed these features were few and far between.

### Closing Comments

Refactoring techniques can and have been applied to C++ programs in a variety of contexts. C++ programs often are expected to be evolved over several years. It is during that process of evolving software that the benefits of refactoring can most easily be seen. The language provides some features that simplify refactoring, whereas other language features if applied make refactoring more difficult. Fortunately, it is widely recognized that using language features such as pointer arithmetic is a bad idea, so most good object-oriented programmers avoid using them.

Many thanks to Ralph Johnson, Mick Murphy, James Roskind, and others for introducing me to some of the power and complexity of C++ with respect to refactoring.

### Refactoring to Achieve Near-term Benefits

It is relatively easy to describe the mid-to-long range benefits of refactoring. Many organizations, however, are increasingly judged by the investment community and by others on near-term performance. Can refactoring make a difference in the near term?

Refactoring has been applied successfully for more than ten years by experienced objectoriented developers. Many of these programmers cut their teeth in a Smalltalk culture that valued clarity and simplicity of code and embraced reuse. In such a culture, programmers would invest time to refactor because it was the right thing to do. The Smalltalk language and its implementations made refactoring possible in ways that hadn't been true for most prior languages and software development environments. Much of the early Smalltalk programming was done in research groups such as Xerox, PARC, or small programming teams at leading-edge companies and consulting firms. The values of these groups were somewhat different from the values of many industrial software groups. Martin and I are both aware that for refactoring to be embraced by the mainstream software development community, at least some of its benefits must be near term.

Our research team [3], [9], [12], [13], [14], [15] has described several examples of how refactorings can be interleaved with extensions to a program in a way that achieves both nearterm and long-term benefits. One of our examples is the Choices file system framework. Initially the framework implemented the BSD (Berkeley Software Distribution) Unix file system format.

Later it was extended to support UNIX System V, MS-DOS, persistent, and distributed file systems. System V file systems bear many similarities to BSD UNIX file systems. The approach taken by the framework developer was first to clone parts of BSD Unix implementation then modify the clone to support System V. The resultant implementation worked, but there was lots of duplicate code. After adding the new code, the framework developer refactored the code, creating abstract superclasses to contain the behavior common to the two Unix file system implementations. Common variables and functions were moved to superclasses. In cases in which corresponding functions were nearly but not entirely identical for the two file system implementations, new functions were defined in each subclass to contain the differences. In the original functions those code segments were replaced with calls to the new functions. Code was incrementally made more similar in the two subclasses. When the functions were identical, they were moved to a common superclass.

These refactorings provide several near-term and mid-term benefits. In the near term, errors found in the common code base during testing needed to be modified only *in one place.* The overall code size was smaller. The behavior specific to a particular file system format was cleanly separated from the code common to the two file system formats. This made it easier to track down and fix behaviors specific to that file system format. In the mid term, the abstractions that resulted from refactoring often were useful in defining subsequent file systems. Granted, the behavior common to the two existing file system formats might not be entirely common for a third format, but the existing base of common code was a valuable starting point. Subsequent refactorings could be applied to clarify what was really common. The framework development team found that over time it took less effort to incrementally add support for a new file system format. Even though the newer formats were more complex, development was done by less experienced staff.

I could cite other examples of near-term and long-term benefit from refactoring, but Martin has already done this. Rather than add to his list, let me draw an analogy to something that is near and dear to many of us, our physical health.

In many ways, refactoring is like exercise and eating a proper diet. Many of us know that we ought to exercise more and eat a more balanced diet. Some of us live in cultures that highly encourage these habits. Some of us can get by for a while without practicing these good habits, even without visible effects. We can always make excuses, but we are only fooling ourselves if we continue to ignore good behavior.

Some of us are motivated by the near-term benefits of exercise and eating a proper diet, such as high energy levels, greater flexibility, higher self-esteem, and other benefits. Nearly all of us know that these near-term benefits are *very* real. Many but not all of us make at least sporadic efforts in these areas. Others, however, aren't sufficiently motivated to do something until they reach a crisis point.

Yes, there are cautions that need to be applied; people should consult with an expert before embarking on a program. In the case of exercise and dieting, they should consult with their physician. In the case of refactoring, they should seek resources such as this book and the papers cited elsewhere in this chapter. Staff experienced in refactoring can provide more focused assistance.

Several people I've met are role models with respect to fitness and refactoring. I admire their energy and their productivity. Negative models show the visible signs of neglect. Their future and the future of the software systems they produce may not be rosy.

Refactoring can achieve near-term benefits and make the software easier to modify and maintain. Refactoring is a means rather than an end. It is part of a broader context of how programmers or programming teams develop and maintain their software.[3]

### Reducing the Overhead of Refactoring

"Refactoring is an overhead activity. I'm paid to write new, revenue-generating features." My response, in summary, is this:

- · Tools and technologies are available to allow refactoring to be done quickly and relatively painlessly.
- · Experiences reported by some object-oriented programmers suggest that the overhead of refactoring is more than compensated by reduced efforts and intervals in other phases of program development.
- · Although refactoring may seem a bit awkward and an overhead item at first, as it becomes part of a software development regimen, it stops feeling like overhead and starts feeling like an essential.

Perhaps the most mature tool for automated refactoring has been developed for Smalltalk by the Software Refactory team at the University of Illinois (see Chapter 14). It is freely available at their Web site (http://st-www.cs.vivc.edu). Although refactoring tools for other languages are not so readily available, many of the techniques described in our papers and in this book can be applied in a relatively straightforward manner with a text editor or, better yet, a browser. Software development environments and browsers have progressed substantially in recent years. We hope to see a growing set of refactoring tools available in the future.

Kent Beck and Ward Cunningham, both experienced Smalltalk programmers, have reported at OOPSLA conferences and other forums that refactoring has enabled them to develop software rapidly in domains such as bond trading. I have heard similar testimonials from C++ and CLOS developers. In this book, Martin describes the benefits of refactoring with respect to Java programs. We expect to hear more testimonials from those who read this book and apply these principles.

My experience suggests that as refactoring becomes part of a routine, it stops feeling like overhead. This statement is easy to make but difficult to substantiate. To the skeptics among you, my advice is just do it, then decide for yourself. Give it time, though.

## Refactoring Safely

Safety is a concern, especially for organizations developing and evolving large systems. In many applications, there are compelling financial, legal, and ethical considerations for providing continuous, reliable, and error-free service. Many organizations provide extensive training and attempt to apply disciplined development processes to help ensure the safety of their products.

For many programmers, though, safety often seems to be less of a concern. It's more than a little ironic that many of us preach safety first to our children, nieces, and nephews but in our roles as programmers scream for freedom, a hybrid of the Wild West gunslinger and teenage driver. Give us freedom, give us the resources, and watch us fly. After all, do we really want our organization to miss out on the fruits of our creativity merely for the sake of repeatability and conformity?

In this section, I discuss approaches to safe refactoring. I focus on an approach that compared with what Martin describes earlier in this book is somewhat more structured and rigorous but that can eliminate many errors that might be introduced in refactoring.

Safety is a difficult concept to define. An intuitive definition is that a safe refactoring is one that doesn't break a program. Because a refactoring is intended to restructure a program without changing its behavior, a program should perform the same way after a refactoring as it does before.

How does one safely refactor? There are several options:

- · Trust your coding abilities.
- · Trust that your compiler will catch errors that you miss.
- · Trust that your test suite will catch errors that you and your compiler miss.
- · Trust that code review will catch errors that you, your compiler, and your test suite miss.

Martin focuses on the first three options in his refactoring. Mid-to-large-size organizations often supplement these steps with code reviews.

Whereas compilers, test suites, code reviews, and disciplined coding styles all are valuable, there are limits to all of these approaches, as follows:

- · Programmers are fallible, even you (I know I am).
- · There are subtle and not-so-subtle errors that compilers can't catch, especially scoping errors related to inheritance.[1]
- · Perry and Kaiser[16] and others have shown that although it is or at least used to be common wisdom that the testing task is simplified when inheritance is used as an implementation technique, in reality an extensive set of tests often is needed to cover all the cases in which operations that used to be requested on an instance of class are now requested on instances of its subclasses. Unless your test designer is omniscient or pays great attention to detail, there are likely to be cases your test suite won't cover. Testing all possible execution paths in a program is a computationally undecidable problem. In other words, you can't be guaranteed to have caught all of the cases with your test suite.
- · Code reviewers, like programmers, are fallible. Furthermore, reviewers may be too busy with their main job to thoroughly review someone else's code.

Another approach, which I took in my research, is to define and prototype a refactoring tool to check whether a refactoring can be safely applied to a program and, if it is, refactor the program. This avoids many of the bugs that may be introduced through human error.

Herein I provide a high-level description of my approach to safe refactoring. This may be the most valuable part of this chapter. For more details, see my dissertation [1] and other references at the end of this chapter; also see Chapter 14. If you find this section to be overly technical, skim ahead to the last several paragraphs of this section.

Part of my refactoring tool is a program analyzer, which is a program that analyzes the structure of another program (in this case, a C++ program to which a refactoring might be applied). The tool can answer a series of questions regarding scoping, typing, and program semantics (the meaning or intended operations of a program). Scoping issues related to inheritance make this analysis more complex than with many non-object-oriented programs, but for C++, language features such as static typing make the analysis easier than for, say, Smalltalk.

Consider, for example, the refactoring to delete a variable from a program. A tool can determine what other parts of a program (if any) reference the variable. If there are any references, removing the variable would leave dangling references; thus this refactoring would not be safe. A user who asks the tool to refactor the program would receive an error flag. The user might then decide that the refactoring is a bad idea after all or to change the parts of the program that refer

to that variable and apply the refactoring to remove the variable. There are many other checks, most as simple as this, some more complex.

In my research, I defined safety in terms of program properties (related to activities such as scoping and typing) that need to continue to hold after refactoring. Many of these program properties are similar to integrity constraints that must be maintained when database schemas change.[17] Each refactoring has associated with it a set of necessary preconditions that if true would ensure that the program properties are preserved. Only if the tool were to determine that everything is safe would the tool perform the refactoring.

Fortunately, determining whether a refactoring is safe often is trivial, especially for the low-level refactorings that constitute most of our refactoring. To ensure that the higher-level, more complicated refactorings are safe, we defined them in terms of the low-level refactorings. For example, the refactoring to create an abstract superclass is defined in terms of steps, which are simpler refactorings such as creating and moving variables and methods. By showing that each step of a more complicated refactoring is safe, we can know by construction that the refactoring is safe.

There are some (relatively rare) cases in which a refactoring might actually be safe to apply to a program but a tool can't be sure. In these cases the tool takes the safe route and disallows the refactoring. For instance, consider again the case in which you want to remove a variable from a program, but there is a reference to it somewhere else in the program. Perhaps the reference is contained in a code segment that will never be executed. For example, the reference may appear inside a conditional, such as an if-then loop, that will never test true. If you can be sure that the conditional would never test true, you could remove the conditional test, including the code referring to the variable or function that you want to delete. You then could safely remove the variable or function. In general it isn't possible to know for certain whether the condition will always be false. (Suppose you inherited code that was developed by someone else. How confident would you be in deleting this code?)

A refactoring tool can flag the reference and alert the user. The user might decide to leave the code alone. If or when the user became sure that the referencing code would never be executed, he or she could remove the code and apply the refactoring. The tool makes the user aware of the implications of the reference rather than blindly applying the change.

This may sound like complicated stuff. It is fine for a doctoral dissertation (the primary audience, the thesis committee, wants to see some attention to theoretical issues), but is it practical for real refactoring?

All of the safety checking can be implemented under the hood of a refactoring tool. A programmer who wants to refactor a program merely needs to ask the tool to check the code and, if it is safe, perform the refactoring. My tool was a research prototype. Don Roberts, John Brant, Ralph Johnson, and I[10] have implemented a far more robust and featured tool (see Chapter 14) as part of our research into refactoring Smalltalk programs.

Many levels of safety can be applied to refactoring. Some are easy to apply but don't guarantee a high level of safety. Using a refactoring tool can provide many benefits. It can make many simple but tedious checks and flag in advance problems that if left unchecked would cause the program to break as a result of refactoring.

Although applying a refactoring tool avoids introducing many of the errors that you otherwise hope will be flagged during compilation, testing, and code review, the latter techniques are still of value, particularly in the development or evolution of real-time systems. Programs often don't execute in isolation; they are parts of a larger network of communicating systems. Some

refactorings not only clean up code but also make a program run more quickly. Speeding up one program might result in performance bottlenecks elsewhere. This is similar to the effects of upgrading microprocessors that speed up parts of a system and require similar approaches to tune and test overall system performance. Conversely, some refactorings may slow overall performance a bit, but in general such effects on performance are minimal.

Safety approaches are intended to guarantee that refactoring does not introduce *new* errors into a program. These approaches don't detect or fix bugs that were in the program before it was refactored. However, refactoring may make it easier to spot such bugs and correct them.

## A Reality Check (Revisited)

Making refactoring real requires addressing the real-world concerns of software professionals. Four commonly expressed concerns are as follows:

- · The programmers might not understand how to refactor.
- · If the benefits are long-term, why exert the effort now? In the long term, you might not be with the project to reap the benefits.
- · Refactoring code is an overhead activity; programmers are paid to write *new* features.
- · Refactoring might break the existing program.

In this chapter, I briefly address each of these concerns and provide pointers for those who want to delve further into these topics.

The following issues are of concern to some projects:

- · What if the code to be refactored is collectively owned by several programmers? In some cases, many of the traditional change management mechanisms are relevant. In other cases, if the software has been well designed and refactored, subsystems will be sufficiently decoupled that many refactorings will affect only a small subset of the code base.
- · What if there are multiple versions or lines of code from a code base? In some cases, refactoring may be relevant for all of the versions, in which case all need to be checked for safety before the refactoring is applied. In other cases, the refactorings may be relevant for only some versions, which simplifies the process of checking and refactoring the code. Managing changes to multiple versions often requires applying many of the traditional version-management techniques. Refactoring can be useful in merging variants or versions into an updated code base, which may simplify version management downstream.

In summary, persuading software professionals of the practical value of refactoring is quite different from persuading a doctoral committee that refactoring research is worthy of a Ph.D. It took me some time after completing my graduate studies to fully appreciate these differences.

## Resources and References for Refactoring

By this point in the book, I hope you are planning to apply refactoring techniques in your work and are encouraging others in your organization to do so. If you are still undecided, you may want to refer to the references I have provided or contact Martin (Fowler@acm.org), me, or others who are experienced in refactoring.

If you want to explore refactoring further, here are a few references that you may want to check out. As Martin has noted, this book isn't the first written work on refactoring, but (I hope) it will expose a broadening audience to the concepts and benefits of refactoring. Although my doctoral dissertation was the first major written work on the topic, most readers interested in exploring the early foundational work on refactoring probably should look first at several papers.[3], [9], [12], [13] Refactoring was a tutorial topic at OOPSLA 95 and OOPSLA 96. [14], [15] For those with an interest in both design patterns and refactoring, the paper "Lifecycle and Refactoring Patterns That Support Evolution and Reuse," [3] which Brian Foote and I presented at PLoP '94 and which appears in the first volume of the Addison-Wesley Pattern Languages of Program Design series, is a good place to start. My refactoring research was largely built on work by Ralph Johnson and Brian regarding object-oriented application frameworks and the design of reusable classes. [4] Subsequent refactoring research by John Brant, Don Roberts, and Ralph Johnson at the University of Illinois has focused on refactoring Smalltalk programs. [10], [11] Their Web site (http://st-www.cs.uiuc.edu) includes some of their most recent work. Interest in refactoring has grown within the object-oriented research community. Several related papers were presented at OOPSLA 96 in a session titled Refactoring and Reuse[18].

## Implications Regarding Software Reuse and Technology Transfer

The real-world concerns addressed earlier don't apply to refactoring alone. They apply more broadly to software evolution and reuse.

For much of the past several years, I have focused on issues related to software reuse, platforms, frameworks, patterns, and the evolution of legacy systems, often involving software that was not object oriented. In addition to working with projects within Lucent and Bell Labs, I have participated in forums with staff at other organizations who have been grappling with similar issues.[19], [20], [21], [22]

The real-world concerns regarding a reuse program are similar to those related to refactoring.

- · Technical staff may not understand what to reuse or how to reuse it.
- · Technical staff may not be motivated to apply a reuse approach unless short-term benefits can be achieved.
- · Overhead, learning curve, and discovery cost issues must be addressed for a reuse approach to be successfully adopted.
- · Adopting a reuse approach should not be disruptive to a project; there may be strong pressures to leverage existing assets or implementation albeit with legacy constraints. New implementations should interwork or be backward compatible with existing systems.

Geoffrey Moore[23] described the technology adoption process in terms of a bell-shaped curve in which the front tail includes innovators and early adopters, the large middle hump includes early majority and late majority, and the trailing tail includes laggards. For an idea and product to succeed, they must ultimately be adopted by the early and late majorities. Put another way, many ideas that appeal to the innovators and early adopters ultimately fail because they never make it across the chasm to the early and late majorities. The disconnect lies mainly in the differing motivators of these customer groups. Innovators and early adopters are attracted by new technologies, visions of paradigm shifts and breakthroughs. The early and late majorities are concerned primarily with maturity, cost, support, and seeing whether the new idea or product has been successfully applied by others with needs similar to theirs.

Software development professionals are impressed and convinced in very different ways than are software researchers. Software researchers are most often what Moore refers to as innovators. Software developers and especially software managers often are part of the early and late

majorities. Recognizing these differences is important in reaching each of these groups. With software reuse, as with refactoring, it is important to reach software development professionals on their terms.

Within Lucent/Bell Labs I found that encouraging application of reuse and platforms required reaching a variety of stakeholders. It required formulating strategy with executives, organizing leadership team meetings among middle managers, consulting with development projects, and publicizing the benefits of these technologies to broad research and development audiences through seminars and publications. Throughout it was important to train staff in the principles, address near-term benefits, provide ways to reduce overhead, and address how these techniques could be introduced safely. I had gained these insights from my refactoring research.

As Ralph Johnson, who was my thesis advisor, pointed out when reviewing a draft of this chapter, these principles don't apply only to refactoring and to software reuse; they are generic issues of technology transfer. If you find yourself trying to persuade other people to refactor (or to adopt another technology or practice), make sure that you focus on these issues and reach people where they are. Technology transfer is difficult, but it can be done.

### A Final Note

Thanks for taking the time to read this chapter. I've tried to address many of the concerns that you might have about refactoring and tried to show that many of the real-world concerns regarding refactoring apply more broadly to software evolution and reuse. I hope that you came away enthusiastic about applying these ideas in your work. Best wishes as you move forward in your software development tasks.
