<span id="page-443-0"></span>
# Glossary

**change point** A place in code where you need to make a change.

**characterization test** A test written to document the current behavior of a piece of software and preserve it as you change its code.

**coupling count** The number of values that pass in and out of a method when it is called. If there is no return value, it is the number of parameters. If there is, it is the number of parameters plus one. Coupling count can be a very useful thing to compute for small methods you'd like to extract if you have to extract without tests.

**effect sketch** A small hand-drawn sketch that shows what variables and method return values can be affected by a software change. Effect sketches can be useful when you are trying to decide where to write tests.

**fake object** An object that impersonates a collaborator of a class during testing.

**feature sketch** A small hand-drawn sketch that shows how methods in a class use other methods and instance variables. Feature sketches can be useful when you are trying to decide how to break apart a large class.

**free function** A function that is not part of any class. In C and other procedural languages, these are just called functions. In C++ they are called non-member functions. Free functions don't exist in Java and C#.

**interception point** A place where a test can be written to sense some condition in a piece of software.

**link seam** A place where you can vary behavior by linking to a library. In compiled languages, you can replace production libraries, DLLs, assemblies, or JAR files with others during testing to get rid of dependencies or sense some condition that can happen in a test.

**mock object** A fake object that asserts conditions internally.

**object seam** A place where you can vary behavior by replacing one object with another. In object-oriented languages, you usually do this by subclassing a class in your production code and overriding various methods of the class.

**Glossary**

**pinch point** A narrowing in an effect sketch that indicates an ideal place to test a cluster of features.

**programming by difference** A way of using inheritance to add features in object-oriented systems. It can often be used as a way to get a new feature into the system quickly. The tests that you write to provoke the new feature can be used to refactor the code into a better state afterward.

**seam** A place where you can vary behavior in a software system without editing in that place. For instance, a call to a polymorphic function on an object is a seam because you can subclass the class of the object and have it behave differently.

**test-driven development (TDD)** A development process that consists of writing failing test cases and satisfying them one at a time. As you do this, you refactor to keep the code as simple as possible. Code developed using TDD has test coverage, by default.

**test harness** A piece of software that enables unit testing.

**testing subclass** A subclass made to allow access to a class for testing.

**unit test** A test that runs in less than 1/10th of a second and is small enough to help you localize problems when it fails.
