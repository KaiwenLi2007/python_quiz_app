1.
The agent honestly crushed the initial setup. It broke the code into different files (like auth.py and storage.py) without me even asking. It got the main menus and the basic quiz logic working perfectly, though it did get a bit lazy with the "Smart Shuffle".

2.
Cursor did a good job on completing what I asked for, no major bugs or mistakes visible at a glamce.

3. 
The second agent was super nitpicky, which was actually great. It caught a security flaw where the first agent forgot to "salt" the passwords, which I totally missed.

On the flip side, it definitely hallucinated a bit. It flagged a "bug" in my error handling that wasn't actually a bug.

4. 
Looking back, my spec was a little too "vibes-based" when it came to the Smart Shuffle. I just said "make it more likely" to show liked questions, so the agent did the bare minimum. If I did this again, I’d give it a specific rule, like: "Questions the user likes should show up twice as often as everything else." The more math you give it, the better it performs.

5.
This plan-delegate-review style is awesome for building the "skeleton" of an app. It stops you from writing "spaghetti code" because you’re forced to think about the structure before you start typing.

That said, it’s kind of a pain for small bug fixes. If there’s just one tiny logic error, it’s way faster to just chat with the AI and fix that one line rather than making it re-read the whole spec and re-build the file.