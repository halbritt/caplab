# index

<span id="page-296-0"></span>
## A AAA (arrange, act, and assert) pattern 42–49 avoiding if statements 44–45 avoiding multiple AAA sections 43–44 differentiating system under test 47–48 dropping AAA comments 48–49 overview 42–43 reusing code in test sections 246–252 in act sections 249–250 in arrange sections 246–249 in assert sections 250 section size 45–47 arrange section 45 number of assertions in assert section 47 sections larger than a single line 45–47 teardown phase 47 abstractions 198, 260 Active Record pattern 159 adapters 227 aggregates 157 ambient context 212 anti-patterns 212 code pollution 266–268 exposing private state 263–264 leaking domain knowledge to tests 264–266 mocking concrete classes 268–271 private methods 260–263 acceptability of testing 261–263 insufficient coverage 260–261 test fragility 260 time 271–273 as ambient context 271–272 as explicit dependency 272–273 API (application programming interface) 104, 111, 133, 191, 195, 227, 264 missing abstractions 260 public vs. private 99 well-designed 100–101, 105, 108, 262 application behavior 57 application services layer 133–134 arrange, act, and assert pattern. *See* AAA pattern assertion libraries, using to improve test readability 62–63 assertion-free testing 12–13 asynchronous communications 191 atomic updates 236 automation concepts 87–90 black-box vs. white-box testing 89–90 Test Pyramid 87–89 B backward migration 233 bad tests 189 black-box testing 68, 89–90 Boolean switches 266–268 branch coverage metric 10–11 brittle tests 83–84, 116, 216 brittleness 86, 125 bugs 68, 79, 104, 175, 189 business logic 106–107, 156, 169, 179 C CanExecute/Execute pattern 172, 174 CAP theorem 86–87 captured data 208

| circular dependencies 203                                      | CQS (command query separation) principle             |
|----------------------------------------------------------------|------------------------------------------------------|
| defined 202                                                    | 97–98                                                |
| eliminating 202–204                                            | CRUD (create, read, update, and delete)              |
| classical school of unit testing 30–37                         | operations 89                                        |
| dependencies 30–34                                             | CSV files 208–209                                    |
| end-to-end tests 38–39                                         | cyclic dependency 202                                |
| integration tests 37–39                                        | cyclomatic complexity 152                            |
| isolation issue 27–30                                          |                                                      |
| mocks 114–116                                                  | D                                                    |
| mocking out out-of-process dependencies                        |                                                      |
| 115–116                                                        | data inconsistencies 241                             |
| using mocks to verify behavior 116                             | data mapping 254                                     |
| precise bug location 36                                        | data motion 234                                      |
| testing large graph of interconnected classes 35               | data, bundling 104                                   |
| testing one class at a time 34–35                              | database backup, restoring 244                       |
| cleanup phase 244                                              | database management system (DBMS) 246                |
| clusters, grouping into aggregates 157                         | database testing                                     |
| code complexity 104, 152                                       | common questions 252–255                             |
| code coverage metric 9–10                                      | testing reads 252–253                                |
| code coverage tools 90                                         | testing repositories 253–254                         |
| code depth 157                                                 | database transaction management 234–243              |
| code pollution 127, 266–268, 272                               | in integration tests 242–243                         |
| code width 157                                                 | in production code 235–242                           |
| collaborators 32, 148, 153                                     | prerequisites for 230–234                            |
| command query separation. See CQS principle<br>commands 97     | keeping database in source control<br>system 230–231 |
| communication-based testing 122–123, 128<br>feedback speed 124 | reference data as part of database<br>schema 231     |
| maintainability 127                                            | separate instances for every developer               |
| overuse of 124                                                 | 232                                                  |
| protection against regressions and feedback                    | state-based vs. migration-based database             |
| speed 124                                                      | delivery 232–234                                     |
| resistance to refactoring 124–125                              | reusing code in test sections 246–252                |
| vulnerability to false alarms 124                              | creating too many database                           |
| communications                                                 | transactions 251–252                                 |
| between applications 107, 110                                  | in act sections 249–250                              |
| between classes in application 110, 116                        | in arrange sections 246–249                          |
| conditional logic 169–180                                      | in assert sections 250                               |
| CanExecute/Execute pattern 172–174                             | test data life cycle 243–246                         |
| domain events for tracking changes in the                      | avoiding in-memory databases 246                     |
| domain model 175–178                                           | clearing data between test runs 244–245              |
| constructors, reusing test fixtures between                    | parallel vs. sequential test execution               |
| tests 52                                                       | 243–244                                              |
| containers 244                                                 | database transaction management 234–243              |
| controllers 153, 225                                           | in integration tests 242–243                         |
| simplicity 171                                                 | in production code 235–242                           |
| coverage metrics, measuring test suite quality<br>with 8–15    | separating connections from transactions<br>236–239  |
| aiming for particular coverage number 15                       | upgrading transaction to unit of work                |
| branch coverage metric 10–11                                   | 239–242                                              |
| code coverage metric 9–10                                      | database transactions 244                            |
| problems with 12–15                                            | daysFromNow parameter 60                             |
| code paths in external libraries 14–15                         | DBMS (database management system) 246                |
| impossible to verify all possible outcomes                     | dead code 260                                        |
| 12–13                                                          | deliveryDate parameter 62                            |

| dependencies 28–29, 35                                                              | Fluent Assertions 62                                                  |
|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| classical school of unit testing 30–34                                              | fragile tests 96, 113                                                 |
| London school of unit testing 30–34                                                 | frameworks 81                                                         |
| out-of-process 161, 190                                                             | functional architecture 128–134                                       |
| shared 29, 31                                                                       | defined 132–133                                                       |
| types of 115                                                                        | drawbacks of 146–149                                                  |
| Detroit approach, unit testing 21<br>diagnostic logging 206, 212                    | applicability of 147–148<br>code base size increases 149              |
| discovered abstractions 198                                                         | performance drawbacks 148                                             |
| Docker container 28                                                                 | functional programming 128–131                                        |
| domain events, tracking changes in domain                                           | hexagonal architecture 133–134                                        |
| model 175–178                                                                       | transitioning to output-based testing 135–146                         |
| domain layers 106–107, 109, 133–134                                                 | audit system 135–137                                                  |
| domain model 16, 153, 225                                                           | refactoring toward functional                                         |
| connecting with external applications 111                                           | architecture 140–145                                                  |
| testability 171                                                                     | using mocks to decouple tests from                                    |
| domain significance 153                                                             | filesystem 137–140                                                    |
| dummy test double 93–94                                                             | functional core 132–133, 143–144, 156<br>functional programming 121   |
| E                                                                                   | functional testing 38, 121, 128                                       |
|                                                                                     |                                                                       |
| EasyMock 25                                                                         | G                                                                     |
| edge cases 187, 189, 194                                                            |                                                                       |
| encapsulation 46, 252                                                               | Git 230–231                                                           |
| end-to-end tests 88–89, 195–196, 205, 222<br>classical school of unit testing 38–39 | Given-When-Then pattern 43<br>GUI (graphical user interface) tests 38 |
| London school of unit testing 38–39                                                 |                                                                       |
| possibility of creating ideal tests 81                                              | H                                                                     |
| enterprise applications 5                                                           |                                                                       |
| Entity Framework 240–242, 255                                                       | handwritten mocks 94, 222                                             |
| entropy 6                                                                           | happy paths 187, 194, 239                                             |
| error handling 146                                                                  | helper methods 126–127                                                |
| exceptions 130<br>expected parameter 62                                             | hexagonal architecture 106–107, 128, 156<br>defining 106–110          |
| explicit inputs and outputs 130                                                     | functional architecture 133–134                                       |
| external libraries 81                                                               | purpose of 107                                                        |
| external reads 170–171, 173                                                         | hexagons 106, 108, 134                                                |
| external state 130                                                                  | hidden outputs 131                                                    |
| external writes 170–171, 173                                                        | high coupling, reusing test fixtures between                          |
|                                                                                     | tests 52                                                              |
| F                                                                                   | HTML tags 72                                                          |
| Fail Fast principle 185, 189                                                        | humble controller 160<br>Humble Object pattern 155, 157–158, 167, 271 |
| failing preconditions 190                                                           | humble objects 157                                                    |
| fake dependencies 93                                                                | humble wrappers 155                                                   |
| fake test double 93–94                                                              |                                                                       |
| false negatives 76–77                                                               | I                                                                     |
| false positives 69–70, 77, 82, 86, 96, 99, 124                                      |                                                                       |
|                                                                                     |                                                                       |
| causes of 71–74                                                                     | ideal tests 80–87                                                     |
| importance of 78–79                                                                 | brittle tests 83–84                                                   |
| fast feedback 81–86, 88, 99, 123, 252, 260                                          | end-to-end tests 81                                                   |
| fat controllers 154                                                                 | possibility of creating 81                                            |
| feedback loop, shortening 189<br>feedback speed 79–80, 124                          | trivial tests 82–83<br>if statements 10–11, 44–45, 143, 152, 173–174  |

immutability [133](012-chapter-6-styles-of-unit-testing.md#page-154-7)

fixed state [50](008-chapter-3-the-anatomy-of-a-unit-test.md#page-71-1)

| immutable classes 133<br>immutable core 132, 134<br>immutable events 176                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | invariants 100, 103<br>isolation issue<br>classical school of unit testing 27–30<br>London school of unit testing 21–27<br>isSuccess flag 113           |  |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| immutable objects 30, 132<br>implementation details 99–105                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                         |  |
| incoming interactions 94–95<br>infrastructure code 16                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | J                                                                                                                                                       |  |
| infrastructure layer 202<br>in-memory databases 246<br>in-process dependencies 199–200<br>INSERT statements 231<br>integer type 14<br>integration testing<br>best practices 200–205<br>eliminating circular dependencies                                                                                                                                                                                                                                                                                                                                            | JMock 25<br>JSON files 208–209                                                                                                                          |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | L                                                                                                                                                       |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | logging functionality testing 205–213<br>amount of logging 212                                                                                          |  |
| 202–204<br>making domain model boundaries<br>explicit 200                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | introducing wrapper on top of ILogger<br>207–208<br>passing around logger instances 212–213                                                             |  |
| multiple act sections 204–205<br>reducing number of layers 200–202<br>classical school of unit testing 37–39<br>database transaction management in<br>242–243<br>defined 186–190<br>example of 193–197<br>categorizing database and message bus 195<br>end-to-end testing 195–196<br>first version 196–197<br>scenarios 194<br>failing fast 188–190<br>interfaces for abstracting dependencies<br>197–200<br>in-process dependencies 199–200<br>loose coupling and 198<br>out-of-process dependencies 199<br>logging functionality 205–213<br>amount of logging 212 | structured logging 208–209<br>whether to test or not 205–206<br>writing tests for support and diagnostic                                                |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | logging 209–211<br>London school of unit testing 30–37                                                                                                  |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | dependencies 30–34<br>end-to-end tests 38–39<br>integration tests 37–39<br>isolation issue 21–27<br>mocks 114–116                                       |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | mocking out out-of-process dependencies<br>115–116                                                                                                      |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | using mocks to verify behavior 116<br>precise bug location 36                                                                                           |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | testing large graph of interconnected classes 35<br>testing one class at a time 34–35<br>loose coupling, interfaces for abstracting depen               |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | dencies and 198                                                                                                                                         |  |
| introducing wrapper on top of ILogger<br>207–208                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | M                                                                                                                                                       |  |
| passing around logger instances 212–213<br>structured logging 208–209<br>whether to test or not 205–206<br>writing tests for support and diagnostic<br>logging 209–211<br>London school of unit testing 37–39<br>out-of-process dependencies 190–193<br>types of 190–191<br>when real databases are unavailable<br>192–193<br>working with both 191–192<br>role of 186–187<br>Test Pyramid 187                                                                                                                                                                      | maintainability 79–80, 85, 88, 99, 137, 148,<br>252, 260<br>comparing testing styles 125–127<br>communication-based tests 127<br>output-based tests 125 |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | state-based tests 125–127<br>managed dependencies 190, 192, 246<br>mathematical functions 128–131                                                       |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | merging domain events 177<br>message bus 190–192, 199, 220, 224<br>method signatures 128                                                                |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | method under test (MUT) 25<br>Microsoft MSTest 49                                                                                                       |  |
| interconnected classes 34                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | migration-based database delivery 232–234                                                                                                               |  |
| internal keyword 99<br>invariant violations 46, 103                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | missing abstractions 260<br>mock chains 127                                                                                                             |  |

| mocking frameworks 25                             | NuGet package 49                                          |
|---------------------------------------------------|-----------------------------------------------------------|
| mockist style, unit testing 21                    | NUnit 49, 51                                              |
| Mockito 25                                        |                                                           |
| mocks 25, 254                                     | O                                                         |
| best practices 225–227                            |                                                           |
| for integration tests only 225                    | object graphs 22–23                                       |
| not just one mock per test 225–226                | Object Mother 248                                         |
| only mock types that you own 227                  | object-oriented programming (OOP) 63, 133                 |
| verifying number of calls 226                     | object-relational mapping (ORM) 163, 177,                 |
| decoupling tests from filesystem 137–140          | 227, 240, 243, 254–255, 263                               |
| defined 25                                        | observable behavior 99, 105, 108, 115, 263                |
| London school vs. classical school 114–116        | leaking implementation details 100–105                    |
| mocking out out-of-process                        | public API 99–100                                         |
| dependencies 115–116                              | well-designed API and encapsulation 103–104               |
| using mocks to verify behavior 116                | OCP (Open-Closed principle) 198                           |
| maximizing value of 217–225                       | OOP (object-oriented programming) 63, 133                 |
| IDomainLogger 224–225                             | Open-Closed principle (OCP) 198                           |
| replacing mocks with spies 222–224                | operations 99, 104                                        |
| verifying interactions at system edges<br>219–222 | orchestration, separating business logic from<br>169, 179 |
| mocking concrete classes 268–271                  | ORM (object-relational mapping) 163, 177,                 |
| observable behavior vs. implementation            | 227, 240, 243, 254–255, 263                               |
| details 99–105                                    | outcoming interactions 94–95                              |
| leaking implementation details 100–105            | out-of-process collaborators 159–160                      |
| observable behavior vs. public API 99–100         | out-of-process dependencies 28, 33, 38–39,                |
| well-designed API and encapsulation               | 115, 125, 148, 160–161, 167, 170, 176,                    |
| 103–104                                           | 186, 200, 229                                             |
| stubs 93–98                                       | integration testing 190–193                               |
| asserting interactions with stubs 96–97           | interfaces for abstracting dependencies 199               |
| commands and queries 97–98                        | types of 190–191                                          |
| mock (tool) vs. mock (test double) 94–95          | when real databases are unavailable                       |
| types of test doubles 93–94                       | 192–193                                                   |
| using mocks and stubs together 97                 | working with both 191–192                                 |
| test doubles 25                                   | output value 121                                          |
| test fragility 106–114                            | output-based testing 120–121, 124, 128                    |
| defining hexagonal architecture 106–110           | feedback speed 124                                        |
| intra-system vs. inter-system                     | maintainability 125                                       |
| communications 110–114                            | protection against regressions and feedback               |
| model database 230                                | speed 124                                                 |
| Model-View-Controller (MVC) pattern 157           | resistance to refactoring 124–125                         |
| Moq 25, 95, 226<br>MSTest 49                      | transitioning to functional architecture<br>and 135–146   |
| MUT (method under test) 25                        | audit system 135–137                                      |
| mutable objects 132                               | refactoring toward functional                             |
| mutable shell 132–133, 143–144                    | architecture 140–145                                      |
| MVC (Model-View-Controller) pattern 157           | using mocks to decouple tests from<br>filesystem 137–140  |
| N                                                 | overcomplicated code 154                                  |
|                                                   | overspecification 96                                      |
| naming tests 54–58                                |                                                           |
| guidelines for 56                                 | P                                                         |
| renaming tests to meet guidelines 56–58           |                                                           |
| NHibernate 240                                    | parallel test execution 243–244                           |

parameterized tests [59](008-chapter-3-the-anatomy-of-a-unit-test.md#page-80-0), [61](008-chapter-3-the-anatomy-of-a-unit-test.md#page-82-0) partition tolerance [86](010-chapter-4-the-four-pillars-of-a-good-unit-test.md#page-107-4)

noise, reducing [78](010-chapter-4-the-four-pillars-of-a-good-unit-test.md#page-99-2) NSubstitute [25](007-chapter-2-what-is-a-unit-test.md#page-46-9)

| performance 171                                   | toward valuable unit tests 158–167                            |
|---------------------------------------------------|---------------------------------------------------------------|
| persistence state 189                             | application services layer 160–162                            |
| preconditions 190                                 | Company class 164–167                                         |
| private APIs 99                                   | customer management system 158–160                            |
| private constructors 263                          | making implicit dependencies explicit 160                     |
| private dependencies 28–29, 31, 115               | removing complexity from application                          |
| private keyword 99                                | service 163–164                                               |
| private methods 260–263                           | reference data 231, 234, 245                                  |
| acceptability of testing 261–263                  | referential transparency 130                                  |
| insufficient coverage and 260–261                 | regression errors 8, 69, 82                                   |
| reusing test fixtures between tests 52–54         | regressions 7, 229                                            |
| test fragility and 260                            | repositories 236–237, 241, 253                                |
| Product array 129                                 | resistance to refactoring 69–71, 79–81, 83–85,                |
| production code 8                                 | 88–90, 92–93, 99, 123, 260, 265                               |
| protection against regressions 68–69, 81, 84–86,  | comparing testing styles 124–125                              |
| 88, 99, 260                                       | importance of false positives and false                       |
| comparing testing styles 124                      | negatives 78–79                                               |
| importance of false positives and false           | maximizing test accuracy 76–78                                |
| negatives 78–79                                   | return statement 10                                           |
| maximizing test accuracy 76–78                    | return true statement 10                                      |
| Public API 99, 109                                | reusability 53                                                |
| pure functions 128                                |                                                               |
|                                                   | S                                                             |
| Q                                                 |                                                               |
|                                                   | scalability 7                                                 |
| queries 97                                        | sequential test execution 243–244                             |
|                                                   | shallowness 124–125                                           |
| R                                                 | shared dependencies 28–29, 31, 33, 115, 148, 246              |
|                                                   | side effects 130–134, 190                                     |
| random number generators 29                       | signal-to-noise ratio 212                                     |
| read operations 252                               | Single Responsibility principle 157, 268, 270                 |
| readability 53                                    | single-line act section 45                                    |
| read-decide-act approach 148                      | SMTP service 110, 112–115, 134, 190                           |
| refactoring 165                                   | software bugs 7, 68                                           |
| analysis of optimal test coverage 167–169         | software entropy 6                                            |
| testing domain layer and utility code 167–168     | source of truth 231                                           |
| testing from other three quadrants 168            | spies 94, 222–224                                             |
| testing preconditions 169                         | spy test double 93                                            |
| conditional logic in controllers 169–180          | SQL scripts 231–232, 240, 245                                 |
| CanExecute/Execute pattern 172–174                | SQLite 246                                                    |
| domain events for tracking changes in the         | state 99, 101                                                 |
| domain model 175–178                              | state verification 125                                        |
| identifying code to refactor 152–158              | state-based database delivery 232                             |
| four types of code 152–155                        | state-based testing 120–122, 124, 128, 135                    |
| Humble Object pattern for splitting overcom       | feedback speed 124                                            |
| plicated code 155–158<br>resistance to 69–71      | maintainability 125–127                                       |
| comparing testing styles 124–125                  | protection against regressions and feedback<br>speed 124      |
| importance of false positives and false           | resistance to refactoring 124–125                             |
|                                                   |                                                               |
| negatives 78–79<br>maximizing test accuracy 76–78 | stubs, mocks 93–98<br>asserting interactions with stubs 96–97 |
| to parameterized tests                            | commands and queries 97–98                                    |
| general discussion 58–62                          | mock (tool) vs. mock (test double) 94–95                      |
| generating data for parameterized tests           | types of test doubles 93–94                                   |
| 60–62                                             | using mocks and stubs together 97                             |
|                                                   |                                                               |

| sub-renderers collection 105                   | tight coupling 5                                |
|------------------------------------------------|-------------------------------------------------|
| support logging 206, 212                       | time 271–273                                    |
| sustainability 7                               | as ambient context 271–272                      |
| sustainable growth 6                           | as explicit dependency 272–273                  |
| SUT (system under test) 24–25, 29, 36–37, 43,  | trivial code 153–154                            |
| 45, 47–48, 57, 71, 73–75, 84, 93–94, 96–97,    | trivial tests 82–83                             |
| 120–121, 123, 153, 244, 264, 266               | true negative 76                                |
| switch statement 10                            | true positive 76                                |
| synchronous communications 191                 | two-line act section 46                         |
| system leaks 100                               |                                                 |
|                                                | U                                               |
| T                                              |                                                 |
|                                                | UI (user interface) tests 38                    |
| tables 191                                     | unit of behavior 56, 225                        |
| tautology tests 82                             | unit of work 239, 242                           |
| TDD (test-driven development) 36, 43           | unit testing                                    |
| tell-don't-ask principle 104                   | anatomy of 41–63                                |
| test code 8                                    | AAA pattern 42–49                               |
| test coverage 9                                | assertion libraries, using to improve test      |
| Test Data Builder 248                          | readability 62–63                               |
| test data life cycle 243–246                   | naming tests 54–58                              |
| avoiding in-memory databases 246               | refactoring to parameterized tests 58–62        |
| clearing data between test runs 244–245        | reusing test fixtures between tests 50–54       |
| parallel vs. sequential test execution         | xUnit testing framework 49–50                   |
| 243–244                                        | automation concepts 87–90                       |
| test doubles 22–23, 25, 28, 93–94, 98, 199     | black-box vs. white-box testing 89–90           |
| test fixtures 248                              | Test Pyramid 87–89                              |
| defined 50                                     | characteristics of successful test suites 15–17 |
| reusing between tests                          | integration into development cycle 16           |
| constructors 52                                | maximum value with minimum maintenance          |
| high coupling 52                               | costs 17                                        |
| private factory methods 52–54                  | targeting most important parts of code          |
| reusing between tests 50–54                    | base 16–17                                      |
| test fragility, mocks and 106–114              | classical school of 30–37                       |
| defining hexagonal architecture 106–110        | dependencies 30–34                              |
| intra-system vs. inter-system                  | end-to-end tests 38–39                          |
| communications 110–114                         | integration tests 37–39                         |
| test isolation 115                             | isolation issue 27–30                           |
| Test Pyramid                                   | precise bug location 36                         |
| general discussion 87–89                       | testing large graph of interconnected           |
| integration testing 187                        | classes 35                                      |
| test suites                                    | testing one class at a time 34–35               |
| characteristics of successful suites 15–17     | coverage metrics, measuring test suite quality  |
| integration into development cycle 16          | with 8–15                                       |
| maximum value with minimum maintenance         | aiming for particular coverage number 15        |
| costs 17                                       | branch coverage metric 10–11                    |
| targeting most important parts of code         | code coverage metric 9–10                       |
| base 16–17                                     | problems with 12–15                             |
| coverage metrics, measuring test suite quality | current state of 4–5                            |
| with 8–15                                      | defined 21–30                                   |
| aiming for particular coverage number 15       | four pillars of 68–80                           |
| branch coverage metric 10–11                   | feedback speed 79–80                            |
| code coverage metric 9–10                      | maintainability 79–80                           |
| problems with 12–15                            | protection against regressions 68–69            |
| third-party applications 81, 112               | resistance to refactoring 69–71                 |

| unit testing (continued)<br>functional architecture 128–134<br>defined 132–133<br>drawbacks of 146–149<br>functional programming 128–131<br>hexagonal architecture 133–134<br>transitioning to output-based testing<br>135–146<br>goal of 5–8 | output-based testing 120–121<br>state-based testing 121–122<br>units of behavior 34<br>units of code 21, 27–29, 34, 47, 225<br>unmanaged dependencies 190, 199, 211, 216,<br>218, 220, 222, 226, 254<br>user controller 193<br>user interface (UI) tests 38 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| good vs. bad tests 7–8                                                                                                                                                                                                                        | V                                                                                                                                                                                                                                                           |
| ideal tests 80–87                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                             |
| brittle tests 83–84                                                                                                                                                                                                                           | value objects 31, 126–127                                                                                                                                                                                                                                   |
| end-to-end tests 81                                                                                                                                                                                                                           | void type 97                                                                                                                                                                                                                                                |
| possibility of creating 81                                                                                                                                                                                                                    | volatile dependencies 29                                                                                                                                                                                                                                    |
| trivial tests 82–83                                                                                                                                                                                                                           |                                                                                                                                                                                                                                                             |
| London school of 30–37                                                                                                                                                                                                                        | W                                                                                                                                                                                                                                                           |
| dependencies 30–34                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                             |
| end-to-end tests 38–39                                                                                                                                                                                                                        | white-box testing 89–90                                                                                                                                                                                                                                     |
| integration tests 37–39                                                                                                                                                                                                                       | write operation 252                                                                                                                                                                                                                                         |
| isolation issue 21–27                                                                                                                                                                                                                         |                                                                                                                                                                                                                                                             |
| precise bug location 36                                                                                                                                                                                                                       | X                                                                                                                                                                                                                                                           |
| testing large graph of interconnected                                                                                                                                                                                                         |                                                                                                                                                                                                                                                             |
| classes 35                                                                                                                                                                                                                                    | xUnit testing framework 49–50                                                                                                                                                                                                                               |
| testing one class at a time 34–35                                                                                                                                                                                                             |                                                                                                                                                                                                                                                             |
| styles of 120–123                                                                                                                                                                                                                             | Y                                                                                                                                                                                                                                                           |
| communication-based testing                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                             |
| 122–123                                                                                                                                                                                                                                       | YAGNI (You aren't gonna need it) principle                                                                                                                                                                                                                  |
| comparing 123–128                                                                                                                                                                                                                             | 198–199                                                                                                                                                                                                                                                     |

## Vladimir Khorikov Unit Testing Principles, Practices, and Patterns

G reat testing practices will help maximize your project quality and delivery speed. Wrong tests will break your code, multiply bugs, and increase time and costs. You owe it to yourself—and your projects—to learn how to do excellent unit testing to increase your productivity and the end-to-end quality of your software.

Unit Testing: Principles, Practices, and Patterns teaches you to design and write tests that target the domain model and other key areas of your code base. In this clearly written guide, you learn to develop professional-quality test suites, safely automate your testing process, and integrate testing throughout the application life cycle. As you adopt a testing mindset, you'll be amazed at how better tests cause you to write better code.

## What's Inside

- Universal guidelines to assess any unit test
- Testing to identify and avoid anti-patterns
- Refactoring tests along with the production code
- Using integration tests to verify the whole system

For readers who know the basics of unit testing. The C# examples apply to any language.

Vladimir Khorikov is an author, blogger, and Microsoft MVP. He has mentored numerous teams on the ins and outs of unit testing.

To download their free eBook in PDF, ePub, and Kindle formats, owners of this book should visit www.manning.com/books/unit-testing

![](../assets/_page_304_Picture_12.jpeg)

"This book is an indispensable resource. "

—Greg Wright Kainos Software Ltd.

"Serves as a valuable and humbling encouragement to double down and test well, something we need no matter how experienced we may be. "

—Mark Nenadov, BorderConnect

"I wish I had this book twenty years ago when I was starting my career in software development. "

—Conor Redmond Incomm Product Control

"This is the kind of book on unit testing I have been waiting on for a long time. "

—Jeremy Lange, G2

ISBN-13: 978-1-61729-627-7 ISBN-10: 1-61729-627-9

![](../assets/_page_304_Picture_22.jpeg)

![](../assets/_page_304_Picture_23.jpeg)
