COURSERATOR 3000
================

Dead simple course schedule generator for University of Waterloo courses.

![Screenshot]() ;wip

If you've ever used [Waterloo Course Qualifier](http://coursequalifier.com/) and gotten the below error message, this is for you.

![Course Qualifier Error](course_qualifier_error.png)

By using a powerful constraint solver, this service can handle extremely complex schedules with ease. See the "Implementation notes" section for details.

Using it online
---------------

1. Enter your courses in the provided field as a comma separated list. For example, `CS240, CS241, ECON201, ECE124, SCI267`.
2. The schedules should now be displayed in a table below the entry field. Select a schedule from the list to view it.
3. Selected schedules are displayed below the schedule table.

Hosting it yourself
-------------------

Is the site down? Want to set up your own Courserator instance? Here's how.

1. Download [this repository](https://github.com/Uberi/COURSERATOR-3000/archive/master.zip) and extract it somewhere.
2. Make sure Python 3.4 with `pip` is installed. Test this by running `pip3` in the terminal. If it prints out `pip` usage instructions, everything is fine.
3. OPTIONAL: If you are using Windows and want to avoid VS2008 (needed to compile Pycosat), install Pycosat from the included `pycosat-0.6.0.win32-py3.4.exe` installer.
4. Run `build.bat` if using Windows, and `build.sh` otherwise. Wait for it to finish installing the Python packages needed to run this app.
5. RECOMMENDED: Set your own uWaterloo API key for the app by changing `UW_API_KEY` in `uwapi.py`, line 3. You can get a key from [here](http://api.uwaterloo.ca/apikey/). If not specified, a default key is used.
6. Run `courserator.py` to start the server.

Implementation notes
--------------------

The solver uses Pycosat as a constraint solver to directly calculate schedules with no conflicts. This eliminates a lot of the work in searching for non-conflicting schedules. For example, out of a search space of roughly 38,000 possible schedules in the code examples, we can solve for the 72 possibilities within 5 milliseconds.

Reducing the schedule conflicts to SAT clauses is simple. Let $A_1, \ldots, A_m$ be courses, each with sections ${A_i}_1, \ldots, {A_i}_m$. Then to specify that we want one of the sections of each course, we specify the clause ${A_i}_1 \lor \ldots \lor {A_i}_1$ for each $i$.

To avoid multiple sections of the same course being selected, we specify the clauses $\neg {A_i}_x \lor \neg {A_i}_y$ for each distinct set $\left\{x, y\right\}$, for each $i$. Now we have specified that we want one and only one section from each course.

The conflict detector is responsible for detecting every possible pair of conflicting sections. This means that we run it once over all the sections and obtain a list of conflicting pairs, which is a good thing since its time complexity is pretty bad (but still polynomial). However, in practice it completes quickly enough, helped by the fact that we only need to run it once per query.

The conflict detector outputs pairs $({A_i}_x, {A_j}_y)$, which represent the idea that the section ${A_i}_x$ conflicts with ${A_j}_y$. For each of these pairs, we specify the clause $\neg {A_i}_x \lor \neg {A_j}_y$. Now we have specified that the conflicting sections cannot both be chosen.

Solving for all these clauses using the SAT solver, we obtain solutions of the form ${A_1}_x, \ldots, {A_n}_y$ - a list of course sections that were solved for. These are the conflict-free schedules. The only thing left to do after this is display the results.

Essentially:

1. User requests courses to attempt to schedule.
2. Course data for each course is requested from the [uWaterloo Open Data API](http://api.uwaterloo.ca/), computing the start/end times of each individual block for each section. A simple caching mechanism cuts down on unnecessary requests.
3. Conflicts are detected by looking for overlapping blocks.
4. Constraints are generated from the course sections and conflicts between them.
5. Schedules are solved for using PycoSAT.
6. Schedules are formatted and displayed to the user.