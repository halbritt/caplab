# O'REILLY®

## Architecture Patterns with Python

Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices

![](../assets/_page_0_Picture_3.jpeg)

Harry J.W. Percival & Bob Gregory

### 1. Preface

- a. Managing Complexity, Solving Business Problems
- b. Why Python?
- c. TDD, DDD, and Event-Driven Architecture
- d. Who Should Read This Book
- e. A Brief Overview of What You'll Learn
  - i. Part I, Building an Architecture to Support Domain Modeling
  - ii. Part II, Event-Driven Architecture
  - iii. Addtional Content
- f. Example Code and Coding Along
- g. License
- h. Conventions Used in This Book
- i. O'Reilly Online Learning
- j. How to Contact O'Reilly
- k. Acknowledgments

### 2. Introduction

- a. Why Do Our Designs Go Wrong?
- b. Encapsulation and Abstractions
- c. Layering
- d. The Dependency Inversion Principle

- e. A Place for All Our Business Logic: The Domain Model
- 3. I. Building an Architecture to Support Domain Modeling
- 4. 1. Domain Modeling
  - a. What Is a Domain Model?
  - b. Exploring the Domain Language
  - c. Unit Testing Domain Models
    - i. Dataclasses Are Great for Value Objects
    - ii. Value Objects and Entities
  - d. Not Everything Has to Be an Object: A Domain Service Function
    - i. Python's Magic Methods Let Us Use Our Models with Idiomatic Python
    - ii. Exceptions Can Express Domain Concepts Too
- 5. 2. Repository Pattern
  - a. Persisting Our Domain Model
  - b. Some Pseudocode: What Are We Going to Need?
  - c. Applying the DIP to Data Access
  - d. Reminder: Our Model
    - i. The "Normal" ORM Way: Model Depends on ORM

- ii. Inverting the Dependency: ORM Depends on Model
- e. Introducing the Repository Pattern
  - i. The Repository in the Abstract
  - ii. What Is the Trade-Off?
- f. Building a Fake Repository for Tests Is Now Trivial!
- g. What Is a Port and What Is an Adapter, in Python?
- h. Wrap-Up
- 6. 3. A Brief Interlude: On Coupling and Abstractions
  - a. Abstracting State Aids Testability
  - b. Choosing the Right Abstraction(s)
  - c. Implementing Our Chosen Abstractions
    - i. Testing Edge to Edge with Fakes and Dependency Injection
    - ii. Why Not Just Patch It Out?
  - d. Wrap-Up
- 7. 4. Our First Use Case: Flask API and Service Layer
  - a. Connecting Our Application to the Real World
  - b. A First End-to-End Test
  - c. The Straightforward Implementation
  - d. Error Conditions That Require Database Checks

- e. Introducing a Service Layer, and Using FakeRepository to Unit Test It
  - i. A Typical Service Function
- f. Why Is Everything Called a Service?
- g. Putting Things in Folders to See Where It All Belongs
- h. Wrap-Up
  - i. The DIP in Action
- 8. 5. TDD in High Gear and Low Gear
  - a. How Is Our Test Pyramid Looking?
  - b. Should Domain Layer Tests Move to the Service Layer?
  - c. On Deciding What Kind of Tests to Write
  - d. High and Low Gear
  - e. Fully Decoupling the Service-Layer Tests from the Domain
    - i. Mitigation: Keep All Domain
      Dependencies in Fixture Functions
    - ii. Adding a Missing Service
  - f. Carrying the Improvement Through to the E2E Tests
  - g. Wrap-Up
- 9. 6. Unit of Work Pattern
  - a. The Unit of Work Collaborates with the Repository

- b. Test-Driving a UoW with Integration Tests
- c. Unit of Work and Its Context Manager
  - i. The Real Unit of Work Uses SQLAlchemy Sessions
  - ii. Fake Unit of Work for Testing
- d. Using the UoW in the Service Layer
- e. Explicit Tests for Commit/Rollback Behavior
- f. Explicit Versus Implicit Commits
- g. Examples: Using UoW to Group Multiple Operations into an Atomic Unit
  - i. Example 1: Reallocate
  - ii. Example 2: Change Batch Quantity
- h. Tidying Up the Integration Tests
- i. Wrap-Up
- 10. 7. Aggregates and Consistency Boundaries
  - a. Why Not Just Run Everything in a Spreadsheet?
  - b. Invariants, Constraints, and Consistency
    - i. Invariants, Concurrency, and Locks
  - c. What Is an Aggregate?
  - d. Choosing an Aggregate
  - e. One Aggregate = One Repository
  - f. What About Performance?

- g. Optimistic Concurrency with Version Numbers
  - i. Implementation Options for Version Numbers
- h. Testing for Our Data Integrity Rules
  - i. Enforcing Concurrency Rules by Using Database Transaction Isolation Levels
  - ii. Pessimistic Concurrency Control Example: SELECT FOR UPDATE
- i. Wrap-Up
- j. Part I Recap
- 11. II. Event-Driven Architecture
- 12. 8. Events and the Message Bus
  - a. Avoiding Making a Mess
    - i. First, Let's Avoid Making a Mess of Our Web Controllers
    - ii. And Let's Not Make a Mess of Our Model Either
    - iii. Or the Service Layer!
  - b. Single Responsibility Principle
  - c. All Aboard the Message Bus!
    - i. The Model Records Events
    - ii. Events Are Simple Dataclasses
    - iii. The Model Raises Events

- iv. The Message Bus Maps Events to Handlers
- d. Option 1: The Service Layer Takes Events from the Model and Puts Them on the Message Bus
- e. Option 2: The Service Layer Raises Its Own Events
- f. Option 3: The UoW Publishes Events to the Message Bus
- g. Wrap-Up
- 13. 9. Going to Town on the Message Bus
  - a. A New Requirement Leads Us to a New Architecture
    - i. Imagining an Architecture Change: Everything Will Be an Event Handler
  - b. Refactoring Service Functions to Message Handlers
    - i. The Message Bus Now Collects Events from the UoW
    - ii. Our Tests Are All Written in Terms of Events Too
    - iii. A Temporary Ugly Hack: The Message Bus Has to Return Results
    - iv. Modifying Our API to Work with Events
  - c. Implementing Our New Requirement
    - i. Our New Event

- d. Test-Driving a New Handler
  - i. Implementation
  - ii. A New Method on the Domain Model
- e. Optionally: Unit Testing Event Handlers in Isolation with a Fake Message Bus
- f. Wrap-Up
  - i. What Have We Achieved?
  - ii. Why Have We Achieved?
- 14. 10. Commands and Command Handler
  - a. Commands and Events
  - b. Differences in Exception Handling
  - c. Discussion: Events, Commands, and Error Handling
  - d. Recovering from Errors Synchronously
  - e. Wrap-Up
- 15. 11. Event-Driven Architecture: Using Events to Integrate Microservices
  - a. Distributed Ball of Mud, and Thinking in Nouns
  - b. Error Handling in Distributed Systems
  - c. The Alternative: Temporal Decoupling Using Asynchronous Messaging
  - d. Using a Redis Pub/Sub Channel for Integration

- e. Test-Driving It All Using an End-to-End Test
  - i. Redis Is Another Thin Adapter Around Our Message Bus
  - ii. Our New Outgoing Event
- f. Internal Versus External Events
- g. Wrap-Up
- 16. 12. Command-Query Responsibility Segregation (CQRS)
  - a. Domain Models Are for Writing
  - b. Most Users Aren't Going to Buy Your Furniture
  - c. Post/Redirect/Get and CQS
  - d. Hold On to Your Lunch, Folks
  - e. Testing CQRS Views
  - f. "Obvious" Alternative 1: Using the Existing Repository
  - g. Your Domain Model Is Not Optimized for Read Operations
  - h. "Obvious" Alternative 2: Using the ORM
  - i. SELECT N+1 and Other Performance Considerations
  - j. Time to Completely Jump the Shark
    - i. <u>Updating a Read Model Table Using an</u> Event Handler

- k. Changing Our Read Model Implementation Is
  Easy
- l. Wrap-Up
- 17. 13. Dependency Injection (and Bootstrapping)
  - a. Implicit Versus Explicit Dependencies
  - b. Aren't Explicit Dependencies Totally Weird and Java-y?
  - c. Preparing Handlers: Manual DI with Closures and Partials
  - d. An Alternative Using Classes
  - e. A Bootstrap Script
  - f. Message Bus Is Given Handlers at Runtime
  - g. Using Bootstrap in Our Entrypoints
  - h. Initializing DI in Our Tests
  - i. Building an Adapter "Properly": A Worked Example
    - i. Define the Abstract and Concrete Implementations
    - ii. Make a Fake Version for Your Tests
    - iii. Figure Out How to Integration Test the Real Thing
  - j. Wrap-Up
- 18. Epilogue
  - a. What Now?

- b. How Do I Get There from Here?
- c. Separating Entangled Responsibilities
- d. Identifying Aggregates and Bounded Contexts
- e. An Event-Driven Approach to Go to Microservices via Strangler Pattern
- f. Convincing Your Stakeholders to Try Something New
- g. Questions Our Tech Reviewers Asked That We Couldn't Work into Prose
- h. Footguns
- i. More Required Reading
- j. Wrap-Up
- 19. A. Summary Diagram and Table
- 20. B. A Template Project Structure
  - a. Env Vars, 12-Factor, and Config, Inside and Outside Containers
  - b. Config.py
  - c. Docker-Compose and Containers Config
  - d. Installing Your Source as a Package
  - e. Dockerfile
  - f. Tests
  - g. Wrap-Up
- 21. C. Swapping Out the Infrastructure: Do Everything with CSVs

a. Implementing a Repository and Unit of Work for CSVs

### 22. D. Repository and Unit of Work Patterns with Django

- a. Repository Pattern with Django
  - i. Custom Methods on Django ORM Classes to Translate to/from Our Domain Model
- b. Unit of Work Pattern with Django
- c. API: Django Views Are Adapters
- d. Why Was This All So Hard?
- e. What to Do If You Already Have Django
- f. Steps Along the Way

### 23. E. Validation

- a. What Is Validation, Anyway?
- b. Validating Syntax
- c. Postel's Law and the Tolerant Reader Pattern
- d. Validating at the Edge
- e. Validating Semantics
- f. Validating Pragmatics

### 24. Index

## Architecture Patterns with Python

Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices

Harry Percival and Bob Gregory

### Architecture Patterns with Python

by Harry Percival and Bob Gregory

Copyright © 2020 Harry Percival and Bob Gregory. All rights reserved.

Printed in the United States of America.

Published by O'Reilly Media, Inc., 1005 Gravenstein Highway North, Sebastopol, CA 95472.

O'Reilly books may be purchased for educational, business, or sales promotional use. Online editions are also available for most titles (<a href="http://oreilly.com">http://oreilly.com</a>). For more information, contact our corporate/institutional sales department: 800-998-9938 or corporate@oreilly.com.

Acquisitions Editor: Ryan Shaw

Development Editor: Corbin Collins

Production Editor: Katherine Tozer

Copyeditor: Sharon Wilkey

Proofreader: Arthur Johnson

Indexer: Ellen Troutman-Zaig

Interior Designer: David Futato

Cover Designer: Karen Montgomery

Illustrator: Rebecca Demarest

March 2020: First Edition

### Revision History for the First Edition

• 2020-03-05: First Release

See <a href="http://oreilly.com/catalog/errata.csp?isbn=9781492052203">http://oreilly.com/catalog/errata.csp?isbn=9781492052203</a> for release details.

The O'Reilly logo is a registered trademark of O'Reilly Media, Inc. *Architecture Patterns with Python*, the cover image, and related trade dress are trademarks of O'Reilly Media, Inc.

The views expressed in this work are those of the authors and do not represent the publisher's views. While the publisher and the authors have used good faith efforts to ensure that the information and instructions contained in this work are accurate, the publisher and the authors disclaim all responsibility for errors or omissions, including without limitation responsibility for damages resulting from the use of or reliance on this work. Use of the information and instructions contained in this work is at your own risk. If any code samples or other technology this work contains or describes is subject to open source licenses or the intellectual property rights of others, it is your responsibility to ensure that your use thereof complies with such licenses and/or rights.
