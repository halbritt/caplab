<span id="page-7-4"></span>
<span id="page-7-3"></span>
<span id="page-7-2"></span>
<span id="page-7-1"></span>
<span id="page-7-0"></span>
# Contents

| Foreword by Robert C. Martin<br>xv                                                   |
|--------------------------------------------------------------------------------------|
| Preface<br>xv                                                                        |
| Introduction<br>xxi                                                                  |
| PART I: The Mechanics of Change 1                                                    |
| Chapter 1: Changing Software 3                                                       |
| Four Reasons to Change Software 4<br>Risky Change 7                                  |
| Chapter 2: Working with Feedback 9                                                   |
| What Is Unit Testing? 12<br>Higher-Level Testing 14                                  |
| Test Coverings 14<br>The Legacy Code Change Algorithm<br>18                          |
| Chapter 3: Sensing and Separation<br><br>21                                          |
| Faking Collaborators 23                                                              |
| Chapter 4: The Seam Model<br>29                                                      |
| A Huge Sheet of Text 29<br>Seams 30<br>Seam Types<br>33                              |
| Chapter 5: Tools<br>45                                                               |
| Automated Refactoring Tools<br>45<br>Mock Objects 47<br>Unit-Testing Harnesses<br>48 |
| General Test Harnesses 53                                                            |

## **viii** CONTENTS

<span id="page-8-2"></span><span id="page-8-1"></span><span id="page-8-0"></span>

| viii |  |
|------|--|
| VIII |  |
|      |  |
| •    |  |

|             | PART II: Changing Software55                                                                                                                                                                                                                                                                                     |  |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
|             | Chapter 6: I Don't Have Much Time and I Have to Change It 57                                                                                                                                                                                                                                                     |  |
| Wrap Method | Sprout Method59<br>Sprout Class63<br>67<br>Wrap Class71                                                                                                                                                                                                                                                          |  |
|             | Summary 76                                                                                                                                                                                                                                                                                                       |  |
|             | Chapter 7: It Takes Forever to Make a Change 77                                                                                                                                                                                                                                                                  |  |
|             | Understanding77<br>Lag Time78<br>Breaking Dependencies<br>79<br>Summary85                                                                                                                                                                                                                                        |  |
|             | Chapter 8: How Do I Add a Feature? 87                                                                                                                                                                                                                                                                            |  |
|             | Test-Driven Development (TDD)<br>88<br>Programming by Difference94<br>Summary104                                                                                                                                                                                                                                 |  |
|             | Chapter 9: I Can't Get This Class into a Test Harness<br>105                                                                                                                                                                                                                                                     |  |
|             | The Case of the Irritating Parameter106<br>The Case of the Hidden Dependency113<br>The Case of the Construction Blob<br>116<br>The Case of the Irritating Global Dependency118<br>The Case of the Horrible Include Dependencies127<br>The Case of the Onion Parameter130<br>The Case of the Aliased Parameter133 |  |
|             | Chapter 10: I Can't Run This Method in a Test Harness<br>137                                                                                                                                                                                                                                                     |  |
|             | The Case of the Hidden Method138<br>The Case of the "Helpful" Language Feature141<br>The Case of the Undetectable Side Effect144                                                                                                                                                                                 |  |
|             | Chapter 11: I Need to Make a Change. What Methods Should I Test? 151                                                                                                                                                                                                                                             |  |
|             | Reasoning About Effects151<br>Reasoning Forward157<br>Effect Propagation163<br>Tools for Effect Reasoning165<br>Learning from Effect Analysis167<br>Simplifying Effect Sketches168                                                                                                                               |  |

<span id="page-9-2"></span><span id="page-9-1"></span><span id="page-9-0"></span>

| Chapter 12: I Need to Make Many Changes in One Area.<br><br>173                                                                           |
|-------------------------------------------------------------------------------------------------------------------------------------------|
| Interception Points 174                                                                                                                   |
| Judging Design with Pinch Points 182                                                                                                      |
| Pinch Point Traps 184                                                                                                                     |
| Chapter 13: I Need to Make a Change,<br>but I Don't Know What Tests to Write<br>185                                                       |
| Characterization Tests<br>186<br>Characterizing Classes 189<br>Targeted Testing 190<br>A Heuristic for Writing Characterization Tests 195 |
| Chapter 14: Dependencies on Libraries Are Killing Me<br>197                                                                               |
| Chapter 15: My Application Is All API Calls<br>199                                                                                        |
| Chapter 16: I Don't Understand the Code Well Enough to Change It 209<br>Notes/Sketching 210                                               |
| Listing Markup 211<br>Scratch Refactoring<br>212<br>Delete Unused Code 213                                                                |
| Chapter 17: My Application Has No Structure<br>215                                                                                        |
| Telling the Story of the System 216<br>Naked CRC 220<br>Conversation Scrutiny<br>224                                                      |
| Chapter 18: My Test Code Is in the Way<br>227                                                                                             |
| Class Naming Conventions 227<br>Test Location 228                                                                                         |
| Chapter 19: My Project Is Not Object Oriented.<br>How Do I Make Safe Changes?<br>231                                                      |
| An Easy Case 232<br>A Hard Case 232<br>Adding New Behavior<br>236                                                                         |
| Taking Advantage of Object Orientation 239<br>It's All Object Oriented 242                                                                |
| Chapter 20: This Class Is Too Big and I Don't Want It to Get Any Bigger .<br>245                                                          |
| Seeing Responsibilities 249                                                                                                               |

<span id="page-10-2"></span>
<span id="page-10-1"></span>
<span id="page-10-0"></span>
### **x** CONTENTS

| Other Techniques265                                                                 |     |
|-------------------------------------------------------------------------------------|-----|
| Moving Forward265                                                                   |     |
| After Extract Class268                                                              |     |
| Chapter 21: I'm Changing the Same Code All Over the Place 269                       |     |
| First Steps<br>272                                                                  |     |
|                                                                                     |     |
| Chapter 22: I Need to Change a Monster Method<br>and I Can't Write Tests for It 289 |     |
| Varieties of Monsters290                                                            |     |
| Tackling Monsters with Automated Refactoring Support                                | 294 |
| The Manual Refactoring Challenge297                                                 |     |
| Strategy304                                                                         |     |
| Chapter 23: How Do I Know That I'm Not Breaking Anything? 309                       |     |
| Hyperaware Editing310                                                               |     |
| Single-Goal Editing311                                                              |     |
| Preserve Signatures312                                                              |     |
| Lean on the Compiler<br>315                                                         |     |
| Chapter 24: We Feel Overwhelmed. It Isn't Going to Get Any Better319                |     |
| PART III: Dependency-Breaking Techniques323                                         |     |
| Chapter 25: Dependency-Breaking Techniques<br>325                                   |     |
| Adapt Parameter326                                                                  |     |
| Break Out Method Object330                                                          |     |
| Definition Completion337                                                            |     |
| Encapsulate Global References339                                                    |     |
| Expose Static Method345                                                             |     |
| Extract and Override Call348                                                        |     |
| Extract and Override Factory Method350                                              |     |
| Extract and Override Getter352                                                      |     |
| Extract Implementer<br>356                                                          |     |
| Extract Interface<br>362                                                            |     |
| Introduce Instance Delegator369                                                     |     |
| Introduce Static Setter372                                                          |     |
| Link Substitution377                                                                |     |
| Parameterize Constructor379                                                         |     |
| Parameterize Method383                                                              |     |

#### CONTENTS **xi**

<span id="page-11-2"></span><span id="page-11-1"></span><span id="page-11-0"></span>

| Primitivize Parameter 385                   |     |
|---------------------------------------------|-----|
| Pull Up Feature 388                         |     |
| Push Down Dependency 392                    |     |
| Replace Function with Function Pointer 396  |     |
| Replace Global Reference with Getter<br>399 |     |
| Subclass and Override Method 401            |     |
| Supersede Instance Variable 404             |     |
| Template Redefinition 408                   |     |
| Text Redefinition 412                       |     |
| Appendix: Refactoring                       | 415 |
| Extract Method<br>415                       |     |
| Glossary<br>                                | 421 |
| Index 423                                   |     |

![](../assets/_page_12_Picture_0.jpeg)
