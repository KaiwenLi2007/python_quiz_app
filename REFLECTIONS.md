1.
The agent did not perform well the initial setup. It broke the code into different files (such as auth.py and storage.py) without asking. The main menus and the basic quiz logic was working, though it did get a bit lazy with the "Shuffle".

2.
Cursor did a relatively good job on completing what I asked for. It would make assumptions on areas that I did not exactly tell it what to do, but overall it was smooth to create a project. No nessary stops during phrase 2. 

3. 
The second agent was picky about the codes, which was desirable for debuging and fixing errors. It caught a few security flaw where the first agent fail to manage the passwords, which I do not understand.

However, it also hallucinated. It would change the code for the previously working areas and flag them. 

4. 
Looking back, my spec was a too vague when speaking about a specifc function of the app. I just said "more likely", which the agent did not understand and excute as well. The agent did the bare minimum on those areas and detailing how much and how in the SPEC will help. If I did this again, I’d give it a specific rule, like: "Questions the user likes should show up twice as often as everything else." The more math you give it, the better it performs.

5.
This plan-delegate-review style is awesome for building the "skeleton" of an app. It stops you from writing pieces and pieces finding out that those pieces will not connect to each other. 

However, the agents also struggle with small bug fixes. If there’s just one tiny logic error, it’s way faster to just chat with the AI and fix that one line rather than making it re-read the whole spec and re-build the file.