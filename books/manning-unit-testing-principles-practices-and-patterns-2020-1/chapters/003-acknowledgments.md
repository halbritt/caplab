# acknowledgments

<span id="page-16-0"></span>This book was a lot of work. Even though I was prepared mentally, it was still much more work than I could ever have imagined.

 A big "thank you" to Sam Zaydel, Alessandro Campeis, Frances Buran, Tiffany Taylor, and especially Marina Michaels, whose invaluable feedback helped shape the book and made me a better writer along the way. Thanks also to everyone else at Manning who worked on this book in production and behind the scenes.

 I'd also like to thank the reviewers who took the time to read my manuscript at various stages during its development and who provided valuable feedback: Aaron Barton, Alessandro Campeis, Conor Redmond, Dror Helper, Greg Wright, Hemant Koneru, Jeremy Lange, Jorge Ezequiel Bo, Jort Rodenburg, Mark Nenadov, Marko Umek, Markus Matzker, Srihari Sridharan, Stephen John Warnett, Sumant Tambe, Tim van Deurzen, and Vladimir Kuptsov.

 Above all, I would like to thank my wife Nina, who supported me during the whole process.

## about this book

<span id="page-17-0"></span>*Unit Testing: Principles, Practices, and Patterns* provides insights into the best practices and common anti-patterns that surround the topic of unit testing. After reading this book, armed with your newfound skills, you'll have the knowledge needed to become an expert at delivering successful projects that are easy to maintain and extend, thanks to the tests you build along the way.

## Who should read this book

Most online and print resources have one drawback: they focus on the basics of unit testing but don't go much beyond that. There's a lot of value in such resources, but the learning doesn't end there. There's a next level: not just writing tests, but doing it in a way that gives you the best return on your efforts. When you reach this point on the learning curve, you're pretty much left to your own devices to figure out how to get to the next level.

 This book takes you to that next level. It teaches a scientific, precise definition of the ideal unit test. That definition provides a universal frame of reference, which will help you look at many of your tests in a new light and see which of them contribute to the project and which must be refactored or removed.

 If you don't have much experience with unit testing, you'll learn a lot from this book. If you're an experienced programmer, you most likely already understand some of the ideas taught in this book. The book will help you articulate why the techniques and best practices you've been using all along are so helpful. And don't underestimate this skill: the ability to clearly communicate your ideas to colleagues is priceless.

## How this book is organized: A roadmap

The book's 11 chapters are divided into 4 parts. Part 1 introduces unit testing and gives a refresher on some of the more generic unit testing principles:

- Chapter 1 defines the goal of unit testing and gives an overview of how to differentiate a good test from a bad one.
- Chapter 2 explores the definition of *unit test* and discusses the two schools of unit testing.
- Chapter 3 provides a refresher on some basic topics, such as structuring of unit tests, reusing test fixtures, and test parameterization.

Part 2 gets to the heart of the subject—it shows what makes a good unit test and provides details about how to refactor your tests toward being more valuable:

- Chapter 4 defines the four pillars that form a good unit test and provide a common frame of reference that is used throughout the book.
- Chapter 5 builds a case for mocks and explores their relation to test fragility.
- Chapter 6 examines the three styles of unit testing, along with which of those styles produces tests of the best quality and why.
- Chapter 7 teaches you how to refactor away from bloated, overcomplicated tests and achieve tests that provide maximum value with minimum maintenance costs.

Part 3 explores the topic of integration testing:

- Chapter 8 looks at integration testing in general along with its benefits and trade-offs.
- Chapter 9 discusses mocks and how to use them in a way that benefits your tests the most.
- Chapter 10 explores working with relational databases in tests.

Part 4's chapter 11 covers common unit testing anti-patterns, some of which you've possibly encountered before.

## About the Code

The code samples are written in C#, but the topics they illustrate are applicable to any object-oriented language, such as Java or C++. C# is just the language that I happen to work with the most.

 I tried not to use any C#-specific language features, and I made the sample code as simple as possible, so you shouldn't have any trouble understanding it. You can download all of the code samples online at [www.manning.com/books/unit-testing.](http://www.manning.com/books/unit-testing)

## liveBook discussion forum

Purchase of *Unit Testing: Principles, Practices, and Patterns* includes free access to a private web forum run by Manning Publications where you can make comments about the book, ask technical questions, and receive help from the author and from other users. To access the forum, go to [https://livebook.manning.com/#!/book/unit-testing/](https://livebook.manning.com/#!/book/unit-testing/discussion) [discussion.](https://livebook.manning.com/#!/book/unit-testing/discussion) You can also learn more about Manning's forums and the rules of conduct at [https://livebook.manning.com/#!/discussion.](https://livebook.manning.com/#!/discussion)

 Manning's commitment to our readers is to provide a venue where a meaningful dialogue between individual readers and between readers and the author can take place. It is not a commitment to any specific amount of participation on the part of the author, whose contribution to the forum remains voluntary (and unpaid). We suggest you try asking the author some challenging questions lest his interest stray! The forum and the archives of previous discussions will be accessible from the publisher's website as long as the book is in print.

### Other online resources

- My blog is at [EnterpriseCraftsmanship.com.](http://EnterpriseCraftsmanship.com)
- I also have an online course about unit testing (in the works, as of this writing), which you can enroll in at [UnitTestingCourse.com](http://UnitTestingCourse.com).
