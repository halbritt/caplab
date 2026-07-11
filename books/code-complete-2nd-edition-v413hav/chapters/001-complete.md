Microsoft\*

# COMPLETE

Second Edition

![](../assets/_page_0_Picture_3.jpeg)

A práctical handbook of software construction

Steve McConnell
Two-time winner of the Software Development Magazine Jolt Award

PUBLISHED BY Microsoft Press A Division of Microsoft Corporation One Microsoft Way Redmond, Washington 98052-6399

Copyright © 2004 by Steven C. McConnell

All rights reserved. No part of the contents of this book may be reproduced or transmitted in any form or by any means without the written permission of the publisher.

Library of Congress Cataloging-in-Publication Data McConnell, Steve

Code Complete / Steve McConnell.--2nd ed.

p. cm. Includes index.

ISBN 0-7356-1967-0

1. Computer Software--Development--Handbooks, manuals, etc. I. Title.

QA76.76.D47M39 2004 005.1--dc22 2004049981

Printed and bound in the United States of America.

15 16 17 18 19 20 21 22 23 24 QGT 6 5 4 3 2 1

Distributed in Canada by H.B. Fenn and Company Ltd. A CIP catalogue record for this book is available from the British Library.

Microsoft Press books are available through booksellers and distributors worldwide. For further information about international editions, contact your local Microsoft Corporation office or contact Microsoft Press International directly at fax (425) 936-7329. Visit our Web site at www.microsoft.com/mspress. Send comments to *mspinput@microsoft.com*.

Microsoft, Microsoft Press, PowerPoint, Visual Basic, Windows, and Windows NT are either registered trademarks or trademarks of Microsoft Corporation in the United States and/or other countries. Other product and company names mentioned herein may be the trademarks of their respective owners.

The example companies, organizations, products, domain names, e-mail addresses, logos, people, places, and events depicted herein are fictitious. No association with any real company, organization, product, domain name, e-mail address, logo, person, place, or event is intended or should be inferred.

This book expresses the author's views and opinions. The information contained in this book is provided without any express, statutory, or implied warranties. Neither the authors, Microsoft Corporation, nor its resellers, or distributors will be held liable for any damages caused or alleged to be caused either directly or indirectly by this book.

**Acquisitions Editors:** Linda Engelman and Robin Van Steenburgh

**Project Editor:** Devon Musgrave

**Indexer:** Bill Myers

**Principal Desktop Publisher:** Carl Diltz

Body Part No. X10-53130

*To my wife, Ashlie, who doesn't have much to do with computer programming but who has everything to do with enriching the rest of my life in more ways than I could possibly describe*

## Further Praise for Code Complete

- "An excellent guide to programming style and software construction."
- —Martin Fowler, *Refactoring*
- "Steve McConnell's *Code Complete* . . . provides a fast track to wisdom for programmers. . . . His books are fun to read, and you never forget that he is speaking from hard-won personal experience." —Jon Bentley, *Programming Pearls*, 2d ed.
- "This is simply the best book on software construction that I've ever read. Every developer should own a copy and read it cover to cover every year. After reading it annually for nine years, I'm still learning things from this book!"
- —John Robbins, *Debugging Applications for Microsoft .NET and Microsoft Windows*
- "Today's software *must* be robust and resilient, and secure code starts with disciplined software construction. After ten years, there is still no better authority than *Code Complete*."
- —Michael Howard, Security Engineering, Microsoft Corporation; Coauthor, *Writing Secure Code*
- "A comprehensive examination of the tactical issues that go into crafting a well-engineered program. McConnell's work covers such diverse topics as architecture, coding standards, testing, integration, and the nature of software craftsmanship."
- —Grady Booch, *Object Solutions*
- "The ultimate encyclopedia for the software developer is *Code Complete* by Steve McConnell. Subtitled 'A Practical Handbook of Software Construction,' this 850-page book is exactly that. Its stated goal is to narrow the gap between the knowledge of 'industry gurus and professors' (Yourdon and Pressman, for example) and common commercial practice, and 'to help you write better programs in less time with fewer headaches.' . . . Every developer should own a copy of McConnell's book. Its style and content are thoroughly practical."
- —Chris Loosley, *High-Performance Client/Server*
- "Steve McConnell's seminal book *Code Complete* is one of the most accessible works discussing in detail software development methods. . . ."
- —Erik Bethke, *Game Development and Production*
- "A mine of useful information and advice on the broader issues in designing and producing good software."
- —John Dempster, *The Laboratory Computer: A Practical Guide for Physiologists and Neuroscientists*

- "If you are serious about improving your programming skills, you should get *Code Complete* by Steve McConnell."
- —Jean J. Labrosse, *Embedded Systems Building Blocks: Complete and Ready-To-Use Modules in C*
- "Steve McConnell has written one of the best books on software development independent of computer environment . . . *Code Complete*."
- —Kenneth Rosen, *Unix: The Complete Reference*
- "Every half an age or so, you come across a book that short-circuits the school of experience and saves you years of purgatory. . . . I cannot adequately express how good this book really is. *Code Complete* is a pretty lame title for a work of brilliance."
- —Jeff Duntemann, *PC Techniques*
- "Microsoft Press has published what I consider to be the definitive book on software construction. This is a book that belongs on every software developer's shelf."
- —Warren Keuffel, *Software Development*
- "Every programmer should read this outstanding book." —T. L. (Frank) Pappas, *Computer*
- "If you aspire to be a professional programmer, this may be the wisest \$35 investment you'll ever make. Don't stop to read the rest of this review: just run out and buy it. McConnell's stated purpose is to narrow the gap between the knowledge of industry gurus and common commercial practice. . . . The amazing thing is that he succeeds."
- —Richard Mateosian, *IEEE Micro*
- "*Code Complete* should be required reading for anyone . . . in software development."
- —Tommy Usher, *C Users Journal*
- "I'm encouraged to stick my neck out a bit further than usual and recommend, without reservation, Steve McConnell's *Code Complete*. . . . My copy has replaced my API reference manuals as the book that's closest to my keyboard while I work."
- —Jim Kyle, *Windows Tech Journal*
- "This well-written but massive tome is arguably the best single volume ever written on the practical aspects of software implementation."
- —Tommy Usher, *Embedded Systems Programming*
- "This is the best book on software engineering that I have yet read."
- —Edward Kenworth, *.EXE Magazine*
- "This book deserves to become a classic, and should be compulsory reading for all developers, and those responsible for managing them." —Peter Wright, *Program Now*

Code Complete, Second Edition

*Steve McConnell*

## Contents at a Glance

| Part<br>I   | Laying the Foundation                                             |
|-------------|-------------------------------------------------------------------|
| 1           | Welcome to Software Construction3                                 |
| 2           | Metaphors for a Richer Understanding of Software Development<br>9 |
| 3           | Measure Twice, Cut Once: Upstream Prerequisites 23                |
| 4           | Key Construction Decisions 61                                     |
| Part<br>II  | Creating High-Quality Code                                        |
| 5           | Design in Construction 73                                         |
| 6           | Working Classes<br>125                                            |
| 7           | High-Quality Routines 161                                         |
| 8           | Defensive Programming<br>187                                      |
| 9           | The Pseudocode Programming Process<br>215                         |
| Part<br>III | Variables                                                         |
| 10          | General Issues in Using Variables 237                             |
| 11          | The Power of Variable Names<br>259                                |
| 12          | Fundamental Data Types<br>291                                     |
| 13          | Unusual Data Types<br>319                                         |
| Part<br>IV  | Statements                                                        |
| 14          | Organizing Straight-Line Code 347                                 |
| 15          | Using Conditionals 355                                            |
| 16          | Controlling Loops<br>367                                          |
| 17          | Unusual Control Structures 391                                    |
| 18          | Table-Driven Methods 411                                          |
| 19          | General Control Issues 431                                        |

| viii        | Table of Contents                         |
|-------------|-------------------------------------------|
| Part<br>V   | Code Improvements                         |
| 20          | The Software-Quality Landscape 463        |
| 21          | Collaborative Construction 479            |
| 22          | Developer Testing<br>499                  |
| 23          | Debugging 535                             |
| 24          | Refactoring 563                           |
| 25          | Code-Tuning Strategies 587                |
| 26          | Code-Tuning Techniques<br>609             |
| Part<br>VI  | System Considerations                     |
| 27          | How Program Size Affects Construction 649 |
| 28          | Managing Construction 661                 |
| 29          | Integration<br>689                        |
| 30          | Programming Tools<br>709                  |
| Part<br>VII | Software Craftsmanship                    |
| 31          | Layout and Style 729                      |
| 32          | Self-Documenting Code<br>777              |
| 33          | Personal Character<br>819                 |
| 34          | Themes in Software Craftsmanship 837      |
| 35          | Where to Find More Information 855        |
