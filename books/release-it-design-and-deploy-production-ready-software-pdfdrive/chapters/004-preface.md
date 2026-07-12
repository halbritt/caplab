# Preface

In this book, you will examine ways to architect, design, and build software —particularly distributed systems—for the muck and mire of the real world. You will prepare for the armies of illogical users who do crazy, unpredictable things. Your software will be under attack from the moment you release it. It needs to stand up to the typhoon winds of flash mobs or the crushing pressure of a DDoS attack by poorly secured IoT toaster ovens. You'll take a hard look at software that failed the test and find ways to make sure your software survives contact with the real world.

## Who Should Read This Book

I've targeted this book to architects, designers, and developers of distributed software systems, including websites, web services, and EAI projects, among others. These must be available or the company loses money. Maybe they're commerce systems that generate revenue directly through sales or critical internal systems that employees use to do their jobs. If anybody has to go home for the day because your software stops working, then this book is for you.

## How This Book Is Organized

The book is divided into four parts, each introduced by a case study. Part I: Create Stability shows you how to keep your systems alive, maintaining system uptime. Despite promises of reliability through redundancy, distributed systems exhibit availability more like "two eights" rather than the coveted "five nines." Stability is a necessary prerequisite to any other concerns. If your system falls over and dies every day, nobody cares about anything else. Short-term fixes—and short-term thinking—will dominate in that environment. There's no viable future without stability, so we'll start by looking at ways to make a stable base.

After stability, the next concern is ongoing operations. In Part II: Design for Production, you'll see what it means to live in production. You'll deal with the complexity of modern production environments in all their virtualized, containerized, load-balanced, service-discovered gory detail. This part illustrates

good patterns for control, transparency, and availability in physical data centers and cloud environments.

In Part III: Deliver Your System, you'll look at deployments. There are great tools for pouring bits onto servers now, but that turns out to be the easy part of the problem. It's much harder to push frequent, small changes without breaking consumers. We'll look at design for deployment and at deployments without downtime, and then we'll move into versioning across disparate services—always a tricky issue!

In Part IV: Solve Systemic Problems, you'll examine the system's ongoing life as part of the overall information ecosystem. If release 1.0 is the birth of the system, then you need to think about its growth and development after that. In this part, you'll see how to build systems that can grow, flex, and adapt over time. This includes evolutionary architecture and shared "knowledge" across systems. Finally, you'll learn how to build antifragile systems through the emerging discipline of "chaos engineering" that uses randomness and deliberate stress on a system to improve it.

### About the Case Studies

I included several extended case studies to illustrate the major themes of this book. These case studies are taken from real events and real system failures that I have personally observed. These failures were very costly and embarrassing for those involved. Therefore, I obfuscated some information to protect the identities of the companies and people involved. I also changed the names of the systems, classes, and methods. Only such nonessential details have been changed, however. In each case, I maintained the same industry, sequence of events, failure mode, error propagation, and outcome. The costs of these failures are not exaggerated. These are real companies, and this is real money. I preserved those figures to underscore the seriousness of this material. Real money is on the line when systems fail.

## Online Resources

This book has its own web page, where you can find details about it, download the source code, post to the discussion forums, and report errata such as typos and content suggestions. The discussion forums are the perfect place to talk shop with other readers and share your comments about the book.

Now, let's get started with an introduction to living in production.

KWW 55 W D JRSJUFRP W LWOHV PQHH
