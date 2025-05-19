# Syntactic Analyzers: LL(1) and SLR(1) Grammars

## Team
* Juan José Escobar Saldarriaga
* Samuel Llano Madrigal
* Class Code: 7308

## Development environment
* Operating System: Windows 11
* Programming Language: Python 3.12.2
* Tools: IDE's and editors such as Visual Studio Code

## Algorithm Description
* This program allows the user to enter a grammar from its derivation rules and then verify if it is type LL(1) and/or SLR(1), in addition to all the processes such as tables or sets necessary for its parser, since it can then verify if a string belongs to the grammar or not.

## Explanation and Structure

### First and Follow
From chapter 4.4.2 of Compilers: Principles, Techniques, & Tools. 2nd ed. Boston: Pearson/Addison Wesley, 2007.
* To compute FIRST (X) for all grammar symbols X, apply the following rules until no more terminals or can be added to any FIRST set.
  1. If X is a terminal, then FIRST (X) = {X}
  2. If X is a nonterminal and X Y1Y2...Yk is a production for some k 1, then place a in FIRST (X) if for some i a is in FIRST (Yi), and is in all of FIRST Y1 ;::: ; FIRST Yi 1); that is, Y1 Yi 1 If is in FIRST Yj for all j = 1 2;::: ;k, then add to FIRST (X).
     For example, everything in FIRST Y1) is surely in FIRST X). If Y1 does not derive , then we add nothing more to FIRST X), but if Y1 , then we add FIRST Y2), and so on.
  3. If X is a production, then add to FIRST X
* To compute FOLLOW (A) for all nonterminals A apply the following rules until nothing can be added to any FOLLOW set.
  1. Place $ in FOLLOW (S), where S is the start symbol, and $ is the input right endmarker.
  2. If there is a production A alphaBbeta, then everything in FIRST (beta) except epsilon is in FOLLOW (B).
  3. If there is a production A -> alphaB or a production A -> alphaBbeta where FIRST (beta) contains epsilon, then everything in FOLLOW (A) is in FOLLOW (B)

### LL(1) Table
