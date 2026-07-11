<span id="page-26-0"></span>
# Acknowledgments

A book is never really written by one person (at least none of my books are). A second edition is even more a collective undertaking.

I'd like to thank the people who contributed review comments on significant portions of the book: Hákon Ágústsson, Scott Ambler, Will Barns, William D. Bartholomew, Lars Bergstrom, Ian Brockbank, Bruce Butler, Jay Cincotta, Alan Cooper, Bob Corrick, Al Corwin, Jerry Deville, Jon Eaves, Edward Estrada, Steve Gouldstone, Owain Griffiths, Matthew Harris, Michael Howard, Andy Hunt, Kevin Hutchison, Rob Jasper, Stephen Jenkins, Ralph Johnson and his Software Architecture Group at the University of Illinois, Marek Konopka, Jeff Langr, Andy Lester, Mitica Manu, Steve Mattingly, Gareth McCaughan, Robert McGovern, Scott Meyers, Gareth Morgan, Matt Peloquin, Bryan Pflug, Jeffrey Richter, Steve Rinn, Doug Rosenberg, Brian St. Pierre, Diomidis Spinellis, Matt Stephens, Dave Thomas, Andy Thomas-Cramer, John Vlissides, Pavel Vozenilek, Denny Williford, Jack Woolley, and Dee Zsombor.

Hundreds of readers sent comments about the first edition, and many more sent individual comments about the second edition. Thanks to everyone who took time to share their reactions to the book in its various forms.

Special thanks to the Construx Software reviewers who formally inspected the entire manuscript: Jason Hills, Bradey Honsinger, Abdul Nizar, Tom Reed, and Pamela Perrott. I was truly amazed at how thorough their review was, especially considering how many eyes had scrutinized the book before they began working on it. Thanks also to Bradey, Jason, and Pamela for their contributions to the *cc2e.com* website.

Working with Devon Musgrave, project editor for this book, has been a special treat. I've worked with numerous excellent editors on other projects, and Devon stands out as especially conscientious and easy to work with. Thanks, Devon! Thanks to Linda Engleman who championed the second edition; this book wouldn't have happened without her. Thanks also to the rest of the Microsoft Press staff, including Robin Van Steenburgh, Elden Nelson, Carl Diltz, Joel Panchot, Patricia Masserman, Bill Myers, Sandi Resnick, Barbara Norfleet, James Kramer, and Prescott Klassen.

I'd like to remember the Microsoft Press staff that published the first edition: Alice Smith, Arlene Myers, Barbara Runyan, Carol Luke, Connie Little, Dean Holmes, Eric Stroo, Erin O'Connor, Jeannie McGivern, Jeff Carey, Jennifer Harris, Jennifer Vick, Judith Bloch, Katherine Erickson, Kim Eggleston, Lisa Sandburg, Lisa Theobald, Margarite Hargrave, Mike Halvorson, Pat Forgette, Peggy Herman, Ruth Pettis, Sally Brunsman, Shawn Peck, Steve Murray, Wallis Bolz, and Zaafar Hasnain.

## **xxviii** Acknowledgments

Thanks to the reviewers who contributed so significantly to the first edition: Al Corwin, Bill Kiestler, Brian Daugherty, Dave Moore, Greg Hitchcock, Hank Meuret, Jack Woolley, Joey Wyrick, Margot Page, Mike Klein, Mike Zevenbergen, Pat Forman, Peter Pathe, Robert L. Glass, Tammy Forman, Tony Pisculli, and Wayne Beardsley. Special thanks to Tony Garland for his exhaustive review: with 12 years' hindsight, I appreciate more than ever how exceptional Tony's several thousand review comments really were.

<span id="page-28-0"></span>
## Checklists

| Requirements<br>42                                |
|---------------------------------------------------|
| Architecture<br>54                                |
| Upstream Prerequisites<br>59                      |
| Major Construction Practices<br>69                |
| Design in Construction<br>122                     |
| Class Quality<br>157                              |
| High-Quality Routines<br>185                      |
| Defensive Programming<br>211                      |
| The Pseudocode Programming Process<br>233         |
| General Considerations In Using Data<br>257       |
| Naming Variables<br>288                           |
| Fundamental Data<br>316                           |
| Considerations in Using Unusual Data Types<br>343 |
| Organizing Straight-Line Code<br>353              |
| Using Conditionals<br>365                         |
| Loops<br>388                                      |
| Unusual Control Structures<br>410                 |
| Table-Driven Methods<br>429                       |
| Control-Structure Issues<br>459                   |
| A Quality-Assurance Plan<br>476                   |
| Effective Pair Programming<br>484                 |
| Effective Inspections<br>491                      |
| Test Cases<br>532                                 |
| Debugging Reminders<br>559                        |
| Reasons to Refactor<br>570                        |
| Summary of Refactorings<br>577                    |
| Refactoring Safely<br>584                         |
| Code-Tuning Strategies<br>607                     |
| Code-Tuning Techniques<br>642                     |

### **xxx** Checklists

Configuration Management 669 Integration 707 Programming Tools 724 Layout 773 Self-Documenting Code 780

Good Commenting Technique 816

<span id="page-30-0"></span>
## Tables

| Table 3-1  | Average Cost of Fixing Defects Based on When They're Introduced and<br>Detected<br>29 |
|------------|---------------------------------------------------------------------------------------|
| Table 3-2  | Typical Good Practices for Three Common Kinds of Software Projects<br>31              |
| Table 3-3  | Effect of Skipping Prerequisites on Sequential and Iterative Projects<br>33           |
| Table 3-4  | Effect of Focusing on Prerequisites on Sequential and Iterative Projects<br>34        |
| Table 4-1  | Ratio of High-Level-Language Statements to Equivalent C Code<br>62                    |
| Table 5-1  | Popular Design Patterns<br>104                                                        |
| Table 5-2  | Design Formality and Level of Detail Needed<br>116                                    |
| Table 6-1  | Variations on Inherited Routines<br>145                                               |
| Table 8-1  | Popular-Language Support for Exceptions<br>198                                        |
| Table 11-1 | Examples of Good and Bad Variable Names<br>261                                        |
| Table 11-2 | Variable Names That Are Too Long, Too Short, or Just Right<br>262                     |
| Table 11-3 | Sample Naming Conventions for C++ and Java<br>277                                     |
| Table 11-4 | Sample Naming Conventions for C<br>278                                                |
| Table 11-5 | Sample Naming Conventions for Visual Basic<br>278                                     |
| Table 11-6 | Sample of UDTs for a Word Processor<br>280                                            |
| Table 11-7 | Semantic Prefixes<br>280                                                              |
| Table 12-1 | Ranges for Different Types of Integers<br>294                                         |
| Table 13-1 | Accessing Global Data Directly and Through Access Routines<br>341                     |
| Table 13-2 | Parallel and Nonparallel Uses of Complex Data<br>342                                  |
| Table 16-1 | The Kinds of Loops<br>368                                                             |
| Table 19-1 | Transformations of Logical Expressions Under DeMorgan's Theorems<br>436               |
| Table 19-2 | Techniques for Counting the Decision Points in a Routine<br>458                       |
| Table 20-1 | Team Ranking on Each Objective<br>469                                                 |
| Table 20-2 | Defect-Detection Rates<br>470                                                         |
| Table 20-3 | Extreme Programming's Estimated Defect-Detection Rate<br>472                          |
| Table 21-1 | Comparison of Collaborative Construction Techniques<br>495                            |
| Table 23-1 | Examples of Psychological Distance Between Variable Names<br>556                      |
| Table 25-1 | Relative Execution Time of Programming Languages<br>600                               |
| Table 25-2 | Costs of Common Operations<br>601                                                     |

### **xxxii** Tables

| Table 27-1 | Project Size and Typical Error Density<br>652         |
|------------|-------------------------------------------------------|
| Table 27-2 | Project Size and Productivity<br>653                  |
| Table 28-1 | Factors That Influence Software-Project Effort<br>674 |
| Table 28-2 | Useful Software-Development Measurements<br>678       |
| Table 28-3 | One View of How Programmers Spend Their Time<br>681   |

<span id="page-32-0"></span>
## Figures

| Figure 1-1 | Construction activities are shown inside the gray circle. Construction<br>focuses on coding and debugging but also includes detailed design, unit<br>testing, integration testing, and other activities.<br>4                                                                                                                       |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Figure 1-2 | This book focuses on coding and debugging, detailed design, construction<br>planning, unit testing, integration, integration testing, and other activities in<br>roughly these proportions.<br>5                                                                                                                                    |
| Figure 2-1 | The letter-writing metaphor suggests that the software process relies on<br>expensive trial and error rather than careful planning and design.<br>14                                                                                                                                                                                |
| Figure 2-2 | It's hard to extend the farming metaphor to software development<br>appropriately.<br>15                                                                                                                                                                                                                                            |
| Figure 2-3 | The penalty for a mistake on a simple structure is only a little time and<br>maybe some embarrassment.<br>17                                                                                                                                                                                                                        |
| Figure 2-4 | More complicated structures require more careful planning.<br>18                                                                                                                                                                                                                                                                    |
| Figure 3-1 | The cost to fix a defect rises dramatically as the time from when it's intro<br>duced to when it's detected increases. This remains true whether the<br>project is highly sequential (doing 100 percent of requirements and design<br>up front) or highly iterative (doing 5 percent of requirements and design<br>up front).<br>30 |
| Figure 3-2 | Activities will overlap to some degree on most projects, even those that are<br>highly sequential.<br>35                                                                                                                                                                                                                            |
| Figure 3-3 | On other projects, activities will overlap for the duration of the project. One<br>key to successful construction is understanding the degree to which prereq<br>uisites have been completed and adjusting your approach accordingly.<br>35                                                                                         |
| Figure 3-4 | The problem definition lays the foundation for the rest of the programming<br>process.<br>37                                                                                                                                                                                                                                        |
| Figure 3-5 | Be sure you know what you're aiming at before you shoot.<br>38                                                                                                                                                                                                                                                                      |
| Figure 3-6 | Without good requirements, you can have the right general problem but<br>miss the mark on specific aspects of the problem.<br>39                                                                                                                                                                                                    |
| Figure 3-7 | Without good software architecture, you may have the right problem but the<br>wrong solution. It may be impossible to have successful construction.<br>44                                                                                                                                                                           |
| Figure 5-1 | The Tacoma Narrows bridge—an example of a wicked problem.<br>75                                                                                                                                                                                                                                                                     |
|            |                                                                                                                                                                                                                                                                                                                                     |

### **xxxiv** Figures

| The levels of design in a program. The system (1) is first organized into sub<br>systems (2). The subsystems are further divided into classes (3), and the<br>classes are divided into routines and data (4). The inside of each routine is<br>also designed (5).<br>82                                          |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| An example of a system with six subsystems.<br>83                                                                                                                                                                                                                                                                |
| An example of what happens with no restrictions on intersubsystem<br>communications.<br>83                                                                                                                                                                                                                       |
| With a few communication rules, you can simplify subsystem interactions<br>significantly.<br>84                                                                                                                                                                                                                  |
| This billing system is composed of four major objects. The objects have been<br>simplified for this example.<br>88                                                                                                                                                                                               |
| Abstraction allows you to take a simpler view of a complex concept.<br>90                                                                                                                                                                                                                                        |
| Encapsulation says that, not only are you allowed to take a simpler view of a<br>complex concept, you are not allowed to look at any of the details of the<br>complex concept. What you see is what you get—it's all you get!<br>91                                                                              |
| A good class interface is like the tip of an iceberg, leaving most of the class<br>unexposed.<br>93                                                                                                                                                                                                              |
| G. Polya developed an approach to problem solving in mathematics that's<br>also useful in solving problems in software design (Polya 1957).<br>109                                                                                                                                                               |
| Part of the Interstate-90 floating bridge in Seattle sank during a storm<br>because the flotation tanks were left uncovered, they filled with water, and<br>the bridge became too heavy to float. During construction, protecting your<br>self against the small stuff matters more than you might think.<br>189 |
| Defining some parts of the software that work with dirty data and some that<br>work with clean data can be an effective way to relieve the majority of the<br>code of the responsibility for checking for bad data.<br>204                                                                                       |
| Details of class construction vary, but the activities generally occur in the<br>order shown here.<br>216                                                                                                                                                                                                        |
| These are the major activities that go into constructing a routine. They're<br>usually performed in the order shown.<br>217                                                                                                                                                                                      |
| You'll perform all of these steps as you design a routine but not necessarily<br>in any particular order.<br>225                                                                                                                                                                                                 |
| "Long live time" means that a variable is live over the course of many state<br>ments. "Short live time" means it's live for only a few statements. "Span"<br>refers to how close together the references to a variable are.<br>246                                                                              |
|                                                                                                                                                                                                                                                                                                                  |
| Sequential data is data that's handled in a defined order.<br>254                                                                                                                                                                                                                                                |
|                                                                                                                                                                                                                                                                                                                  |

| Figure 10-4 | Iterative data is repeated.<br>255                                                                                                                                                                                                                    |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Figure 13-1 | The amount of memory used by each data type is shown by double<br>lines.<br>324                                                                                                                                                                       |
| Figure 13-2 | An example of a picture that helps us think through the steps involved in<br>relinking pointers.<br>329                                                                                                                                               |
| Figure 14-1 | If the code is well organized into groups, boxes drawn around related sec<br>tions don't overlap. They might be nested.<br>352                                                                                                                        |
| Figure 14-2 | If the code is organized poorly, boxes drawn around related sections<br>overlap.<br>353                                                                                                                                                               |
| Figure 17-1 | Recursion can be a valuable tool in the battle against complexity—when used<br>to attack suitable problems.<br>394                                                                                                                                    |
| Figure 18-1 | As the name suggests, a direct-access table allows you to access the table ele<br>ment you're interested in directly.<br>413                                                                                                                          |
| Figure 18-2 | Messages are stored in no particular order, and each one is identified with a<br>message ID.<br>417                                                                                                                                                   |
| Figure 18-3 | Aside from the Message ID, each kind of message has its own format.<br>418                                                                                                                                                                            |
| Figure 18-4 | Rather than being accessed directly, an indexed access table is accessed via<br>an intermediate index.<br>425                                                                                                                                         |
| Figure 18-5 | The stair-step approach categorizes each entry by determining the level at<br>which it hits a "staircase." The "step" it hits determines its category.<br>426                                                                                         |
| Figure 19-1 | Examples of using number-line ordering for boolean tests.<br>440                                                                                                                                                                                      |
| Figure 20-1 | Focusing on one external characteristic of software quality can affect other<br>characteristics positively, adversely, or not at all.<br>466                                                                                                          |
| Figure 20-2 | Neither the fastest nor the slowest development approach produces the soft<br>ware with the most defects.<br>475                                                                                                                                      |
| Figure 22-1 | As the size of the project increases, developer testing consumes a smaller<br>percentage of the total development time. The effects of program size are<br>described in more detail in Chapter 27, "How Program Size Affects<br>Construction."<br>502 |
| Figure 22-2 | As the size of the project increases, the proportion of errors committed dur<br>ing construction decreases. Nevertheless, construction errors account for<br>45–75% of all errors on even the largest projects.<br>521                                |
| Figure 23-1 | Try to reproduce an error several different ways to determine its exact                                                                                                                                                                               |

**Figure 24-1** Small changes tend to be more error-prone than larger changes (Weinberg

cause. 545

1983). 581

#### **xxxvi** Figures

| Figure 24-2 | Your code doesn't have to be messy just because the real world is messy.<br>Conceive your system as a combination of ideal code, interfaces from the<br>ideal code to the messy real world, and the messy real world.<br>583                                                                                                                                                                                                                                                                                |  |  |  |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| Figure 24-3 | One strategy for improving production code is to refactor poorly written leg<br>acy code as you touch it, so as to move it to the other side of the "interface to<br>the messy real world."<br>584                                                                                                                                                                                                                                                                                                          |  |  |  |
| Figure 27-1 | The number of communication paths increases proportionate to the square<br>of the number of people on the team.<br>650                                                                                                                                                                                                                                                                                                                                                                                      |  |  |  |
| Figure 27-2 | As project size increases, errors usually come more from requirements and<br>design. Sometimes they still come primarily from construction (Boehm<br>1981, Grady 1987, Jones 1998).<br>652                                                                                                                                                                                                                                                                                                                  |  |  |  |
| Figure 27-3 | Construction activities dominate small projects. Larger projects require<br>more architecture, integration work, and system testing to succeed. Require<br>ments work is not shown on this diagram because requirements effort is not<br>as directly a function of program size as other activities are (Albrecht 1979;<br>Glass 1982; Boehm, Gray, and Seewaldt 1984; Boddie 1987; Card 1987;<br>McGarry, Waligora, and McDermott 1989; Brooks 1995; Jones 1998; Jones<br>2000; Boehm et al. 2000).<br>654 |  |  |  |
| Figure 27-4 | The amount of software construction work is a near-linear function of<br>project size. Other kinds of work increase nonlinearly as project size<br>increases.<br>655                                                                                                                                                                                                                                                                                                                                        |  |  |  |
| Figure 28-1 | This chapter covers the software-management topics related to<br>construction.<br>661                                                                                                                                                                                                                                                                                                                                                                                                                       |  |  |  |
| Figure 28-2 | Estimates created early in a project are inherently inaccurate. As the project<br>progresses, estimates can become more accurate. Reestimate periodically<br>throughout a project, and use what you learn during each activity to improve<br>your estimate for the next activity.<br>673                                                                                                                                                                                                                    |  |  |  |
| Figure 29-1 | The football stadium add-on at the University of Washington collapsed<br>because it wasn't strong enough to support itself during construction. It<br>likely would have been strong enough when completed, but it was con<br>structed in the wrong order—an integration error.<br>690                                                                                                                                                                                                                       |  |  |  |
| Figure 29-2 | Phased integration is also called "big bang" integration for a good<br>reason!<br>691                                                                                                                                                                                                                                                                                                                                                                                                                       |  |  |  |
| Figure 29-3 | Incremental integration helps a project build momentum, like a snowball<br>going down a hill.<br>692                                                                                                                                                                                                                                                                                                                                                                                                        |  |  |  |
|             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |  |

| Figure 29-4  | In phased integration, you integrate so many components at once that it's<br>hard to know where the error is. It might be in any of the components or in<br>any of their connections. In incremental integration, the error is usually<br>either in the new component or in the connection between the new compo<br>nent and the system.<br>693 |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Figure 29-5  | In top-down integration, you add classes at the top first, at the bottom<br>last.<br>695                                                                                                                                                                                                                                                        |
| Figure 29-6  | As an alternative to proceeding strictly top to bottom, you can integrate from<br>the top down in vertical slices.<br>696                                                                                                                                                                                                                       |
| Figure 29-7  | In bottom-up integration, you integrate classes at the bottom first, at the top<br>last.<br>697                                                                                                                                                                                                                                                 |
| Figure 29-8  | As an alternative to proceeding purely bottom to top, you can integrate from<br>the bottom up in sections. This blurs the line between bottom-up integration<br>and feature-oriented integration, which is described later in this<br>chapter.<br>698                                                                                           |
| Figure 29-9  | In sandwich integration, you integrate top-level and widely used bottom<br>level classes first and you save middle-level classes for last.<br>698                                                                                                                                                                                               |
| Figure 29-10 | In risk-oriented integration, you integrate classes that you expect to be most<br>troublesome first; you implement easier classes later.<br>699                                                                                                                                                                                                 |
| Figure 29-11 | In feature-oriented integration, you integrate classes in groups that make up<br>identifiable features—usually, but not always, multiple classes at a<br>time.<br>700                                                                                                                                                                           |
| Figure 29-12 | In T-shaped integration, you build and integrate a deep slice of the system to                                                                                                                                                                                                                                                                  |

verify architectural assumptions and then you build and integrate the breadth of the system to provide a framework for developing the remaining

you to spend much of your time focusing on only the upper layers and ignor-

**Figure 34-1** Programs can be divided into levels of abstraction. A good design will allow

functionality. 701

ing the lower layers. 846
