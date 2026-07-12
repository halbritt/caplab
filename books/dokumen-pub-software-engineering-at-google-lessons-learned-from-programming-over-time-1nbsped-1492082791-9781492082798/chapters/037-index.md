# Index

| Symbols                                       | API comments, 193                                   |
|-----------------------------------------------|-----------------------------------------------------|
| @deprecated annotation, 322                   | benefits of documentation to, 187                   |
| @DoNotMock annotation, 266                    | C++, documentation for, 193                         |
|                                               | Code Search, exposure of, 359                       |
| Α                                             | conceptual documentation and, 198                   |
| A/B diff tests, 299                           | declaring a type should not be mocked, 266          |
| limitations of, 300                           | faking, 270                                         |
| running presubmit, 304                        | service UI backend providing public API,            |
| of SUT behaviors, 296                         | 292                                                 |
| ABI compatibility, 434                        | testing via public APIs, 234-237                    |
| Abseil, compatibility promises, 434           | apologizing for mistakes, 94                        |
| adversarial group interactions, 47            | AppEngine example, exporting resources, 454         |
| advisory deprecations, 316                    | Approval stamp from reviewers, 412                  |
| AI (artificial intelligence)                  | approvals for code changes at Google, 167           |
| facial-recognition software, disadvantaging   | architecting for failure, 523                       |
| some populations, 73                          | artifact-based build systems, 380-386               |
| seed data, biases in, 282                     | functional perspective, 381                         |
| airplane, parable of, 108                     | getting concrete with Bazel, 381                    |
| alert fatigue, 318                            | other nifty Bazel tricks, 383-386                   |
| "Always of leadership"                        | time, scale, and trade-offs, 390                    |
| Always be deciding, 108                       | asking questions, 48                                |
| decide, then iterate, 110                     | asking team members if they need anything,          |
| Always be leaving, 112                        | 100                                                 |
| Always be reaving, 112 Always be scaling, 116 | asking the community, 50-52                         |
| analysis results from code analyzers, 404     | Zen management technique, 95                        |
| annotations, per-test, documenting ownership, | assertions                                          |
| 308                                           | among multiple calls to the system under            |
| Ant, 376                                      | test, 243                                           |
| performing builds by providing tasks to       | in Java test, using Truth library, <mark>248</mark> |
| command line, 377                             | stubbed functions having direct relationship        |
| · · · · · · · · · · · · · · · · · · ·         | with, 275                                           |
| replacement by more modern build systems,     | test assertion in Go, 248                           |
|                                               | verifying behavior of SUTs, 295                     |
| antipatterns in test suites, 220 APIs         | atomic changes, barriers to, 463-465                |
| ALD                                           |                                                     |

| atomicity for commits in VCSs, 328, 332              | naming tests after behavior being tested,                              |
|------------------------------------------------------|------------------------------------------------------------------------|
| attention from engineers (QUANTS), 131               | 244                                                                    |
| audience reviews, 199                                | structuring tests to emphasize behaviors,                              |
| authoring large tests, 305                           | 243                                                                    |
| authorization for large-scale changes, 473           | unanticipated, testing for, 284                                        |
| automated build system, 372                          | updates to tests for changes in, 234                                   |
| automated testing<br>code correctness checks, 172    | best practices, style guide rules enforcing, 152 Beyoncé Rule, 14, 221 |
| limits of, 229                                       | biases, 18                                                             |
| automation                                           | small expressions of in interactions, 48                               |
| automated A/B releases, 512                          |                                                                        |
|                                                      | universal presence of, 70                                              |
| in continous integration, 483-485                    | binaries, interacting, functional testing of, 297                      |
| of code reviews, 179                                 | blameless postmortems, 39-41, 88                                       |
| automation of toil in CaaS, 518-520                  | Blaze, 371, 380                                                        |
| automated scheduling, 519                            | global dependency graph, 496                                           |
| simple automations, 519                              | blinders, identifying, 109                                             |
| autonomy for team members, 104                       | in Web Search latency case study, 110                                  |
| autoscaling, <mark>522</mark>                        | Boost C++ library, compatibility promises, 435                         |
|                                                      | branch management, 336-339                                             |
| В                                                    | branch names in VCSs, 330                                              |
| backsliding, preventing in deprecation process,      | dev branches, 337-339                                                  |
| 322                                                  | few long-lived branches at Google, 343                                 |
| backward compatibility and reactions to effi-        | release branches, 339                                                  |
| ciency improvement, 11                               | work in progress is akin to a branch, 336                              |
| batch jobs versus serving jobs, 525                  | "brilliant jerks", <mark>57</mark>                                     |
| Bazel, 371, 380                                      | brittle tests, 224                                                     |
| dependency versions, 394                             | preventing, 233-239                                                    |
| extending the build system, 384                      | striving for unchanging tests, 233                                     |
|                                                      | testing state, not interactions, 238                                   |
| getting concrete with, 381                           | testing via public APIs, 234-237                                       |
| parallelization of build steps, 382                  | record/replay systems causing, 492                                     |
| performing builds with command line,                 | with overuse of stubbing, 273                                          |
| 382                                                  | browser and device testing, 297                                        |
| rebuilding only minimum set of targets               | Buck, 380                                                              |
| each time, 383                                       | bug bashes, 299                                                        |
| isolating the environment, 384                       | bug fixes, 181, 234                                                    |
| making external dependencies determinis-<br>tic, 385 | bugs                                                                   |
| platform independence using toolchains,              | catching later in development, costs of, 207                           |
| 384                                                  | in real implementations causing cascade of                             |
| remote caching and reproducible builds,              | test failures, 265                                                     |
| 387                                                  | logic concealing a bug in a test, 246                                  |
| speed and correctness, 372                           | not prevented by programmer ability alone,                             |
| tools as dependencies, 383                           | 210                                                                    |
| beginning, middle, and end sections for docu-        | BUILD files, reformatting, 162                                         |
| ments, 202                                           | build scripts                                                          |
| behaviors                                            | difficulties of task-based build systems with,                         |
| code reviews for changes in, 181                     | 379                                                                    |
| testing instead of methods, 241-246                  | writing as tasks, 378                                                  |
|                                                      | build systems, 371-398                                                 |

| dealing with modules and dependencies,                 | celebrity, <mark>29</mark>                      |
|--------------------------------------------------------|-------------------------------------------------|
| 390-396                                                | centralization versus customization in compute  |
| managing dependencies, 392-396                         | services, 537-539                               |
| minimizing module visibility, 392                      | centralized version control systems (VCSs), 332 |
| using fine-grained modules and 1:1:1                   | future of, 348                                  |
| rule, 391                                              | in-house-developed, Piper at Google, 340        |
| modern, 375-390                                        | operations scaling linearly with size of a      |
| artifact-based, 380-386                                | change, <mark>463</mark>                        |
| dependencies and, 375                                  | source of truth in, 334                         |
| distributed builds, 386-390                            | uncommitted local changes and committed         |
| task-based, 376-380                                    | changes on a branch, 336                        |
| time, scale, and trade-offs, 390                       | change management for large-scale changes,      |
| purpose of, 371                                        | 470                                             |
| using other tools instead of, 372-375                  | Changelist Search, 411                          |
| compilers, 373                                         | changelists (CLs), readability approval for, 63 |
| shell scripts, 373                                     | changes to code                                 |
| Builder pattern, 252                                   | change approvals or scoring a change, 412       |
| buildfiles, <mark>376</mark>                           | change creation in LSC process, 473             |
| build scripts and, 378                                 | commenting on, 408                              |
| in artifact-based build systems, 380                   | committing, 413                                 |
| Bazel, 381                                             | creating, 402-406                               |
| building for everyone, 77                              | large-scale (see large-scale changes)           |
| bundled distribution models, 441                       | tracking history of, 414                        |
| bus factor, 31, 112                                    | tracking in VCSs, 328                           |
|                                                        | types of changes to production code, 233        |
| C                                                      | understanding the state of, 410-412             |
| C language, projects written in, changes to, 10        | writing good change descriptions, 178           |
| C++                                                    | writing small changes, 177                      |
| APIs, reference documentation for, 193                 | chaos and uncertainty, shielding your team      |
| Boost library, compatibility promises, 435             | from, 102                                       |
| compatibility promises, 434                            | chaos engineering, 222, 302                     |
| developer guide for Googlers, 200                      | Chesterson's fence, principle of, 49            |
| googlemock mocking framework, 262                      | Churn Rule, 13                                  |
| open sourcing command-line flag libraries,             | clang-tidy, 160                                 |
| 452                                                    | integration with Tricorder, 422                 |
| scoped_ptr to std::unique_ptr, 467                     | class comments, 194                             |
| caching build results using external dependen-         | classes and tech talks, 52                      |
| cies, 395                                              | classical testing, <mark>265</mark>             |
| CamelCase naming in Python, 154                        | "clean" and "maintainable" code, 10             |
| canary analysis, 301                                   | cleanup in LSC process, 477                     |
| canarying, 482                                         | clear tests, writing, 239-248                   |
| canonical documentation, 188                           | leaving logic out of tests, 246                 |
| careers, tracking for team members, 101                | making large tests understandable, 307          |
| carrot-and-stick method of management, <mark>86</mark> | making tests complete and concise, 240          |
| catalyst, being, 96                                    | testing behaviors, not methods, 241-246         |
| cattle versus pets analogy                             | behavior-driven test, 242                       |
| applying to changes in a codebase, 474                 | method-driven test, 241                         |
| applying to server management, 524                     | naming tests after behavior being tested,       |
| CD (see continuous delivery)                           | 244                                             |
| **                                                     |                                                 |

| structuring tests to emphasize behaviors,              | answering who and when someine intro-                      |
|--------------------------------------------------------|------------------------------------------------------------|
| 2.0                                                    | duced code, 355                                            |
| writing clear failure messages, 247 "clever" code, 10  | answering why code is behaving in une-<br>pected ways, 354 |
| Clojure package management ecosystem, 447              | asnwering how others have done some-                       |
| cloud providers, public versus private, 543            | thing, 354                                                 |
| coaching a low performer, 90 code                      | asnwering what a part of the codebase is doing, 354        |
| benefits of testing, 213-214                           | impact of scale on design, 359-361                         |
| code as a liability, not an asset, 167, 313            | index latency, 360                                         |
| embedding documentation in with g3doc,                 | search query latency, 359                                  |
| 190                                                    | reasons for a separate web tool, 355-359                   |
|                                                        |                                                            |
| expressing tests as, 212<br>knowledge sharing with, 56 | integration with other developer tools,<br>356-359         |
|                                                        |                                                            |
| quality of, 131                                        | scale of Google's codebase, 355                            |
| code coverage, 222                                     | specialization, 356                                        |
| code formatters, 161                                   | zero setup global code view, 356                           |
| code reviews, 56, 62-66, 165-183                       | trade-offs in implementing, 366-369                        |
| benefits of, 166, 170-176                              | completeness, all vs. most-relevant                        |
| code consistency, 173                                  | results, 366                                               |
| comprehension of code, 172                             | completeness, head vs. branches vs. all                    |
| correctness of code, 171                               | history vs. workspaces, 367                                |
| knowledge sharing, 175                                 | completeness, repository at head, 366                      |
| psychological and cultural, 174                        | expressiveness, token vs. substring vs.                    |
| best practices, 176-180                                | regex, 368                                                 |
| automating where possible, 179                         | UI, 352                                                    |
| being polite and professional, 176                     | code sharing, tests and, 248-255                           |
| keeping reviewers to a minimum, 179                    | defining test infrastructure, 255                          |
| writing good change descriptions, 178                  | shared helpers and validation, 254                         |
| writing small changes, 177                             | shared setup, 253                                          |
| code as a liability, 167                               | shared values, 251                                         |
| flow, 400                                              | test that is too DRY, 249                                  |
| for large-scale changes, 467, 476                      | tests should be DAMP, 250                                  |
| how they work at Google, 167-169                       | codebase                                                   |
| ownership of code, 169-170                             | analysis of, large-scale changes and, 470                  |
| steps in, 166                                          | comments in, reference documentation gen-                  |
| types of, 180-182                                      | erated from, 193                                           |
| behavioral changes, improvements, and                  | factors affecting flexibility of, 16                       |
| optimizations, 181                                     | scalability, 12                                            |
| bug fixes and rollbacks, 181                           | sustainability, 12                                         |
| greenfield reviews, 180                                | value of codebase-wide consistency, 64                     |
| refactorings and large-scale changes, 182              | codelabs, 60                                               |
| Code Search, 178, 351-370                              | commenting on changes in Critique, 408                     |
| Google's implementation, 361-365                       | comments                                                   |
| ranking, 363-365                                       | code, 193                                                  |
| search index, 361                                      | style guide rules for, 145                                 |
| how Googlers use it, 353-355                           | communities                                                |
| answering where something is in the                    | cross-organizational, sharing knowledge in,                |
| codebase, 353                                          | 62                                                         |

| getting help from the community, 50-52           | containers and implicit dependencies, 532         |
|--------------------------------------------------|---------------------------------------------------|
| compiler integration with static analysis, 426   | context, understanding, 49                        |
| compiler upgrage (example), 14-16                | continuous build (CB), 483                        |
| compilers, using instead of build systems, 373   | continuous delivery (CD), 483, 505-515            |
| completeness and conciseness in tests, 240       | breaking up deployment into manageable            |
| completeness, accuracy, and clarity in docu-     | pieces, 507                                       |
| mentation, 202                                   | changing team culture to build disclipline        |
| comprehension of code, 172                       | into deployment, 513                              |
| compulsory deprecation, 317                      | evaluating changes in isolation, flag-            |
| Compute as a Service (CaaS), 517-545             | guarding features, <mark>508</mark>               |
| choosing a compute service, 535-544              | idioms of CD at Google, 506                       |
| centralization versus customization,             | quality and user-focus, shipping only what        |
| 537-539                                          | gets used, 511                                    |
| level of abstraction, serverless, 539-543        | shifting left and making data-driven deci-        |
| public versus private, 543                       | sions earlier, 512                                |
| over time and scale, 530-535                     | striving for agility, setting up a release train, |
| containers as an abstraction, 530-532            | 509-510                                           |
| one service to rule them all, 533                | continuous deployment (CD), release branches      |
| submitted configuration, 535                     | and, 339                                          |
| taming the compute environment, 518-523          | continuous integration (CI), 14, 479-503          |
| automation of toil, 518-520                      | alerting, 487-493                                 |
| containerization and multitenancy,               | CI challenges, 490                                |
| 520-522                                          | hermetic testing, 491                             |
| writing software for managed compute,<br>523-530 | core concepts, 481-487 automation, 483-485        |
| architecting for failure, 523                    | continuous testing, 485-487                       |
| batch versus serving, 525                        | fast feedback loops, 481-483                      |
| connecting to a service, 528                     | dev branches and, 338                             |
| managing state, 527                              | greenfield reviews necessitating for a            |
| one-off code, 529                                | project, 180                                      |
| conceptual documentation, 198                    | implementation at Google, 493-503                 |
| condescending and unwelcoming behaviors, 47      | case study, Google Takeout, 496-502               |
| configuration issues with unit tests, 283        | TAP, global continuous build, 494-496             |
| consensus, building, 96                          | Live at Head dependency management and,           |
| consistency within the codebase, 146             | 442                                               |
| advantages of, 146                               | system at Google, <mark>223</mark>                |
| building in consistency, rules for, 153          | contract fakes, 272                               |
| ensuring with code reviews, 173                  | cooperative group interactions, 47                |
| exceptions to, conceding to practicalities,      | correctness in build systems, 372                 |
| 150                                              | correctness of code, 171                          |
| inefficiency of perfect consistency in very      | costs                                             |
| large codebase, 148                              | in software engineering, 12                       |
| One-Version Rule and, 342                        | reducing by finding problems earlier in           |
| setting the standard, 148                        | development, 17                                   |
| constructive criticism, 37                       | trade-offs and, 18-23                             |
| consumer-driven contract tests, 293              | deciding between time and scale (exam-            |
| containerization and multitenancy, 520-522       | ple), <mark>22</mark>                             |
| rightsizing and autoscaling, 522                 | distributed builds (example), 20                  |
| containers as an abstraction, 530-532            | inputs to decision making, 20, 20                 |

| mistakes in decision making, 22                | deciding, then iterating, 110                   |
|------------------------------------------------|-------------------------------------------------|
| types of costs, 18                             | in an engineering group, justifications for,    |
| whiteboard markers (example), 19               | 19                                              |
| criticism, learning to give and take, 37       | inputs to decision making, 20                   |
| Critique code review tool, 165, 353, 399-416   | making at higher levels of leadership, 108      |
| change approvals, 412                          | delegation of subproblems to team leaders, 113  |
| code review flow, 400                          | dependencies                                    |
| code review tooling principles, 399            | Bazel treating tools as dependencies to each    |
| committing a change, 413                       | target, 383                                     |
| creating a change, 402-406                     | build systems and, 375                          |
| analysis results, 404                          | construction when using real implementa-        |
| diffing, 403                                   | tions in tests, 268                             |
| tight tool ingegration, 406                    | containers and implicit dependencies, 532       |
| diff viewer, Tricorder warnings on, 421        | dependency management versus version            |
| request review, 406-408                        | control, 336                                    |
| understanding and commenting on a              | external, causing nondeterminism in tests,      |
| change, 408-412                                | 268                                             |
| view of static analysis fix, 424               | external, compilers and, 373                    |
| cryptographic hashes, 385                      | forking/reimplementing versus adding a          |
| culprit finding and failure isolation, 490     | dependency, 22                                  |
| using TAP, 495                                 | in task-based build systems, 377                |
| culture                                        | making external dependencies deterministic      |
| building discipline into deployment, 513       | in Bazel, <mark>385</mark>                      |
| changes in norms surrounding LSCs, 469         | managing for modules in build systems,          |
| cultivating knowledge-sharing culture,         | 392-396                                         |
| 56-58                                          | automatic vs. manual management, 394            |
| cultural benefits of code reviews, 174         | caching build results using external            |
| culture of learning, 43                        | dependencies, 395                               |
| data-driven, 19, 22                            | external dependencies, 393                      |
| healthy automated testing culture, 213         | internal dependencies, 392                      |
| testing culture today at Google, 228           | One-Version Rule, 394                           |
| customers, documentation for, 192              | security and reliability of external            |
| CVS (Concurrent Versions System), 328, 332     | dependencies, 396                               |
|                                                | transitive external dependencies, 395           |
| D                                              | new, preventing introduction into depre-        |
| DAMP, 249                                      | cated system, 322                               |
| complementary to DRY, not a replacement,       | on values in shared setup methods, 253          |
| 251                                            | replacing all in a class with test doubles, 265 |
| test rewritten to be DAMP, 250                 | test scope and, 219                             |
| dashboard and search system (Critique), 411    | unknown, discovering during deprecation,        |
| data structures in libraries, listings of, 158 | 318                                             |
| data-driven culture                            | dependency injection                            |
| about, 19                                      | frameworks for, 261                             |
| admitting to mistakes, 22                      | introducing seams with, 260                     |
| data-driven decisions, making earlier, 512     | dependency management, 429-457                  |
| datacenters, automating management of, 523     | difficulty of, reasons for, 431-433             |
| debugging versus testing, 210                  | conflicting requirements and diamond            |
| decisions                                      | dependencies, 431-433                           |
| admitting to making mistakes, 22               | importing dependencies, 433-439                 |

| compatibility promises, 433-436                  | developer happiness, focus on, with static anal-                  |
|--------------------------------------------------|-------------------------------------------------------------------|
| considerations in, 436                           | ysis, <b>41</b> 9                                                 |
| Google's handling of, 437-439                    | developer tools, Code Search integration with,                    |
| in theory, <b>439-443</b>                        | 356-359                                                           |
| bundled distribution models, 441                 | developer workflow, large tests and, 304-309                      |
| Live at Head, 442                                | authoring large tests, 305                                        |
| nothing changes (static dependency               | running large tests, 305-308                                      |
| model), 439                                      | driving out flakiness, 306                                        |
| semantic versioning, 440                         | making tests understandable, 307                                  |
| limitations of semantic versioning, 443-449      | owning large tests, 308                                           |
| Minimum Version Selection, 447                   | speeding up tests, 305                                            |
| motivations, 446                                 | developer workflow, making static analysis part                   |
| overconstrains, 444                              | of, 420                                                           |
| overpromising compatibility, 445                 | DevOps                                                            |
| questioning whether it works, 448                | philosophy on tech productivity, 32                               |
| with infinite resources, 449-455                 | trunk-based development popularized by,                           |
| exporting dependencies, 452-455                  | 327                                                               |
| deployment                                       | DevOps Research and Assessment (DORA)                             |
| breaking up into manageable pieces, 507          | no long-lived branches and, 343                                   |
| building discipline into, 513                    | predictive relationship between trunk-based                       |
| deployment configuration testing, 298            | development and high-performing                                   |
| deprecation, 311-323                             | organizations, 343                                                |
| as example of scaling problems, 13               | research on release branches, 339                                 |
| difficulty of, 313-315                           | diamond dependency issue, 394, 431-433                            |
| during design, 315                               | diffing code changes, 403<br>change summary and diff view, 404    |
| managing the process, 319-322                    |                                                                   |
| deprecation tooling, 321-322<br>milestones, 320  | direction, giving to team members, 104                            |
|                                                  | disaster recovery testing, 302<br>discovery (in deprecation), 321 |
| process owners, 320<br>of old documentation, 203 | distributed builds, 386-390                                       |
| preventing new uses of deprecated object,        | at Google, 389                                                    |
| 477                                              | remote caching, 386                                               |
| reasons for, 312                                 | remote execution, 387                                             |
| static analysis in API deprecation, 417          | trade-offs and costs example, 20                                  |
| types of, 316-319                                | distributed version control systems (DVCSs),                      |
| advisory deprecation, 316                        | 332                                                               |
| compulsory deprecation, 317                      | compression of historical data, 367                               |
| deprecation warnings, 318                        | scenario, no clear source of truth, 335                           |
| Descriptive And Meaningful Phrases (see          | source of truth, 334                                              |
| DAMP)                                            | diversity                                                         |
| design documents, 195                            | making it actionable, 74                                          |
| design reviews for new code or projects, 180     | understanding the need for, 72                                    |
| designing systems to eventually be deprecated,   | Docker, 531                                                       |
| 315                                              | documentation, 53-55, 185-205                                     |
| determinism in tests, 267                        | about, 185                                                        |
| dev branches, 337-339                            | benefits of, 186-187                                              |
| no long-lived branches and, 343                  | code, <mark>56</mark>                                             |
| developer guides, 59                             | Code Search integration in, 358                                   |
| -                                                | creating, 54                                                      |
|                                                  | <del>-</del>                                                      |

| for code changes, 178                          | letting the team know failure is an option,    |
|------------------------------------------------|------------------------------------------------|
| knowing your audience, 190-192                 | 87                                             |
| types of audiences, 191                        | manager as four-letter word, 86                |
| philosophy, 201-204                            | engineering productivity                       |
| beginning, middle, and end sections, 202       | improving with testing, 231                    |
| deprecating documents, 203                     | readability program and, 65                    |
| parameters of good documentation, 202          | Engineering Productivity Research (EPR) team   |
| who, what, why, when, where, and how,          | 65                                             |
| 201                                            | engineering productivity, measuring, 123-138   |
| promoting, 55                                  | assessing worth of measuring, 125-128          |
| treating as code, 188-190                      | goals, 130                                     |
| Google wiki and, 189                           | metrics, 132                                   |
| types of, 192-199                              | reasons for, 123-125                           |
| conceptual, 198                                | selecting meaningful metrics with goals and    |
| design documents, 195                          | signals, 129-130                               |
| landing pages, 198                             | signals, 132                                   |
| reference, 193-195                             | taking action and tracking results after per-  |
| tutorials, 196                                 | forming research, 137                          |
| updating, 54                                   | validating metrics with data, 133-137          |
| when you need technical writers, 204           | equitable and inclusive engineering, 69-79     |
| documentation comments, 145                    | bias and, 70                                   |
| documentation reviews, 199-201                 | building multicultural capacity, 72-74         |
| documented knowledge, 45                       | challenging established processes, 76          |
| domain knowledge of documentation audien-      | making diversity actionable, 74                |
| ces, 191                                       | need for diversity, 72                         |
| DRY (Don't Repeat Yourself) principle          | racial inclusion, 70                           |
| tests and code sharing, DAMP, not DRY,         | rejecting singular approaches, 75              |
| 248-255                                        | staying curious, and pushing forward, 78       |
| DAMP as complement to DRY, 251                 | values versus outcomes, 77                     |
| test that is too DRY, 249                      | error checking tools, 160                      |
| violating for clearer tests, 241               | Error Prone tool (Java), 160                   |
| DVCSs (see distributed version control sys-    | @DoNotMock annotation, 266                     |
| tems)                                          | integration with Tricorder, 422                |
|                                                | error-prone and surprising constructs in code, |
| E                                              | avoiding, 149                                  |
| Edison, Thomas, 38                             | execution time for tests, 267                  |
| education of software engineers, 72            | speeding up tests, 305                         |
| more inclusive education needed, 74            | experience levels for documentation audiences, |
| efficiency improvements, changing code for, 11 | 191                                            |
| ego, losing, 36, 93                            | experiments and feature flags, 482             |
| Eisenhower, Dwight D., 118                     | expertise                                      |
| email at Google, 51                            | all-or-nothing, 44                             |
| Emerson, Ralph Waldo, 150                      | personalized advice from an expert, 45         |
| end-to-end tests, 219                          | and shared communication forums, 14            |
| engineering managers, 82, 86-88, 88            | exploitation versus exploration problem, 363   |
| (see also leading a team; managers and tech    | exploratory testing, 229, 298                  |
| leads)                                         | extrinsic versus intrinsic motivation, 104     |
| contemporary managers, 87                      |                                                |

| F                                                       | flag-guarding features, 508                             |
|---------------------------------------------------------|---------------------------------------------------------|
| "Fail early, fail fast, fail often", 31                 | flaky tests, 216, 267, 490                              |
| failures                                                | driving out flakiness in large tests, 306               |
| addressing test failures, 213                           | expense of, 218                                         |
| architecting for failure in software for man-           | Forge, 389, 496                                         |
| aged compute, 523                                       | forking/reimplementing versus adding a                  |
| bug in real implementation causing cascade              | dependency, 22                                          |
| of test failures, 265                                   | function comments, 195                                  |
| clear code aiding in diagnosing test failures,          | functional programming languages, 381                   |
| 218                                                     | functional tests, 219                                   |
| culprit finding and failure isolation, 490              | testing of one or more interacting binaries,            |
| fail fast and iterate, 38                               | 297                                                     |
| failure is an option, 87                                |                                                         |
| failure management with TAP, 495                        | G                                                       |
| large test that fails, 307                              | <del>-</del>                                            |
| reasons for test failures, 239                          | g3doc, <mark>190</mark><br>Gates, Bill, <mark>28</mark> |
| testing for system failure, 222                         |                                                         |
| writing clear failure messages for tests, 247           | generated files, Code Search index and, 366             |
| faking, 263, 269-272                                    | Genius Myth, 28                                         |
| fake hermetic backend, 491                              | Gerrit code review tool, 414                            |
| fidelity of fakes, 271                                  | Git, 333                                                |
| importance of fakes, 270                                | improvements to, 347                                    |
|                                                         | synthesizing monorepo behavior, 346                     |
| testing fakes, 272<br>when fakes are not available, 272 | given/when/then, expressing behaviors, 242              |
| when to write fakes, 270                                | alternating when/then blocks, 244                       |
|                                                         | well-structured test with, 243                          |
| false negatives in static analysis, 419                 | Go programming language                                 |
| false positives in static analysis, 419                 | compatibility promises, 434                             |
| features page 234                                       | gofmt tool case study, 161-163                          |
| features, new, 234                                      | standard package management ecosystem,                  |
| federated/virtual-monorepo (VMR)-style                  | 447                                                     |
| repository, 346                                         | test assertion in, 248                                  |
| feedback                                                | go/links, 60                                            |
| accelerating pace of progress with, 32                  | use with canonical documentation, 188, 201              |
| fast feedback loops in CI, 481-483                      | goals                                                   |
| for documentation, 54                                   | defined, 129                                            |
| giving hard feedback to team members, 98                | team leader setting clear goals, 97                     |
| integrated feedback channels in Tricorder,              | Goals/Signals/Metrics (GSM) framework,                  |
| 423                                                     | 129-133                                                 |
| soliciting from developers on static analysis,          | goals, 130                                              |
| 419                                                     | metrics, 132                                            |
| fidelity                                                | signals, 132                                            |
| of fakes, 271                                           | use for metrics in readability process study,           |
| of SUTs, 290                                            | 134                                                     |
| of test doubles, 258                                    | Google Assistant, 492                                   |
| of tests, 282                                           | Google Search, 6                                        |
| file comments, 194                                      | and bifurcation of Google's internal com-               |
| file locking in VCSs, 329, 332                          | pute offering, 538                                      |
| filesystem abstraction, 531                             | larger tests at Google, 286                             |
| filesystems, VCS as way to extend, 329                  | manually testing functionality of, 210                  |
|                                                         |                                                         |

| subdividing latency problem of, 113 Google Takeout case study, 496-502 Google Web Server (GWS), 209 Google wiki (GooWiki), 189 "Googley", being, 41 Gradle, 376 dependency versions, 394\nimprovements on Ant, 378 greenfield code reviews, 180 grep command, 352 group chats, 50 | human issues, ignoring in a team, 90 human problems, solving, 29 humility, 35 being "Googley", 41 practicing, 36-39 hybrid SUTs, 291 Hyrum's Law, 8 consideration in unit tests, 284 deprecation and, 313 hash ordering (example), 9 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Grunt, 376                                                                                                                                                                                                                                                                        | I                                                                                                                                                                                                                                    |
| H "hacky" or "clever" code, 10 Hamming, Richard, 35, 36 happiness, tracking for your team, 99 outside the office and in their careers, 100                                                                                                                                        | ice cream cone antipattern in testing, 220, 287 idempotency, 529  IDEs (integrated development environments) reasons for using Code Search instead of, 355-359 static analysis and, 427                                              |
| hash flooding attacks, 9                                                                                                                                                                                                                                                          | image recognition, racial inclusion and, 70                                                                                                                                                                                          |
| hash ordering (example), 9                                                                                                                                                                                                                                                        | imperative programming languages, 381                                                                                                                                                                                                |
| haunted graveyards, 44, 464                                                                                                                                                                                                                                                       | implementation comments, 145, 193                                                                                                                                                                                                    |
| Heartbleed, 10                                                                                                                                                                                                                                                                    | important versus urgent problems, 118                                                                                                                                                                                                |
| "Hello World" tutorials, 196                                                                                                                                                                                                                                                      | improvements to existing code, code reviews                                                                                                                                                                                          |
| helper methods shared helpers and validation, 254                                                                                                                                                                                                                                 | for, 181 incentives and recognition for knowledge shar-                                                                                                                                                                              |
| shared values in, 252                                                                                                                                                                                                                                                             | ing, 57                                                                                                                                                                                                                              |
| hermetic code, nondeterminism and, 268<br>hermetic SUTs, 290                                                                                                                                                                                                                      | incremental builds, difficulty in task-based build systems, 379                                                                                                                                                                      |
| benefits of, 291                                                                                                                                                                                                                                                                  | indexes                                                                                                                                                                                                                              |
| hermetic testing, 491                                                                                                                                                                                                                                                             | Code Search versus IDEs, 355                                                                                                                                                                                                         |
| Google Assistant, 492                                                                                                                                                                                                                                                             | dropping files from Code Search index, 366                                                                                                                                                                                           |
| hero worship, 28                                                                                                                                                                                                                                                                  | indexing multiple versions of a repository,<br>367                                                                                                                                                                                   |
| hiding your work<br>Genius Myth and, 29                                                                                                                                                                                                                                           | latency in Code Search, 360                                                                                                                                                                                                          |
| harmful effects of, 30-34                                                                                                                                                                                                                                                         | search index in Code Search, 361                                                                                                                                                                                                     |
| bus factor, 31                                                                                                                                                                                                                                                                    | individual engineers, increasing productivity                                                                                                                                                                                        |
| engineers and offices, 32                                                                                                                                                                                                                                                         | of, 124                                                                                                                                                                                                                              |
| forgoing early detection of flaws or                                                                                                                                                                                                                                              | influence, being open to, 40                                                                                                                                                                                                         |
| issues, 31                                                                                                                                                                                                                                                                        | influencing without authority (case study), 83                                                                                                                                                                                       |
| pace of progress, 32                                                                                                                                                                                                                                                              | information islands, 43                                                                                                                                                                                                              |
| hiring of software engineers                                                                                                                                                                                                                                                      | information, canonical sources of, 58-61                                                                                                                                                                                             |
| compromising the hiring bar (antipattern),                                                                                                                                                                                                                                        | codelabs, 60                                                                                                                                                                                                                         |
| 92                                                                                                                                                                                                                                                                                | developer guides, <mark>5</mark> 9                                                                                                                                                                                                   |
| hiring pushovers (antipattern), 89                                                                                                                                                                                                                                                | go/ links, <mark>60</mark>                                                                                                                                                                                                           |
| making diversity actionable, 75                                                                                                                                                                                                                                                   | static analysis, 61                                                                                                                                                                                                                  |
| history, indexing in Code Search, 367                                                                                                                                                                                                                                             | insecurity, 28                                                                                                                                                                                                                       |
| honesty, being honest with your team, 98                                                                                                                                                                                                                                          | criticism and, 37                                                                                                                                                                                                                    |
| "Hope is not a strategy", 89                                                                                                                                                                                                                                                      | manifestation in Genius Myth, <mark>29</mark>                                                                                                                                                                                        |
| hourglass antipattern in testing, 220                                                                                                                                                                                                                                             | integration tests, 219                                                                                                                                                                                                               |

| intellectual complexity (QUANTS), 131              | establishing canonical sources of infor-      |
|----------------------------------------------------|-----------------------------------------------|
| interaction testing, 238, 275-280                  | mation, 58-61                                 |
| appropriate uses of, 277                           | staying in the loop, 61-62                    |
| best practices, 277                                | standardized mentorship through code          |
| avoiding overspecification, 278                    | reviews, <mark>62-66</mark>                   |
| performing only for state-changing                 | teaching others, 52-56                        |
| functions, 277                                     | Kondo, Marie, 119                             |
| preferring state testing over, 275                 | Kubernetes clusters, 533                      |
| limitations of interaction testing, 276            | kudos, 58                                     |
| using test doubles, 264                            | Kythe, 470                                    |
| interoperability of code, 151                      | integration with Code Search, 351             |
| intraline diffing showing character-level differ-  | navigating cross-references with, 406         |
| ences, 403                                         | ,                                             |
| intrinsic versus extrinsic motivation, 104         | 1                                             |
| iteration, making your teams comfortable with,     | L 100                                         |
| 110                                                | landing pages, 198                            |
|                                                    | Large Scale Change tooling and processes, 148 |
| 1                                                  | large tests, 217                              |
| j                                                  | (see also larger testing)                     |
| Java                                               | large-scale changes, 372, 459-478             |
| assertion in a test using Truth library, 248       | barriers to atomic changes, 463-465           |
| javac compiler, 373                                | heterogeneity, 464                            |
| Mockito mocking framework for, 262                 | merge conflicts, 463                          |
| shading in, 342                                    | no haunted graveyards, 464                    |
| third-party JAR files, 373                         | technical limitations, 463                    |
| Jevons Paradox, 21                                 | testing, 465                                  |
| Jobs, Steve, 28, 92                                | code reviews for, 182                         |
| Jordan, Michael, <mark>28</mark>                   | importance of trunk-based development         |
| JUnit, 305                                         | and, 343                                      |
|                                                    | infrastructure, 468-472                       |
| K                                                  | change management, 470                        |
| key abstractions and data structures in libraries, | codebase insight, 470                         |
| listings of, 158                                   | language support, 471                         |
| knowledge sharing, 43-67                           | Operation RoseHub, 472                        |
| as benefit of code reviews, 175                    | policies and culture, 469                     |
| asking the community, 50-52                        | testing, 471                                  |
| challenges to learning, 43                         | larger tests skipped during, 285              |
| critical role of psychological safety, 46-48       | process, 472-477                              |
| growing your knowledge, 48, 49                     | authorization, 473                            |
| asking questions, 48                               | change creation, 473                          |
| understanding context, 49                          | cleanup, 477                                  |
| increasing knowledge by working with oth-          | sharding and submitting, 474-477              |
| ers, 31                                            | qualities of, <mark>460</mark>                |
| philosophy of, 45                                  | responsibility for, 461-462                   |
| readability process and code reviews, 158          | testing, 466-468                              |
| scaling your organization's knowledge,             | code reviews, 467                             |
| 56-62                                              | riding the TAP train, 466                     |
| cultivating knowledge-sharing culture,             | scoped_ptr to std::unique_ptr, 467            |
| 56-58                                              | larger testing, 281-309                       |
|                                                    | advantages of, 282                            |

| challenges and limitations of, 285             | hiring pushovers, 89                         |
|------------------------------------------------|----------------------------------------------|
| characteristics of, 281                        | ignoring human issues, 90                    |
| fidelity of tests, 282                         | ignoring low performers, 89                  |
| large tests and developer workflow, 304-309    | treating your team like children, 92         |
| authoring large tests, 305                     | asking team members if they need anything    |
| running large tests, 305-308                   | 100                                          |
| larger tests at Google, 286-289                | engineering manager, <mark>86-88</mark>      |
| Google scale and, 288                          | failure as an option, 87                     |
| time and, 286                                  | history of managers, 86                      |
| structure of a large test, 289-296             | today's manager, 87                          |
| systems under test (SUTs), 290-294             | fulfilling different needs of team members,  |
| test data, 294                                 | 103                                          |
| verification, 295                              | motivation, 104                              |
| types of large tests, 296-304                  | managers and tech leads, 81-83               |
| A/B diff (regression), 299                     | case study, influencing without author-      |
| browser and device testing, 297                | ity, 83                                      |
| deployment configuration testing, 298          | engineering manager, 82                      |
| disaster recovery and chaos engineering,       | tech lead, 82                                |
| 302                                            | tech lead manager, 82                        |
| exploratory testing, 298                       | moving from individual contributor to lead   |
| functional testing of interacting binaries,    | ership role, <mark>83-86</mark>              |
| 297                                            | reasons people don't want to be manag-       |
| performance, load, and stress testing,         | ers, 84                                      |
| 297                                            | servant leadership, 85                       |
| probers and canary analysis, 301               | other tips and tricks for, 101               |
| UAT, 301                                       | positive patterns, 93-100                    |
| user evaluation, 303                           | being a catalyst, 96                         |
| unit tests not providing good risk mitigation  | being a teacher and mentor, 97               |
| coverage, 283-284                              | being a Zen master, 94                       |
| law enforcement facial recognition databases,  | being honest, 98                             |
| racial bias in, 74                             | losing the ego, 93                           |
| leadership, brilliant jerks and, 57            | removing roadblocks, 96                      |
| leadership, scaling into a really good leader, | setting clear goals, 97                      |
| 107-122                                        | tracking happiness, 99                       |
| Addressing Web Search latency (case study),    | learning, 46                                 |
| 110-112                                        | (see also knolwedge sharing)                 |
| Always be deciding, 108                        | challenges to, 43                            |
| Always be leaving, 112                         | LGTM (looks good to me) stamp from review-   |
| Always be scaling, 116                         | ers, 166                                     |
| deciding, then iterating, 110                  | change approval with, 401                    |
| identifying key trade-offs, 109                | code owner's approval and, 168               |
| identifying the blinders, 109                  | correctness and comprehension checks, 167    |
| important vs. urgent problems, 118-119         | from primary reviewer, 178                   |
| learning to drop balls, 119                    | meaning of, 412                              |
| protecting your energy, 120                    | separation from readability approval, 173    |
| leading a team, 81-105                         | tech leads submitting code change after, 168 |
| antipatterns, 88-93                            | libraries, compilers and, 373                |
| being everyone's friend, 91                    | linters in Tricorder, 425                    |
| compromising the hiring bar, 92                | Linux                                        |

| developers of, 28                             | in hard-to-quantify areas, 20                   |
|-----------------------------------------------|-------------------------------------------------|
| kernel patches, sources of truth for, 335     | medium tests, 217                               |
| Live at Head model, 442                       | Meltdown and Spectre, 11                        |
| load, testing, 297                            | mentorship, 46                                  |
| log viewer, Code Search integration with, 357 | being a teacher and mentor for your team,       |
| logic, not putting in tests, 246              | 97                                              |
| LSCs (see large-scale changes)                | standardized, through code reviews, 62-66       |
|                                               | merge conflicts, size of changes and, 463       |
| M                                             | merges                                          |
| mailing lists, 50                             | branch-and-merge process, development as,       |
| •                                             | 330                                             |
| maintainability of tests, 232                 | coordination of dev branch merging, 338         |
| "manageritis", 84                             | dev branches and, 338                           |
| managers and tech leads, 81-83                | merge tracking in VCSs, 329                     |
| antipatterns, 88-93                           | method-driven tests, 241                        |
| being everyone's friend, 91                   | example test, 241                               |
| compromising the hiring bar, 92               | sample method naming patterns, 246              |
| hiring pushovers, 89                          | metrics                                         |
| ignoring human issues, 90                     | assessing worth of measuring, 125-128           |
| ignoring low performers, 89                   | in GSM framework, 129, 132                      |
| treating your team like children, 92          | meaningful, selecting with goals and signals,   |
| case study, influencing without authority, 83 | 129-130                                         |
| engineering manager, 82, 86-88                | using data to validate, 133-137                 |
| contemporary, 87                              | migrations                                      |
| failure as an option, 87                      | in the deprecation process, 322                 |
| history of managers, 86                       | migrating users from an obsolete system,        |
| moving from individual contributor to lead-   | 317                                             |
| ership role, 83-86                            | milestones of a deprecation process, 320        |
| reasons people don't want to be manag-        | Minimum Version Selection (MVS), 447            |
| ers, 84                                       | mobile devices, browser and device testing, 297 |
| servant leadership, 85                        | mocking, 257                                    |
| positive patterns, 93-100                     | (see also test doubles)                         |
| being a catalyst, 96                          | interaction testing and, 264                    |
| being a teacher and mentor, 97                | misuse of mock objects, causing brittle tests,  |
| being a Zen master, 94                        | 224                                             |
| being honest, 98                              | mocks becoming stale, 283                       |
| losing the ego, 93                            | mocking frameworks                              |
| removing roadblocks, 96                       | about, 261                                      |
| setting clear goals, 97                       | for major programming languages, 262            |
| tracking happiness, 99<br>tech lead, 82       | interaction testing done via, 264               |
| •                                             | over reliance on, 239, 259                      |
| tech lead manager (TLM), 82                   | stubbing via, <mark>264</mark>                  |
| manual testing, 286                           | mockist testing, 265                            |
| Markdown, 190                                 | Mockito                                         |
| mastery for team members, 104                 | example of use, 262                             |
| Maven, 376                                    | stubbing example, 263                           |
| improvements on Ant, 378                      | modules, dealing with in build systems,         |
| measurements, 123                             | 390-396                                         |
| (see also engineering productivity, measur-   | managing dependencies, 392-396                  |
| ing)                                          | 0 0 1                                           |

| minimizing module visibility, 392             | Р                                                                 |
|-----------------------------------------------|-------------------------------------------------------------------|
| using fine-grained modules and 1:1:1 rule,    | Pact Contract Testing, 293                                        |
| 391                                           | Pants, 380                                                        |
| monorepos, 345                                | parallelization of build steps                                    |
| arguments against, 346                        | difficulty in task-based systems, 378                             |
| organizations citing benefits of, 346         | in Bazel, 383                                                     |
| motivating your team, 103                     | parallelization of tests, 267                                     |
| intrinsic vs. extrinsic motivation, 104       | parroting, 44                                                     |
| move detection for code chunks, 403           | Pascal, Blaise, 191                                               |
| multicultural capacity, building, 72-74       | patience and kindness in answering questions,                     |
| how inequalities in society impact workpla-   | 49                                                                |
| ces, <b>74</b>                                | patience, learning, 39                                            |
| multimachine SUT, <mark>291</mark>            | peer bonuses, 58                                                  |
| multitenancy, containerization and, 521-522   | Perforce, revision mumbers for a change, 336                      |
| multitenancy for serving jobs, 534            | performance                                                       |
| multitenant framework servers, 540            | accommodating optimizations in the code-<br>base, 151             |
| N                                             | testing, <mark>297</mark>                                         |
| named resources, managing on the machine,     | performance of software engineers                                 |
| 531                                           | flaws in performance ratings, 76                                  |
| network ports, containers and, 531            | ignoring low performers, 89                                       |
| newsletters, 61                               | personnel costs, 18                                               |
| no binary is perfect, 509                     | "Peter Principle", 84                                             |
| non-state-changing functions, 278             | Piper, 340                                                        |
| nondeterministic behavior in tests, 216, 218, | Code Search integration with, 353                                 |
| 267                                           | tools built on top of, 406                                        |
| notifications from Critique, 402              | policies for large-scale changes, 469                             |
| 0                                             | politeness and professionalism in code reviews                    |
| office hours, using for knowledge sharing, 52 | postmortems, blameless, 39-41, 88                                 |
| 1:1:1 rule, <mark>391</mark>                  | precommit reviews, 400                                            |
| one-off code, <mark>529</mark>                | presubmits, 179                                                   |
| One-Version Rule, 340, 342, 394               | checks in Tricorder, 425                                          |
| monorepos and, 345                            | continuous testing and, 485                                       |
| Open Source Software (OSS)                    | infrastructure for large tests, 305                               |
| dependency management and, 430                | optimization of, 490, 494<br>testing on merges in dev branch, 338 |
| monorepos and, 347                            |                                                                   |
| open sourcing gflags, <mark>452</mark>        | versus postsubmit, 486<br>probers, 301                            |
| Operation RoseHub, 472                        | problems                                                          |
| optimizations of existing code, code reviews  | dividing the problem space, 113-116                               |
| for, 181                                      | important vs. urgent, 118                                         |
| overspecification of interaction tests, 278   | product stability, dev branches and, 337                          |
| ownership of code, 169-170                    | production                                                        |
| deprecation process owners, 320               | risks of testing in, 292                                          |
| for greenfield reviews, 180                   | testing in, 487                                                   |
| granular ownership in Google monorepo,        | professionalism in code reviews, 176                              |
| 340                                           | programming                                                       |
| owning large tests, 308                       | clever code and, 10                                               |
|                                               | ·                                                                 |

| software engineering versus, 3, 23              | question-and-answer system (YAQS), 51            |
|-------------------------------------------------|--------------------------------------------------|
| programming guidance, 157                       | questions, asking (see asking questions)         |
| programming languages                           |                                                  |
| advice for areas more difficult to get correct, | R                                                |
| 158                                             | racial bias in facial recognition databases, 74  |
| avoiding use of error-prone and surprising      | racial inclusion, 70                             |
| constructs, 149                                 | Rake, 376                                        |
| breakdowns of new feature and advice on         | ranking in Code Search, 363-365                  |
| using them, 158                                 | query dependent signals, 364                     |
| documenting, 202                                | query independent signals, 363                   |
| imperative and functional, 381                  | result diversity, 365                            |
| limitations on new and not-yet-well-            | retrieval, 365                                   |
| understood features, 152                        | RCS (Revision Control System), 329, 332          |
| logic in, <mark>246</mark>                      | readability, 56, 62-66                           |
| reference documentation, 193                    | approval for code changes at Google, 168         |
| style guides for each language, 142             | ensuring with code reviews, 173                  |
| support for large-scale changes, 471            | readability process, 56                          |
| Project Health (pH) tool, 228                   | about, 63                                        |
| project-level customization in Tricorder, 425   | advantages of, <mark>64</mark>                   |
| Proto Best Practices analyzer, 424              | real implementations, using instead of test dou- |
| protocol buffers static analysis of, 425        | bles, 264-269                                    |
| providers, documentation for, 192               | deciding when to use real implementations,       |
| psychological benefits of code reviews, 174     | 266-269                                          |
| psychological safety, 46-48                     | dependency construction, 268                     |
| building through mentorship, 46                 | determinism in tests, 267                        |
| catalyzing your team by building, 87            | execution time, 267                              |
| in large groups, 47                             | preferring realism over isolation, 265           |
| lack of, 43                                     | recall bias, 134                                 |
| public versus private compute services, 543     | recency bias, 134                                |
| public APIs, 237                                | recognition for knowledge sharing, 57            |
| purpose of documentation years 191              | recommendations on research findings, 137        |
| purpose of documentation users, 191             | record/replay systems, 293, 492                  |
| Python, 28<br>unittest.mock framework for, 262  | redundancy in documentation, 202                 |
| Python style guides                             | refactorings, 233                                |
| avoidance of power features such as reflec-     | code reviews for, 182                            |
| tion, 149                                       | large-scale, and use of references for rank-     |
| CamelCase vs. snake_case naming, 154            | ing, 364                                         |
| indentation of the code, 149                    | search-and-replace-based, 360                    |
| indefinition of the code, 112                   | uncommitted work as akin to a branch, 337        |
| Λ                                               | reference documentation, 193-195                 |
| Q Novi 100                                      | class comments, 194                              |
| qualitative metrics, 133                        | file comments, 194                               |
| quality and user-focus in CD, 511               | function comments, 195                           |
| quality of code, 131                            | references, using for ranking, 363               |
| QUANTS in engineering productivity metrics,     | regression tests, 299                            |
| in readability process study 134                | (see also A/B diff tests)                        |
| in readability process study, 134               | regular expressions (regex) search, 368          |
| query dependent signals, 364                    | reimplementing/forking versus adding a           |
| query independent signals, 363                  | dependency, 22                                   |

| release branches, 339                                           | being consistent, 146                                      |
|-----------------------------------------------------------------|------------------------------------------------------------|
| Google and, 344                                                 | conceding to practicalities, 150                           |
| release candidate testing, 486                                  | optimizing for code reader, not the                        |
| releases                                                        | author, 144                                                |
| striving for agility, setting up a release train,               | rules must pull their weight, 144                          |
| 509                                                             | reasons for having, 142                                    |
| meeting your release deadline, 510<br>no binary is perfect, 509 | rules, defining in Bazel, 384                              |
| reliability of external dependencies, 396                       | S                                                          |
| remote caching in distributed builds, 386                       |                                                            |
| Google's remote cache, 389                                      | sampling bias, 134                                         |
| remote execution of distributed builds, 387                     | sandboxing                                                 |
| Google remote execution system, Forge, 389                      | hermetic testing and, 492                                  |
| repositories, 328                                               | use by Bazel, 384                                          |
| central repository for a project in DVCSs,                      | satisfaction (QUANTS), 131<br>scalability                  |
| 333                                                             | forking and, 22                                            |
| finer-grained vs. monorepos, 345                                |                                                            |
| repository branching, not used at Google, 223                   | of static analysis tools, 418 scale                        |
| representative testing, 512                                     |                                                            |
| resource constraints, CI and, 490                               | deciding between time and, 22 in software engineering, 4   |
| respect, 35                                                     | issues in software engineering, 5                          |
| being "Googley", 41                                             | scale and efficiency, 11-17                                |
| practicing, 36-39, 57                                           | compiler upgrade (example), 14-16                          |
| result diversity in search, 365                                 | finding problems earlier in developer work-                |
| retrieval, 365                                                  | flow, 17                                                   |
| reviewers of code, keeping to a minimum, 179                    | policies that don't scale, 12                              |
| rightsizing and autoscaling, 522                                | policies that don't scale, 12 policies that scale well, 14 |
| risks                                                           | scaling                                                    |
| making failure an option, 87                                    | enabled by consistency in the codebase, 147                |
| of working alone, 30                                            | impact of scale on Code Search design,                     |
| roadblocks, removing, 96                                        | 359-361                                                    |
| rollbacks, 181                                                  | scheduling, automated, 519, 524                            |
| Rosie tool, 470                                                 | scope of tests, 219-221, 281                               |
| sharding and submitting in LSC process,                         | defining scope for a unit, 237                             |
| 474-477                                                         | smallest possible test, 289                                |
| rules governing code, 141                                       | scoped_ptr in C++, 467                                     |
| categories of rules in style guides                             | scoring a change, 413                                      |
| rules building in consistency, 153                              | seams, 260                                                 |
| rules enforcing best practices, 152                             | search index in Code Search, 361                           |
| rules to avoid danger, 151                                      | search query latency, Code Search and, 359                 |
| topics not covered, 153                                         | security                                                   |
| changing, 154-157                                               | of external dependencies, 396                              |
| enforcing, 158-163                                              | reacting to threats and vulnerabilities, 10                |
| gofmt case study, 161-163                                       | risks introduced by external dependencies,                 |
| using code formatters, 161                                      | 385                                                        |
| using error checkers, 160                                       | seeded data, 294                                           |
| guiding principles for, 143-151                                 | seekers (of documentation), 191                            |
| avoiding error-prone and surprising                             | self-confidence, 36                                        |
| constructs, 149                                                 | self-driving team, building, 112-116                       |
|                                                                 |                                                            |

| semantic version strings, 394                   | concluding thoughts, 549-550                   |
|-------------------------------------------------|------------------------------------------------|
| semantic versioning, 440                        | deprecation and, 311                           |
| limitations of, 443-449                         | programming versus, 3, 23                      |
| Minimum Version Selection, 447                  | version control systems and, 329               |
| motivations, 446                                | scale and efficiency, 11-17                    |
| overconstrains, 444                             | time and change, 6-11                          |
| overpromising compatibility, 445                | trade-offs and costs, 18-23                    |
| questioning if it works, 448                    | software engineers                             |
| SemVer (see semantic versioning)                | code reviews and, 170                          |
| servant leadership, 85                          | offices for, <mark>32</mark>                   |
| serverless, 539-543                             | source control                                 |
| about, 540                                      | dependency management and, 430                 |
| pros and cons of, 541                           | Git as dominant system, 333                    |
| serverless frameworks, 541                      | moving documentation to, 189                   |
| trade-off, 542                                  | source of truth, 334-336                       |
| services, connecting to in software for managed | One Version as single source of truth, 340     |
| compute, 528                                    | scenario, no clear source of truth, 335        |
| serving jobs, 526                               | work in progress and branches, 336             |
| multitenancy for, 534                           | sparse n-gram solution, search index in Code   |
| shading (in Java), 342                          | Search, 362                                    |
| sharding and submitting in LSC process,         | speed in build systems, 371                    |
| 474-477                                         | speeding up tests, 305                         |
| shared environment SUT, 291                     | Spring Cloud Contracts, 293                    |
| shell scripts, using for builds, 373            | stack frames, Code Search integration in, 357  |
| shifting left, 17, 32                           | staged rollouts, 512                           |
| making data-driven decisions earlier, 512       | standardization, lack of, in larger tests, 285 |
| shipping only what gets used, 511               | state testing, 238                             |
| signals                                         | preferring over interaction testing, 275       |
| defined, 129                                    | state, managing, 527                           |
| Goals/Signals/Metrics (GSM) framework,          | state-changing functions, 277                  |
| 129                                             | static analysis, 417-428                       |
| single point of failure (SPOF), 44              | effective, characteristics of, 418-419         |
| leader as, 112                                  | scalability, 418                               |
| single-machine SUT, 291                         | usability, 418                                 |
| single-process SUT, 290                         | examples of, 417                               |
| small fixes across the codebase with LSCs, 462  | making it work, key lessons in, 419-421        |
| small tests, 216, 231, 281                      | empowering users to contribute, 420            |
| social interaction                              | focus on developer happiness, 419              |
| being "Googley", 41                             | making static analysis part of core devel-     |
| coaching a low performer, 90                    | oper workflow, 420                             |
| group interaction patterns, 47                  | Tricorder platform, 421-427                    |
| humility, respect, and trust in practice,       | analysis while editing and browsing            |
| 36-39                                           | code, 427                                      |
| pillars of, 34                                  | compiler integration, 426                      |
| why the pillars matter, 35                      | integrated feedback channels, 423              |
| social skills, 29                               | integrated tools, 422                          |
| societal costs, 18                              | per-project customization, 424                 |
| software engineering                            | presubmits, 425                                |
| clever code and, 10                             | suggested fixes, 424                           |
|                                                 |                                                |

| static analysis tools, 61                       | risks of testing in production and Webdriver  |
|-------------------------------------------------|-----------------------------------------------|
| for code correctness, 172                       | Torso, 292                                    |
| static dependency model, 439                    | scope of, test scope and, 289                 |
| std::unique_ptr in C++, 153, 468                | seeding the SUT state, 294                    |
| streetlight effect, 129                         | verification of behavior, 295                 |
| stress testing, 297                             |                                               |
| stubbing, 263, 272-275                          | T                                             |
| appropriate use of, <mark>275</mark>            | TAP (see Test Automation Platform)            |
| dangers of overusing, 273                       | task-based build systems, 376-380             |
| stumblers, documentation for, 192               | dark side of, 378                             |
| style arbiters, 156                             | difficulty maintaining and debugging build    |
| style guides for code, 59, 141                  | scripts, 379                                  |
| advantages of having rules, 142                 | difficulty of parallelizing build steps, 378  |
| applying the rules, 158-163                     | difficulty of performing incremental builds,  |
| categories of rules in, 151                     | 379                                           |
| rules building in consistency, 153              | time, scale, and trade-offs, 390              |
| rules enforcing best practices, 152             | teacher and mentor, being, 97                 |
| rules to avoid danger, 151                      | teams                                         |
| topics not covered, 153                         | anchoring a team's identity, 115              |
| changing the rules, 154-157                     | engineers and offices, opinions on, 32        |
| making exceptions to the rules, 156             | Genius Myth and, 28                           |
| process for, 155                                | leading, 81                                   |
| style arbiters, <mark>156</mark>                | (see also leading a team)                     |
| creating the rules, 143-151                     | software engineering as team endeavor,        |
| guiding principles, 143-151                     | 34-42                                         |
| for each programming language, 141              | being "Googley", 41                           |
| programming guidance, 157                       | blameless postmortem culture, 39-41           |
| substring search, 369                           | humility, respect, and trust in practice,     |
| Subversion, 332                                 | 36-39                                         |
| success, cycle of, 116                          | pillars of social interaction, 34             |
| suffix array-based solution, search index in    | why social interaction pillars matter, 35     |
| Code Search, 362                                | tech lead (TL), 82                            |
| supplemental retrieval, 365                     | tech lead manager (TLM), 82                   |
| sustainability                                  | tech talks and classes, 52                    |
| codebase, 12                                    | techie-celebrity phenomenon, 29               |
| forking and, <mark>22</mark>                    | technical reviews, 199                        |
| for software, 4                                 | technical writers, writing documentation, 204 |
| system tests, 219                               | tempo and velocity (QUANTS), 131              |
| systems under test (SUTs), 290-294              | Test Automation Platform (TAP), 223, 494-496  |
| dealing with dependent but subsidiary serv-     | culprit finding, 495                          |
| ices, 293                                       | failure management, 495                       |
| examples of, 290                                | presubmit optimization, 494                   |
| fidelity of tests to behavior of, 282           | resource constraints and, 496                 |
| in functional test of interacting binaries, 297 | testing LSC shards, 475                       |
| larger tests for, 288                           | train model and testing of LSCs, 466          |
| production vs. isolated hermetic SUTs, 305      | test data for larger tests, 294               |
| reducing size at problem testing boundaries,    | test doubles, 219, 257-280                    |
| 292                                             | at Google, 258                                |
|                                                 | example, 259                                  |
|                                                 |                                               |

| faking, 269-272                          | history at Google, 225-229                          |
|------------------------------------------|-----------------------------------------------------|
| impact on software development, 258      | contemporary testing culture, 228                   |
| interaction testing, 275-280             | orientation classes, 226                            |
| mocking frameworks, 261                  | Test Certified program, 227                         |
| seams, 260                               | Testing on the Toilet (TotT), 227                   |
| stubbing, 272-275                        | in large-scale change infrastructure, 471           |
| techniques for using, 262-264            | larger (see larger testing)                         |
| faking, 263                              | of large-scale changes, 466-468                     |
| interaction testing, 264                 | reasons for writing tests, 208-214                  |
| stubbing, <mark>263</mark>               | Google Web Server, story of, 209                    |
| unfaithful, <mark>283</mark>             | tests for fakes, 272                                |
| using in brittle interaction test, 238   | write, run, react in automating testing,            |
| using real implementations instead of,   | 212-213                                             |
| 264-269                                  | Testing on the Toilet (TotT), 227                   |
| deciding when to use real implementa-    | tests                                               |
| tion, 266-269                            | becoming brittle with overuse of stubbing,          |
| preferring realism over isolation, 265   | 273                                                 |
| test infrastructure, 255                 | becoming less effective with overuse of             |
| test instability, 491                    | stubbing, 273                                       |
| test scope (see scope of tests)          | becoming unclear with overuse of stubbing,          |
| test sizes, 215                          | 273                                                 |
| in practice, 219                         | making understandable, 307                          |
| large tests, 217, 281                    | overusing stubbing, example of, 274                 |
| medium tests, 217                        | refactoring to avoid stubbing, 274                  |
| properties common to all sizes, 218      | speeding up, 305                                    |
| small tests, 216                         | third_party directory, 437                          |
| test scope and, <mark>220</mark>         | time                                                |
| unit tests, 231                          | deciding between time and scale, 22                 |
| test suite, 208                          | in version control systems, 329                     |
| large, pitfalls of, 224                  | larger tests and passage of time, 2 <mark>86</mark> |
| test traffic, 294                        | time and change in software projects, 6-11          |
| testability                              | aiming for nothing changes, 10                      |
| testable code, 260                       | hash ordering (example), 9                          |
| writing testable code early, 261         | Hyrum's Law, 8                                      |
| testing, 207-230                         | life span of programs and, 3                        |
| as barrier to atomic changes, 465        | TL (see tech lead)                                  |
| at Google scale, 223-225                 | TLM (see tech lead manager)                         |
| automated, limits of, 229                | token-based searches, 368                           |
| automating to keep up with modern devel- | toolchains, use by Bazel, 384                       |
| opment, 210                              | Torvalds, Linus, 28                                 |
| benefits of testing code, 213-214        | traceability, maintaining for metrics, 130          |
| continuous integration and, 480          | tracking history of code changes in Critique,       |
| continuous testing in CI, 485-487        | 414                                                 |
| designing a test suite, 214-223          | tracking systems for work, 119                      |
| Beyoncé Rule, 221                        | trade-offs                                          |
| code coverage, 222                       | cost/benefit, 18-23                                 |
| test scope, 219-221                      | deciding between time and scale (exam-              |
| test size, 215                           | ple), 22                                            |
| hermetic, 491                            | distributed builds (example), 20                    |

| mistakes in decision making, 22                                | unchanging tests, 233                                         |
|----------------------------------------------------------------|---------------------------------------------------------------|
| whiteboard markers (example), 19                               | unit testing, 231-256                                         |
| for leaders, 109                                               | common gaps in unit tests, 283-284                            |
| in engineering productivity, 130                               | configuration issues, 283                                     |
| in Web Search latency case study, 111<br>key, identifying, 109 | emergent behaviors and the vacuum<br>effect, <mark>284</mark> |
| transitive dependencies, 392                                   | issues arising under load, 284                                |
| external, 395                                                  | unanticipated behaviors, inputs, and side                     |
| strict, enforcing, 393                                         | effects, 284                                                  |
| tribal knowledge, 45                                           | unfaithful test doubles, 283                                  |
| Tricorder static analysis platform, 322, 421-427               | execution time for tests, 267                                 |
| analysis while editing and browsing code,                      | lifespan of software tested, 286                              |
| 427                                                            | limitations of unit tests, 282                                |
| compiler integration, 426                                      | maintainability of tests, importance of, 232                  |
| criteria for new checks, 422                                   | narrow-scoped tests (or unit tests), 219                      |
| integrated feedback channels, 423                              | preventing brittle tests, 233-239                             |
| integrated tools, 422                                          | properties of good unit tests, 285                            |
| per-project customization, 424                                 | tests and code sharing, DAMP, not DRY,                        |
| presubmit checks, 425                                          | 248-255                                                       |
| suggested fixes, 424                                           | DAMP test, 250                                                |
| trigram-based approach, search index in Code                   | defining test infrastructure, 255                             |
| Search, 361                                                    | shared helpers and validation, 254                            |
| trunk-based development, 327, 339                              | shared setup, 253                                             |
| correlation with good technical outcomes,                      | shared values, 251                                            |
| 339                                                            | writing clear tests, 239-248                                  |
| Live at Head model and, 442                                    | leaving logic out of tests, 246                               |
| predictive relationship between high-                          | making tests complete and concise, 240                        |
| performing organizations and, 343                              | testing behaviors, not methods, 241-246                       |
| source control questions and, 429                              | writing clear failure messages, 247                           |
| trust, 35                                                      | units (in unit testing), 237                                  |
| being "Googley", 41                                            | Unix, developers of, 28                                       |
| code reviews and, 400                                          | unreproducable builds, 385                                    |
| practicing, 36-39                                              | upgrades, 4                                                   |
| treating your team like children (antipat-                     | compiler upgrade example, 14-16                               |
| tern), 92                                                      | life span of software projects and impor-                     |
| trusting your team and losing the ego, 93                      | tance of, 6                                                   |
| vulnerability and, 40                                          | usability of static analyses, 418                             |
| Truth assertion library, 248                                   | user evaluation tests, 303                                    |
| tutorials, 196                                                 | user focus in CD, shipping only what gets used,               |
| example of a bad tutorial, 196                                 | 511                                                           |
| example, bad tutorial made better, 197                         | users                                                         |
|                                                                | engineers building software for all users, 72                 |
| U                                                              | focusing first on users most impacted by                      |
| UAT (user acceptance testing), 301                             | bias and discrimination, 78                                   |
| UIs                                                            | relegating consideration of user groups to                    |
| end-to-end tests of service UI to its back-                    | late in development, 76                                       |
| end, 292                                                       |                                                               |
| in example of fairly small SUT, 288                            | V                                                             |
| tests for, unreliable and costly, 292                          | vacuum effect, unit tests and, 284                            |
| •                                                              |                                                               |

| validation, shared helpers and, 254           | for isolation in multitenant compute serv-       |
|-----------------------------------------------|--------------------------------------------------|
| values versus outcomes in equitable engineer- | ices, 521                                        |
| ing, 77                                       | virtual monorepos (VMRs), 346, 347               |
| Van Rossum, Guido, 28                         | visibility, minimizing for modules in build sys- |
| VCSs (version control systems), 327           | tems, 392                                        |
| (see also version control)                    | vulnerability, showing, 40                       |
| blending between fine-grained repositories    |                                                  |
| and monorepos, 346                            | W                                                |
| early, 329                                    | Web Search latency case study, 110-112           |
| velocity is a team sport, 507                 | Webdriver Torso incident, 292                    |
| vendoring your project's dependencies, 396    | well-specified interaction tests, 279            |
| version control, 327-336                      | who, what, when, where, and why questions,       |
| about, 328                                    | answering in documentation, 201                  |
| at Google, 340-345                            | workspaces                                       |
| few long-lived branches, 343                  | differences from the global repository, 368      |
| One-Version Rule, 340, 342                    | local, Code Search support for, 362              |
| release branches, 344                         | tight integration between Critique and, 406      |
| scenario, multiple available versions, 341    | writing reviews (for technical documents), 199   |
| branch management, 336-339                    |                                                  |
| centralized vs. distributed VCSs, 331-334     | γ                                                |
| versus dependency management, 336             |                                                  |
| future of, 346                                | YAQS ("Yet Another Question System"), 51         |
| importance of, 329-331                        | -                                                |
| monorepos, 345                                | Z                                                |
| source of truth, 334-336                      | Zen master, being, 94                            |
| virtual machines (VMs), 524                   |                                                  |

## About the Authors

Titus Winters is a Senior Staff Software Engineer at Google, where he has worked since 2010. Today, he is the chair of the global subcommittee for the design of the C++ standard library. At Google, he is the library lead for Google's C++ codebase: 250 million lines of code that will be edited by 12,000 distinct engineers in a month. For the last seven years, Titus and his teams have been organizing, maintaining, and evolving the foundational components of Google's C++ codebase using modern automation and tooling. Along the way, he has started several Google projects that are believed to be in the top-10 largest refactorings in human history. As a direct result of helping to build out refactoring tooling and automation, Titus has encountered first-hand a huge swath of the shortcuts that engineers and programmers may take to "just get something working." That unique scale and perspective has informed all of his thinking on the care and feeding of software systems.

Tom Manshreck is a Staff Technical Writer within Software Engineering at Google since 2005, responsible for developing and maintaining many of Google's core programming guides in infrastructure and language. Since 2011, he has been a member of Google's C++ Library Team, developing Google's C++ documentation set, launching (with Titus Winters) Google's C++ training classes, and documenting Abseil, Google's open source C++ code. Tom holds a BS in Political Science and a BS in History from the Massachusetts Institute of Technology. Before Google, Tom worked as a Managing Editor at Pearson/Prentice Hall and various startups.

Hyrum Wright is a Staff Software Engineer at Google, where he has worked since 2012, mainly in the areas of large-scale maintenance of Google's C++ codebase. Hyrum has made more individual edits to Google's codebase than any other engineer in the history of the company, and leads Google's automated change tooling group. Hyrum received a PhD in Software Engineering from the University of Texas at Austin and also holds an MS from the University of Texas and a BS from Brigham Young University, and is an occasional visiting faculty member at Carnegie Mellon University. He is an active speaker at conferences and contributor to the academic literature on software maintenance and evolution.
