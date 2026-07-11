<span id="page-228-0"></span>
# Appendix A3: Data Mining with Git, cloc, and CodeScene

<span id="page-228-1"></span>This appendix contains a brief summary of the data mining commands used throughout the book. There's also a brief introduction to cloc as a proxy for complexity metrics, and a quick look at the planned support for exporting analysis data from CodeScene.

<span id="page-228-4"></span>
## Behavioral Code Analysis with Git

This section summarizes the most important Git commands. Please note that the trailing backslash, \, is used to break the lines so that they appear readable in the text, and you want to omit those backslashes and join the lines together when you enter the commands.

<span id="page-228-3"></span>
## Detect Hotspots

Here we ask Git to deliver a list of all modified files in every commit. We then remove empty lines—a side effect of the Git command—with the egrep command. The command then counts the frequency of the resulting file names and delivers the results sorted in descending order:

```
adam$ git log --format=format: --name-only | egrep -v '^$' | sort \
                          | uniq -c | sort -r
```

You limit the analysis period by specifying the --after option—for example, as --after=2016-01-01 to only get modifications since January 1, 2016.

In large codebases, you may want to run the analyses on each subsystem. You do that by specifying the path to the root folder of each subsystem. For example, the following command limits the data mining to the code under Linux's drivers/gpu folder:

```
adam$ git log --format=format: --name-only --after=2016-01-01 \
     -- drivers/gpu/ | sort | uniq -c | sort -r
```

<span id="page-229-0"></span>Use git rev-list --count HEAD to aggregate all contributions and calculate hotspots on the level of logical components. You can run the same command on individual folders too, in case they align with the logical components in your codebase. Here's an example:

```
adam$ git rev-list --count HEAD -- src/application/engine/
55
```

The X-Ray functionality is typically built using language-specific parsers, but you can get a working version for free with some Git magic. In that case you specify the -L option, which instructs Git to fetch each historic revision based on the range of lines of code that make up a function. Here's an example on Linux to X-Ray the intel\_crtc\_page\_flip function in the drivers/gpu/drm/i915/intel\_display.c hotspot:

```
adam$ git log -L:intel_crtc_page_flip:drivers/gpu/drm/i915/intel_display.c
```

Note that the command will take quite some time to complete on large files. The command outputs the complete state of the code as it looked in each revision. This comes in handy if you want to calculate complexity trends. If you just want to get a proxy for the technical debt interest rate, then you can count the change frequency of the hotspot function by means of commandline tools. Here's an example from a Bash shell where grep filters out each commit hash, wc -l counts them, and the --after option limits the amount of data to a recent development period:

```
adam$ git log -L:intel_crtc_page_flip:drivers/gpu/drm/i915/intel_display.c \
             --after=2017-01-01 | grep 'commit ' | wc -l
  5
```

### Explore Git's Command-Line Options

![](../assets/_page_229_Picture_9.jpeg)

Git wasn't designed for data mining, so we often need to postprocess its output. This becomes less painful if we learn the different command-line options offered by the Git commands. Often, finding the right combination of options can dramatically simplify the postprocessing by delegating the heavy lifting to Git itself. The Git reference manual is a behavioral data miner's best friend.<sup>1</sup>

<sup>1.</sup> <https://git-scm.com/docs>

### Get Author Summaries

<span id="page-230-3"></span>The command git shortlog -s gives you a list of all contributing authors, including a count of their number of commits. You can run this command on a specific folder, too, by specifying a path with a double dash, as shown in the next example:

```
adam$ git shortlog -s -- src/application/engine/
  943 John
   11 Paul
  280 George
   20 Ringo
```

<span id="page-230-5"></span><span id="page-230-4"></span>This data serves as the basis for quick knowledge maps and as a first hint at a possible knowledge loss during offboarding.

Just as in earlier examples, you limit the data-mining depth to a specific time period with the --after option. This is useful to get information on the recent amount of parallel development in a component. In that case you summarize the number of unique authors by piping the output to the wc -l utility (available in a Bash shell), as shown in the next example:

```
adam$ git shortlog -s --after=2016-09-19 -- drivers/gpu/drm/i915/ | wc -l
55
```

### Get the Age of Your Code

Code age is calculated in two steps: first we fetch a list of all files in the repository with the git ls-files command, then we request the modification date of each file using a variation of git log, as shown in the next example:

```
adam$ git log -1 --format="%ad" --date=short \
  -- activerecord/lib/active_record/base.rb
2016-06-09
```

## A Brief Introduction to cloc

<span id="page-230-6"></span>cloc is used to calculate the number of lines of code and its GitHub page contains detailed documentation on the tool.<sup>2</sup> This section shows only the basic commands used to augment a change-frequency analysis with a lines-of-code dimension.

To get a summary of the content of your repository, move inside your repository and run cloc with the --quiet option:

<sup>2.</sup> <https://github.com/AlDanial/cloc>

| adam\$ clocquiet |  |  |  |  |  |
|------------------|--|--|--|--|--|
|------------------|--|--|--|--|--|

| Language               | files       | blank              | comment      | code            |
|------------------------|-------------|--------------------|--------------|-----------------|
| JavaScript<br>HTML     | 8208<br>243 | <br>122901<br>1533 | 130552<br>35 | 655610<br>21836 |
| <br>Dockerfile<br>Lisp | <br>2<br>1  | <br>7<br>0         | <br>4<br>0   | <br>22<br>6     |
| SUM:                   | 12966       | <br>179726<br>     | 138584       | 1145430         |

<span id="page-231-4"></span><span id="page-231-2"></span>You generate machine-readable CSV by adding the --csv option. This is the recommended approach since it makes it easier to postprocess the results by means of scripts or command-line tools.

To get the lines of code for each individual file you use the --by-file option. Here's an example where the line count of each file is delivered as CSV:

```
adam$ cloc ./ --by-file --csv --quiet
Java,./src/jvm/clojure/lang/Compiler.java,1000,651,7302
Clojure,./src/clj/clojure/core.clj,855,70,6844
Java,./src/jvm/clojure/lang/Numbers.java,676,1569,1911
Markdown,./changes.md,574,0,1860
...
```

<span id="page-231-5"></span><span id="page-231-1"></span>Just add the --report-file option to instruct cloc to save the data to a file:

```
adam$ cloc ./ --by-file --csv --quiet --report-file=lines_by_file.csv
```

cloc offers several options that help you filter and clean your data. The one I use all the time is --exclude-dir, which lets you exclude folders with third-party code or autogenerated content:

```
adam$ cloc ./ --by-file --csv --quiet --exclude-dir=node_modules
```

### Take Care on Windows

<span id="page-231-3"></span><span id="page-231-0"></span>![](../assets/_page_231_Picture_11.jpeg)

If you're on Windows you want to specify the --unix flag to get the cloc file names in the same UNIX path format as the data from Git.

## Export Analysis Data from CodeScene

At the time of writing (winter 2018), the CodeScene APIs aren't public yet, but they're likely to be if you pick up this book in the future. So let's have a brief discussion on those future possibilities and what you could do once the CodeScene APIs are available.

CodeScene automates most of the analyses in this book and provides some additional analyses—for example, risk classifications and machine learning–based prioritization algorithms. One of the goals with CodeScene is to make all that data available so that you can build your own analyses on top of it, or maybe complement it with other types of metrics.

In the final chapter of the book we looked at some proactive usages of behavioral code analysis. This is a field that has a lot to offer, in particular when we integrate the data into our IDEs and code editors. For example, we saw how a change coupling analysis could help detect omissions in *[Catch the Absence](016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md#page-205-0) of Change*[, on page 197.](016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md#page-205-0) The same data could be used to solve a much harder problem: reading code. Wouldn't it be great if the next time you looked at an unfamiliar piece of code, you got a friendly message that said, "Hey, other developers who read the code in this file also looked at the backup\_procedures.sql in the database and the regular\_scheduling.js file in the front-end repository."? Using existing analysis data would allow you to build that.
