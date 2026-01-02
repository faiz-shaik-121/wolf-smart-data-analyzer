# Wolf Smart Analyzer

* how this project was built
* why design choices were made
* how the workflow evolved
* what problems it solves
* how the final system came together

This reads like a **project story + implementation walkthrough**, useful for portfolio and interview reviewers.

You can paste this directly into your README.

---

# How This Project Was Built — Development Story and Process

This project was not built in a single step. It went through learning, iteration, design thinking, trial-and-error, and improvement over time. The goal was always to create something practical, meaningful, and useful for real-world analytics work — not just another dashboard or visualization script.

The project started with a simple intention:

> “I want to build a tool that helps analysts clean and understand data before creating reports or dashboards.”

Most tools focus on visualization first,
but in real life analysts first deal with messy datasets.

So instead of starting with charts,
this project focused on:

* cleaning raw data
* understanding structure
* identifying possible keys
* detecting relationships
* preparing data for modeling

This approach makes the project much closer to real BI workflows used in companies.

---

## Step 1 — Understanding the Problem Analysts Face

Before writing any code, I began by asking:

What do analysts struggle with when they receive raw datasets?

The common answers were:

* Too many missing values
* Duplicate records
* Mixed data types
* No clear primary key
* Multiple unrelated tables
* Unknown relationships
* No clarity about table purpose

Most people jump straight to visualization.

But without proper preparation, dashboards become:

* unreliable
* misleading
* difficult to maintain

So the first design principle became:

> The project must improve data quality and understanding first.

This shaped the entire direction of the tool.

---

## Step 2 — Choosing the Right Technologies

Python was selected as the core language because:

* it is widely used in data analytics
* it has strong library support
* it is easy to extend or modify
* it works well with different data formats

Streamlit was chosen because:

* it is lightweight
* it is interactive
* it allows building tools quickly
* it is easy for others to run
* no frontend coding is required

Pandas and NumPy were selected because they are standard tools for:

* data cleaning
* transformations
* profiling
* analysis

Graphviz was included to generate model view diagrams because:

* it represents relationships visually
* it supports schema-style graph layouts
* it feels similar to Power BI Model View

All tool choices were made with one goal in mind:

> Keep the project practical, understandable, and relevant to real analysts.

---

## Step 3 — Designing the Workflow of the Application

Before coding, the core workflow was written out in simple steps.

The intended flow was:

1. User uploads one or more datasets
2. Data gets cleaned and standardized
3. Missing values and duplicates are analyzed
4. Column uniqueness and data types are examined
5. Potential key fields are detected
6. A data dictionary is generated
7. Tables are classified as fact or dimension
8. Relationships between datasets are detected
9. A model diagram is created
10. Cleaned datasets are exported

Designing the workflow first helped in:

* keeping code modular
* preventing feature confusion
* adding features logically instead of randomly

The goal was to make the tool feel like
a real assistant for analysts.

---

## Step 4 — Building the Cleaning Pipeline

The first working component developed was the cleaning engine.

It focused on:

* removing duplicate rows
* trimming extra spaces
* fixing inconsistent values
* handling numeric-like text
* interpreting possible date fields

The intention was not to “force change” the data,
but to improve consistency while staying safe.

This ensured:

* cleaner tables
* more reliable joins
* fewer modeling issues later

This also allowed the application to support many types of datasets.

---

## Step 5 — Adding the Data Quality Report

Once the cleaning step was functional,
the next task was to help the analyst understand:

* how complete the dataset is
* how unique columns are
* where potential issues exist

The quality report included:

* data type
* missing value count
* missing percentage
* unique values
* primary key candidates

This helped answer early business questions like:

“Which column can be used to uniquely identify rows?”

and

“Is this table suitable for building relationships?”

This made the tool much more than a simple cleaning script.

---

## Step 6 — Creating the Data Dictionary Generator

The next major feature was the automatic data dictionary.

Typical datasets lack documentation.

So the tool attempts to infer:

* column purpose
* sample meaning
* uniqueness strength
* potential business role

This improves:

* data transparency
* analyst understanding
* collaboration value

The dictionary works automatically without manual input.

This makes the application helpful
even for completely unknown datasets.

---

## Step 7 — Fact vs Dimension Table Classification

To bring the project closer to BI modeling practice:

A classifier was added to identify:

* fact tables
* dimension tables
* reference tables

The classification uses:

* row count
* numeric density
* structural behavior
* column characteristics

This enables analysts to think in star-schema terms.

It also helps when moving data into Power BI or SQL models.

This feature transformed the project from:

a data tool → into a modeling assistant.

---

## Step 8 — Detecting Relationships Between Tables

The final stage focused on relationships.

The tool looks for:

* common column names
* shared value intersections
* match strength estimates

It does not claim to be perfect.

Instead, it acts as a guide for analysts by:

* highlighting candidate relationships
* revealing potential join paths
* improving table understanding

The model view diagram visually connects tables.

This makes the project feel more complete and professional.

---

## Step 9 — Final Integration and User Experience

Once each module was developed, they were carefully integrated.

The final priorities were:

* stability
* clarity
* usability
* safety
* flexibility

The application now:

* accepts different file formats
* works with different schemas
* prevents unexpected crashes
* informs users instead of failing silently

The design always focused on real-world usefulness,
not just technical experimentation.

---

## Final Outcome

This project evolved into:

* a data preparation tool
* a schema understanding assistant
* a relationship exploration system
* a BI model support utility

It demonstrates:

* practical data engineering thinking
* real analyst workflow awareness
* strong problem understanding
* value beyond visualization

It is designed for people who work with data —
not just for coding demonstration.


