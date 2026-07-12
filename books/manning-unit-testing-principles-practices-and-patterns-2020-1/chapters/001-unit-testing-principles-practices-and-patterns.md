![](../assets/_page_0_Figure_0.jpeg)

*Chapter Map*

![](../assets/_page_1_Figure_1.jpeg)

# Unit Testing: Principles, Practices, and Patterns

VLADIMIR KHORIKOV

![](../assets/_page_2_Picture_2.jpeg)

For online information and ordering of this and other Manning books, please visit <www.manning.com>. The publisher offers discounts on this book when ordered in quantity. For more information, please contact

Special Sales Department Manning Publications Co. 20 Baldwin Road PO Box 761 Shelter Island, NY 11964 Email: orders@manning.com

©2020 by Manning Publications Co. All rights reserved.

No part of this publication may be reproduced, stored in a retrieval system, or transmitted, in any form or by means electronic, mechanical, photocopying, or otherwise, without prior written permission of the publisher.

Many of the designations used by manufacturers and sellers to distinguish their products are claimed as trademarks. Where those designations appear in the book, and Manning Publications was aware of a trademark claim, the designations have been printed in initial caps or all caps.

Recognizing the importance of preserving what has been written, it is Manning's policy to have the books we publish printed on acid-free paper, and we exert our best efforts to that end. Recognizing also our responsibility to conserve the resources of our planet, Manning books are printed on paper that is at least 15 percent recycled and processed without the use of elemental chlorine.

Manning Publications Co. Acquisitions editor: Mike Stephens 20 Baldwin Road Development editor: Marina Michaels PO Box 761 Technical development editor: Sam Zaydel

Shelter Island, NY 11964 Review editor: Aleksandar Dragosavljevic´

Production editor: Anthony Calcara Copy editor: Tiffany Taylor ESL copyeditor: Frances Buran Proofreader: Keri Hales

Technical proofreader: Alessandro Campeis

Typesetter: Dennis Dalinnik Cover designer: Marija Tudor

ISBN: 9781617296277

Printed in the United States of America

![](../assets/_page_4_Picture_0.jpeg)

## brief contents

| PART 1 | THE<br>PICTURE1<br>BIGGER                               |
|--------|---------------------------------------------------------|
|        | 1<br>The goal of unit testing<br>3<br>■                 |
|        | 2<br>What is a unit test?<br>20<br>■                    |
|        | 3<br>The anatomy of a unit test<br>41<br>■              |
| PART 2 | MAKING<br>YOU65<br>YOUR<br>TESTS<br>WORK<br>FOR         |
|        | 4<br>The four pillars of a good unit test<br>67<br>■    |
|        | 5<br>Mocks and test fragility<br>92<br>■                |
|        | 6<br>Styles of unit testing<br>119<br>■                 |
|        | 7<br>Refactoring toward valuable unit tests<br>151<br>■ |
| PART 3 | INTEGRATION<br>TESTING183                               |
|        | 8<br>Why integration testing?<br>185<br>■               |
|        | 9<br>Mocking best practices<br>216<br>■                 |
|        | 10<br>Testing the database<br>229<br>■                  |
| PART 4 | UNIT<br>ANTI-PATTERNS257<br>TESTING                     |
|        | 11<br>Unit testing anti-patterns<br>259<br>■            |

## contents

.....1

preface xiv
acknowledgments xv
about this book xvi
about the author xix
about the cover illustration xx

| PART 1 | THE BIGGER | PICTURE | <br> |
|--------|------------|---------|------|
|        |            |         | <br> |

## The goal of unit testing 3

- 1.1 The current state of unit testing 4
- 1.2 The goal of unit testing 5

  What makes a good or bad test? 7
- 1.3 Using coverage metrics to measure test suite quality 8

  Understanding the code coverage metric 9 Understanding the branch coverage metric 10 Problems with coverage metrics 12

  Aiming at a particular coverage number 15
- 1.4 What makes a successful test suite? 15

  It's integrated into the development cycle 16 It targets only the most important parts of your code base 16 It provides maximum value with minimum maintenance costs 17
- 1.5 What you will learn in this book 17

**viii** CONTENTS

|     | 20                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.1 | 2 What is a unit test?<br>The definition of "unit test"<br>21<br>The isolation issue: The London take<br>21<br>■ The isolation issue:<br>The classical take<br>27                                                                                                                                                                                                                                                                                                                      |
| 2.2 | The classical and London schools of unit testing<br>30<br>How the classical and London schools handle dependencies<br>30                                                                                                                                                                                                                                                                                                                                                               |
| 2.3 | Contrasting the classical and London schools<br>of unit testing<br>34<br>Unit testing one class at a time<br>34<br>■ Unit testing a large graph of<br>interconnected classes<br>35<br>■ Revealing the precise bug location<br>36<br>Other differences between the classical and London schools<br>36                                                                                                                                                                                   |
| 2.4 | Integration tests in the two schools<br>37<br>End-to-end tests are a subset of integration tests<br>38                                                                                                                                                                                                                                                                                                                                                                                 |
|     | 41                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 3.1 | 3 The anatomy of a unit test<br>How to structure a unit test<br>42<br>Using the AAA pattern<br>42<br>■ Avoid multiple arrange, act,<br>and assert sections<br>43<br>■ Avoid if statements in tests<br>44<br>How large should each section be?<br>45<br>■ How many assertions<br>should the assert section hold?<br>47<br>■ What about the teardown<br>phase?<br>47<br>■ Differentiating the system under test<br>47<br>Dropping the arrange, act, and assert comments from tests<br>48 |
| 3.2 | Exploring the xUnit testing framework<br>49                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 3.3 | Reusing test fixtures between tests<br>50<br>High coupling between tests is an anti-pattern<br>52<br>■ The use of<br>constructors in tests diminishes test readability<br>52<br>■ A better way<br>to reuse test fixtures<br>52                                                                                                                                                                                                                                                         |
| 3.4 | Naming a unit test<br>54<br>Unit test naming guidelines<br>56<br>■ Example: Renaming a test<br>toward the guidelines<br>56                                                                                                                                                                                                                                                                                                                                                             |
| 3.5 | Refactoring to parameterized tests<br>58<br>Generating data for parameterized tests<br>60                                                                                                                                                                                                                                                                                                                                                                                              |
| 3.6 | Using an assertion library to further improve<br>test readability<br>62                                                                                                                                                                                                                                                                                                                                                                                                                |

CONTENTS **ix**

|     | 67                                                                                                                                                                                                                                                                                                                                     |
|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.1 | 4 The four pillars of a good unit test<br>Diving into the four pillars of a good unit test<br>68<br>The first pillar: Protection against regressions<br>68<br>■ The second<br>pillar: Resistance to refactoring<br>69<br>■ What causes false<br>positives?<br>71<br>■ Aim at the end result instead of<br>implementation details<br>74 |
| 4.2 | The intrinsic connection between the first<br>two attributes<br>76                                                                                                                                                                                                                                                                     |
|     | Maximizing test accuracy<br>76<br>■ The importance of false positives<br>and false negatives: The dynamics<br>78                                                                                                                                                                                                                       |
| 4.3 | The third and fourth pillars: Fast feedback<br>and maintainability<br>79                                                                                                                                                                                                                                                               |
| 4.4 | In search of an ideal test<br>80                                                                                                                                                                                                                                                                                                       |
|     | Is it possible to create an ideal test?<br>81<br>■ Extreme case #1:<br>End-to-end tests<br>81<br>■ Extreme case #2: Trivial tests<br>82<br>Extreme case #3: Brittle tests<br>83<br>■ In search of an ideal test:<br>The results<br>84                                                                                                  |
| 4.5 | Exploring well-known test automation concepts<br>87                                                                                                                                                                                                                                                                                    |
|     | Breaking down the Test Pyramid<br>87<br>■ Choosing between black-box<br>and white-box testing<br>89                                                                                                                                                                                                                                    |
|     | 5 Mocks and test fragility<br>92                                                                                                                                                                                                                                                                                                       |
| 5.1 | Differentiating mocks from stubs<br>93                                                                                                                                                                                                                                                                                                 |
|     | The types of test doubles<br>93<br>■ Mock (the tool) vs. mock (the<br>test double)<br>94<br>■ Don't assert interactions with stubs<br>96<br>Using mocks and stubs together<br>97<br>■ How mocks and stubs<br>relate to commands and queries<br>97                                                                                      |
| 5.2 | Observable behavior vs. implementation details<br>99                                                                                                                                                                                                                                                                                   |
|     | Observable behavior is not the same as a public API<br>99<br>■ Leaking<br>implementation details: An example with an operation<br>100<br>Well-designed API and encapsulation<br>103<br>■ Leaking<br>implementation details: An example with state<br>104                                                                               |
| 5.3 | The relationship between mocks and test fragility<br>106                                                                                                                                                                                                                                                                               |
|     | Defining hexagonal architecture<br>106<br>■ Intra-system vs. inter<br>system communications<br>110<br>■ Intra-system vs. inter-system                                                                                                                                                                                                  |

*[communications: An example 111](011-chapter-5-mocks-and-test-fragility.md#page-132-0)*

**x** CONTENTS

| 5.4 | The classical vs. London schools of unit testing,<br>revisited<br>114                                                                                                                                                                                                                                            |
|-----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     | Not all out-of-process dependencies should be mocked out<br>115<br>Using mocks to verify behavior<br>116                                                                                                                                                                                                         |
|     | 119                                                                                                                                                                                                                                                                                                              |
| 6.1 | 6 Styles of unit testing<br>The three styles of unit testing<br>120                                                                                                                                                                                                                                              |
|     | Defining the output-based style<br>120<br>■ Defining the state-based<br>style<br>121<br>■ Defining the communication-based style<br>122                                                                                                                                                                          |
| 6.2 | Comparing the three styles of unit testing<br>123                                                                                                                                                                                                                                                                |
|     | Comparing the styles using the metrics of protection against<br>regressions and feedback speed<br>124<br>■ Comparing the styles using<br>the metric of resistance to refactoring<br>124<br>■ Comparing the styles<br>using the metric of maintainability<br>125<br>■ Comparing the styles:<br>The results<br>127 |
| 6.3 | Understanding functional architecture<br>128                                                                                                                                                                                                                                                                     |
|     | What is functional programming?<br>128<br>■ What is functional<br>architecture?<br>132<br>■ Comparing functional and hexagonal<br>architectures<br>133                                                                                                                                                           |
| 6.4 | Transitioning to functional architecture and output-based<br>testing<br>135<br>Introducing an audit system<br>135<br>■ Using mocks to decouple tests<br>from the filesystem<br>137<br>■ Refactoring toward functional<br>architecture<br>140<br>■ Looking forward to further developments<br>146                 |
| 6.5 | Understanding the drawbacks of functional architecture<br>146<br>Applicability of functional architecture<br>147<br>■ Performance<br>drawbacks<br>148<br>■ Increase in the code base size<br>149                                                                                                                 |
|     | 151                                                                                                                                                                                                                                                                                                              |
| 7.1 | 7 Refactoring toward valuable unit tests<br>Identifying the code to refactor<br>152                                                                                                                                                                                                                              |
|     | The four types of code<br>152<br>■ Using the Humble Object pattern to<br>split overcomplicated code<br>155                                                                                                                                                                                                       |
| 7.2 | Refactoring toward valuable unit tests<br>158                                                                                                                                                                                                                                                                    |
|     | Introducing a customer management system<br>158<br>■ Take 1:<br>Making implicit dependencies explicit<br>160<br>■ Take 2: Introducing<br>an application services layer<br>160<br>■ Take 3: Removing complexity<br>from the application service<br>163<br>■ Take 4: Introducing a new                             |

CONTENTS **xi**

|        | 7.3 | Analysis of optimal unit test coverage<br>167                                                                                                                                                                                                                   |
|--------|-----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        |     | Testing the domain layer and utility code<br>167<br>■ Testing the code<br>from the other three quadrants<br>168<br>■ Should you test<br>preconditions?<br>169                                                                                                   |
|        | 7.4 | Handling conditional logic in controllers<br>169<br>Using the CanExecute/Execute pattern<br>172<br>■ Using domain<br>events to track changes in the domain model<br>175                                                                                         |
|        | 7.5 | Conclusion<br>178                                                                                                                                                                                                                                               |
| PART 3 |     | INTEGRATION<br>TESTING183                                                                                                                                                                                                                                       |
|        |     | 185                                                                                                                                                                                                                                                             |
|        | 8.1 | 8 Why integration testing?<br>What is an integration test?<br>186                                                                                                                                                                                               |
|        |     | The role of integration tests<br>186<br>■ The Test Pyramid<br>revisited<br>187<br>■ Integration testing vs. failing fast<br>188                                                                                                                                 |
|        | 8.2 | Which out-of-process dependencies to test directly<br>190<br>The two types of out-of-process dependencies<br>190<br>■ Working with<br>both managed and unmanaged dependencies<br>191<br>■ What if you<br>can't use a real database in integration tests?<br>192 |
|        | 8.3 | Integration testing: An example<br>193<br>What scenarios to test?<br>194<br>■ Categorizing the database and<br>the message bus<br>195<br>■ What about end-to-end testing?<br>195<br>Integration testing: The first try<br>196                                   |
|        | 8.4 | Using interfaces to abstract dependencies<br>197<br>Interfaces and loose coupling<br>198<br>■ Why use interfaces for<br>out-of-process dependencies?<br>199<br>■ Using interfaces for in-process<br>dependencies<br>199                                         |
|        | 8.5 | Integration testing best practices<br>200<br>Making domain model boundaries explicit<br>200<br>■ Reducing the<br>number of layers<br>200<br>■ Eliminating circular dependencies<br>202<br>Using multiple act sections in a test<br>204                          |
|        | 8.6 | How to test logging functionality<br>205<br>Should you test logging?<br>205<br>■ How should you test<br>logging?<br>207<br>■ How much logging is enough?<br>212<br>How do you pass around logger instances?<br>212                                              |
|        | 8.7 | Conclusion<br>213                                                                                                                                                                                                                                               |
|        |     |                                                                                                                                                                                                                                                                 |

**xii** CONTENTS

|                | 216                                                                                                                                                                                                                                         |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 9.1            | 9 Mocking best practices<br>Maximizing mocks' value<br>217                                                                                                                                                                                  |
|                | Verifying interactions at the system edges<br>219<br>■ Replacing mocks<br>with spies<br>222<br>■ What about IDomainLogger?<br>224                                                                                                           |
| 9.2            | Mocking best practices<br>225                                                                                                                                                                                                               |
|                | Mocks are for integration tests only<br>225<br>■ Not just one mock per<br>test<br>225<br>■ Verifying the number of calls<br>226<br>■ Only mock types<br>that you own<br>227                                                                 |
|                | 229                                                                                                                                                                                                                                         |
| 10.1           | 10 Testing the database<br>Prerequisites for testing the database<br>230                                                                                                                                                                    |
|                | Keeping the database in the source control system<br>230<br>■ Reference<br>data is part of the database schema<br>231<br>■ Separate instance for<br>every developer<br>232<br>■ State-based vs. migration-based database<br>delivery<br>232 |
| 10.2           | Database transaction management<br>234                                                                                                                                                                                                      |
|                | Managing database transactions in production code<br>235<br>■ Managing<br>database transactions in integration tests<br>242                                                                                                                 |
| 10.3           | Test data life cycle<br>243                                                                                                                                                                                                                 |
|                | Parallel vs. sequential test execution<br>243<br>■ Clearing data between<br>test runs<br>244<br>■ Avoid in-memory databases<br>246                                                                                                          |
| 10.4           | Reusing code in test sections<br>246                                                                                                                                                                                                        |
|                | Reusing code in arrange sections<br>246<br>■ Reusing code in<br>act sections<br>249<br>■ Reusing code in assert sections<br>250<br>Does the test create too many database transactions?<br>251                                              |
| 10.5           | Common database testing questions<br>252                                                                                                                                                                                                    |
|                | Should you test reads?<br>252<br>■ Should you test repositories?<br>253                                                                                                                                                                     |
| 10.6           | Conclusion<br>254                                                                                                                                                                                                                           |
| PART 3<br>UNIT | ANTI-PATTERNS257<br>TESTING                                                                                                                                                                                                                 |
|                | 259                                                                                                                                                                                                                                         |
| 11.1           | 11 Unit testing anti-patterns<br>Unit testing private methods<br>260                                                                                                                                                                        |
|                | Private methods and test fragility<br>260<br>■ Private methods and<br>insufficient coverage<br>260<br>■ When testing private methods is<br>acceptable<br>261                                                                                |
| 11.2           | Exposing private state<br>263                                                                                                                                                                                                               |
| 11.3           | Leaking domain knowledge to tests<br>264                                                                                                                                                                                                    |
|                |                                                                                                                                                                                                                                             |

CONTENTS **xiii**

- [11.4 Code pollution 266](019-chapter-11-unit-testing-anti-patterns.md#page-287-0)
- [11.5 Mocking concrete classes 268](019-chapter-11-unit-testing-anti-patterns.md#page-289-0)
- [11.6 Working with time 271](019-chapter-11-unit-testing-anti-patterns.md#page-292-0) *[Time as an ambient context 271](019-chapter-11-unit-testing-anti-patterns.md#page-292-1)* ■ *[Time as an explicit](019-chapter-11-unit-testing-anti-patterns.md#page-293-0)  [dependency 272](019-chapter-11-unit-testing-anti-patterns.md#page-293-0)*

[11.7 Conclusion 273](019-chapter-11-unit-testing-anti-patterns.md#page-294-0)

*[index 275](020-index.md#page-296-0)*
