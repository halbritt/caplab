# Preface

<span id="page-10-0"></span>Welcome to the pragmatic software development world, where engineers are not afraid of ambitious performance goals. Where the change in requirements or unex‐ pected efficiency issues is handled without stress, where code is optimized tactically and effectively, based on data, yet the codebase is kept simple and easy to read, main‐ tain, and extend. Wait, is this even possible?

Yes, and I will show you how! The good news is that if you bought this book, you are already halfway there—it means you acknowledge the problem and are open to learn‐ ing more! The bad news is that, while I tried to distill the knowledge to only what's necessary, there are still 11 chapters to go through. I think *Efficient Go* is unique in this regard as it is not a quick tutorial. Instead, it is a complete guide to writing effi‐ cient yet pragmatic software that goes through all aspects I wish I had known when I started my career.

In this book, you will undoubtedly learn a lot about my favorite programming lan‐ guage, Go, and how to optimize it. But don't let the title of this book fool you. While I use Go as the example language to show the optimization mindset and observability patterns, 8 out of 11 chapters of this book are language agnostic. You can use the same techniques to improve software written in any other language like Java, C#, Scala, Python, C++, Rust, or Haskell.

Finally, if you expected a full list of low-level optimization tricks, this is not the right book. Firstly, optimizations do not generalize well. The fact that someone unrolled the loop or used a pointer in their struct field and achieved better efficiency does not mean it will be helpful if we do the same! We will go through some optimization tricks, but I emphasize complete knowledge about efficiency in pragmatic software development instead.

Secondly, "low-level" dangerous tricks are often not needed. In most cases, an aware‐ ness of simple points where your program wastes time and resources is enough to fulfill your efficiency and scalability goals cheaply and effectively. Furthermore, you

will learn that in most cases, there is no need to rewrite your program to C++, Rust, or Assembly to have an efficient solution!

Before we start, let's go through the main goals behind this book and why I found it necessary to focus my time on the subject of efficiency. You will also learn how to get the most out of this book and effectively use it in your software development tasks.

## Why I Wrote This Book

I spent around 1,200 hours writing *Efficient Go*, so the choice to deliver such a book was not spur-of-the-moment. In the era of social media, YouTube, and TikTok, book writing and reading might feel outdated, but in my experience, modern media tend to oversimplify topics. You have to condense those to an absolute minimum not to lose viewers and monetization. It leads to [the wrong incentives,](https://oreil.ly/A8dCv) which generally collide with what I wanted to achieve with this book.

My mission here is straightforward: I want the software I use or depend on to be bet‐ ter! I want software project contributors and maintainers to understand their code's efficiency and how to assess it. I want them to reliably review my or others' pull requests with efficiency improvements. I want people around me to know how to handle performance issues professionally instead of building a stressful atmosphere. I want users and stakeholders to be cautious with the benchmarks and cheap market‐ ing we see in the industry. Finally, I want leaders, directors, and product managers to approach software efficiency topics maturely with the awareness of how to form pragmatic efficiency requirements that help engineers to deliver excellent products.

I also consider this book a small contribution toward more sustainable software. Every wasted CPU time and memory wastes a significant amount of your business's money. However, it also wastes energy and hardware, which has a serious environ‐ mental effect. So saving money and the planet at the same time while enabling better value for your business is not a bad outcome of the skills you will learn here.

I figured out that writing a book is the best way to achieve this goal. It's easier than continuously explaining the same nuances, tooling, and techniques in my daily work, open source, and conferences!

### How I Gathered This Knowledge

I built my experience toward efficiency topics and high-quality software development through a lot of practice, mistakes, experiments, [implicit mentors,](https://oreil.ly/7IFBd) and research.

I was 29 years old when I started writing this book. That might not feel like much experience, but I started a full-time, professional software development career when I was 19. I did full-time computer science studies in parallel to work at Intel around software-defined infrastructure (SDI). I initially coded in Python around the

[OpenStack project,](https://www.openstack.org) then in C++ including contributions to the popular-back-then [Mesos](https://mesos.apache.org) project under the supervision of amazing engineers from [Mesosphere](https://oreil.ly/yUHzn) and Twitter. Finally, I moved to develop Go around [Kubernetes](https://kubernetes.io) and fell in love with this language.

I spent a nontrivial amount of time at Intel on node [oversubscription feature](https://oreil.ly/uPnb7) with noisy neighbor mitigations. Generally, oversubscription allows running more pro‐ grams on a single machine than would be otherwise possible. This can work since statistically, all programs rarely use all of their reserved resources simultaneously. Looking at this now from a later perspective, it is usually easier and more effective to save money by starting with software optimization than by using complex algorithms like this.

In 2016, I moved to London to work for a gaming start-up. I worked with past employees of Google, Amazon, Microsoft, and Facebook to develop and operate a global gaming platform. We were developing microservices, mostly in Go running on dozens of Kubernetes clusters worldwide. This is where I learned a lot about dis‐ tributed systems, site reliability engineering, and monitoring. Perhaps this was when I got addicted to amazing tooling around observability, which is key to achieving pragmatic efficiency and explained in [Chapter 6.](010-chapter-6-efficiency-observability.md#page-212-0)

My passion for good visibility of the running software translated to becoming an expert in using and developing a popular, open source, time-series database for mon‐ itoring purposes called [Prometheus](https://prometheus.io). Eventually, I became an official maintainer and started multiple other Go open source projects and libraries. Finally, I had an oppor‐ tunity to cocreate with Fabian Reinartz a large distributed time-series database in the open source called [Thanos.](https://thanos.io) I would not be surprised if some of my code runs in your company infrastructure!

In 2019, I moved to Red Hat, where I work full-time on observability systems in open source. This is when I also dived more into continuous profiling solutions, which you will learn in this book too.

I am also active in [the Cloud Native Computing Foundation \(CNCF\)](https://cncf.io) as the ambassa‐ dor and [observability Technical Advisory Group \(TAG\)](https://oreil.ly/f9UYG) tech lead. In addition, I coorganize conferences and meetups. Finally, with the Prometheus and Thanos projects, with the team, we mentor multiple engineers every year via the CNCF [men‐](https://oreil.ly/rU0bg) [toring initiatives](https://oreil.ly/rU0bg). 1

<sup>1</sup> If you are new to software development or open source, talk to us, start contributing, and apply for two months paid mentorship. Let me know if you would like to have fun while mentoring others! We need good mentors too—it's important to teach another generation of open source maintainers.

I wrote or reviewed thousands of code lines for various software that had to run on production, be reliable, and scale. I have taught and mentored over two dozen engi‐ neers so far. However, perhaps the most insightful was the open source work. You interact with diverse people, from different companies and places worldwide, with different backgrounds, goals, and needs.

Overall, I believe we achieved amazing things with the fantastic people I had a chance to work with. I was lucky to work in environments where high-quality code was more important than decreasing code review delays or reducing time spent addressing style issues. We thrived on good system design, code maintainability, and readability. We tried to bring those values to open source, and I think we did a good job there. How‐ ever, there is one important thing I would improve if I had a chance to write, for instance, the Thanos project again: I would try to focus more on the pragmatic effi‐ ciency of my code and the algorithms we chose. I would focus on having clearer effi‐ ciency requirements from the start and invest more in benchmarking and profiling.

And don't get me wrong, the Thanos system nowadays is faster and uses much fewer resources than some competitors, but it took a lot of time, and there is still a massive amount of hardware resources we could use less. We still have many bottlenecks that await community attention. However, if I applied the knowledge, techniques, and suggestions that you will learn in this book, I believe we could have cut the develop‐ ment cost in half, if not more, to have Thanos in the state we have today (I hope my ex-boss who paid for this work won't read that!).

My journey showed me how much a book like this was needed. With more people programming overall, often without a computer science background, there are plenty of mistakes and misconceptions, especially regarding software efficiency. Not much literature was available to give us practical answers to our efficiency or scaling ques‐ tions, especially for Go. Hopefully, this book fills that literature gap.

### Who This Book Is For

*Efficient Go* focuses on giving the tools and knowledge necessary to answer when and how to apply efficiency optimization, depending strongly on circumstances and your organization's goals. As a result, the primary audience for this book is software devel‐ opers designing, creating, or changing programs written in Go and any other modern language. It should be a software engineer's job to be an expert on ensuring the soft‐ ware they create works within both functional and efficiency requirements. Ideally, you have some basic programming skills when starting this book.

I believe this book is also useful to those who primarily operate software somebody else writes, e.g., DevOps engineers, SRE, sysadmins, and platform teams. There are many optimization design levels (as discussed in ["Optimization Design Levels"](007-chapter-3-conquering-efficiency.md#page-117-0) on [page 98](007-chapter-3-conquering-efficiency.md#page-117-0)). Sometimes it makes sense to invest in software optimizations, and some‐ times we might need to address it on other levels! Moreover, to achieve reliable effi‐ ciency, software engineers have to benchmark and experiment a lot with productionlike environments (as explained in [Chapter 6](010-chapter-6-efficiency-observability.md#page-212-0)), which usually means close collaboration with platform teams. Finally, the observability practices explained in [Chapter 6](010-chapter-6-efficiency-observability.md#page-212-0) are state-of-the-art tools recommended for modern platform engineering. I am a strong proponent of avoiding differentiating between application performance monitoring (APM) and observability for SRE. If you hear that differentiation, it's mostly coming from vendors who want you to pay more or feel like they have more features. As I will explain, we can reuse the same tools, instrumentations, and signals across all software observations.<sup>2</sup> Generally, we are on the same team—we want to build better products!

Finally, I would like to recommend this book to managers, product managers, and leaders who want to stay technical and understand how to ensure you are not wasting millions of dollars on easy-to-fix efficiency issues within your team!

### How This Book Is Organized

This book is organized into 11 chapters. In [Chapter 1,](005-chapter-1-software-efficiency-matters.md#page-20-0) we discuss efficiency and why it matters. Then, in [Chapter 2](006-chapter-2-efficient-introduction-to-go.md#page-54-0), I briefly introduce Go with efficiency in mind. Then, in [Chapter 3](007-chapter-3-conquering-efficiency.md#page-90-0), we will talk about optimizations and how to think about them and approach those. Efficiency improvements can take enormous amounts of your time, but systematic approaches help you save a lot of time and effort.

In Chapters [4](008-chapter-4-how-go-uses-the-cpu-resource-or-two.md#page-130-0) and [5,](009-chapter-5-how-go-uses-memory-resource.md#page-168-0) I will explain all you need to know about latency, CPU, and memory resources, as well as how OS and Go abstract them.

Then we will move on to what it means to perform data-driven decisions around software efficiency. We will start with [Chapter 6.](010-chapter-6-efficiency-observability.md#page-212-0) Then we will discuss the reliability of experiments and complexity analysis in [Chapter 7](011-chapter-7-data-driven-efficiency-assessment.md#page-258-0). Finally, I will explain bench‐ marking and profiling techniques in Chapters [8](012-chapter-8-benchmarking-versus-stress-and-load-tests.md#page-294-0) and [9.](013-chapter-9-data-driven-bottleneck-analysis.md#page-348-0)

Last but not least, I will show you various examples of different optimization situa‐ tions in [Chapter 10.](014-chapter-10-optimization-examples.md#page-400-0) Finally, in [Chapter 11,](015-chapter-11-optimization-patterns.md#page-434-0) we will take a few learnings and summa‐ rize various efficiency patterns and tricks we see in the Go community.

<sup>2</sup> I've already gotten feedback from some experienced people that they did not know you could use metrics to work on efficiency and performance improvements! It's possible, and you will learn how here.

### Conventions Used in This Book

The following typographical conventions are used in this book:

*Italic*

Indicates new terms, URLs, email addresses, filenames, and file extensions.

#### Constant width

Used for program listings, as well as within paragraphs to refer to program ele‐ ments such as variable or function names, databases, data types, environment variables, statements, and keywords.

#### Constant width bold

Shows commands or other text that should be typed literally by the user.

#### Constant width italic

Shows text that should be replaced with user-supplied values or by values deter‐ mined by context.

![](../assets/_page_15_Picture_10.jpeg)

This element signifies a tip or suggestion.

![](../assets/_page_15_Picture_12.jpeg)

This element signifies a general note.

![](../assets/_page_15_Picture_14.jpeg)

This element indicates a warning or caution.

### Using Code Examples

This book contains code examples that should help you understand the tools, techni‐ ques, and good practices. All of them are in the Go programming language and work with Go version 1.18 and above.

You can find all the examples from this book in the executable and tested open source GitHub repository [efficientgo/examples](https://github.com/efficientgo/examples). You are welcome to fork it, use it, and play with the examples I share in this book. Everybody learns differently. For some people, it is helpful to import some examples into their favorite IDE and play with it by modifying it, running, testing, or debugging. Find the way that works for you and feel free to ask questions or propose improvements through [GitHub issues](https://github.com/efficientgo/examples/issues) [or pull requests](https://github.com/efficientgo/examples/issues)!

Note that the code examples in this book are simplified for a clear view and smaller size. Particularly, the following rules apply:

- If the Go package is not specified, assume package main.
- If the filename or extension of the example is not specified, assume the file has a *.go* extension. If it's a functional test or microbenchmark, the file name has to end with *\_test.go*.
- import statements are not always provided. In such cases, assume standard library or previously introduced packages are imported.
- Sometimes, I don't provide imports in the import statement but in a comment (// import <URL>). This is when I want to explain a single nontrivial import out of many needed in this code example.
- A comment with three dots (// ...) specifies that some unrelated content was removed. This highlights that some logic is there for a function to make sense.
- A comment with the handle error statement (// handle error) indicates that error handling was removed for readability. Always handle errors in your code!

This book is here to help you get your job done. In general, if this book offers an example code, you may use it in your programs and documentation. You do not need to contact us for permission unless you're reproducing a significant portion of the code. For example, writing a program that uses several chunks of code from this book does not require permission. Selling or distributing examples from O'Reilly books does require permission. Answering a question by citing this book and quoting example code does not require permission. However, incorporating a significant amount of example code from this book into your product's documentation does require permission.

We appreciate but generally do not require attribution. An attribution usually includes the title, author, publisher, and ISBN. For example, "*Efficient Go* by Bartło‐ miej Płotka (O'Reilly). Copyright 2023 Alloc Limited, 978-1-098-10571-6."

If you feel your use of code examples falls outside fair use or the permission given above, feel free to contact us at *[permissions@oreilly.com](mailto:permissions@oreilly.com)*.
