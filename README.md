# Challenge 2: # Knowledge base from heterogeneous file sources

Goal of this task is the development of a pipeline step that allows for the processing of a variety of common file formats into plain text chunks for the inclusion in a RAG knowledge base. From this a solid grasp on the challenges associated with various document formats and an understanding of applicable strategies is to be generated.

## Requirements include:
* extensible support for file formats
* generation of text-based chunks ready for embedding and insertion into prompts as supported by common LLM completion APIs
* generation of sensible content previews
* generation of sensible references to the chunk's content in the original document
* future support for Text-Documents, tabular data, in-text images, FAQ-pairs, websites, dynamic database info
* file types: xlsx,docx,pdf,common raster images,

## Tasks:
* choose file formats
* identify challenges in either one of
    * content extraction
    * chunking
    * referencing
    * preview generation
* brainstorm approaches to tackle challenges
* choose example file format
* read in File
* determine processing strategy
* separate document into sensible chunks
* convert into plain text format
* include reference and preview data
* choose sensible output format

## Expected Deliverables:
* A summary of the challenges associated with each file format
* A number of formulated pre-processing strategies
* An example implementation of a pre-processing routine that is extensible to various file formats and processing strategies and that implements at least one strategy for the overcoming of a format-associated challenge
* stretch goal: implement multiple strategies and compare resulting chatbot performance in example RAG deployment

## Bonus question:
record-aligned chunking quickly exceeds winner chunk limits and forces a tradeoff between maintaining already found chunks as part of the conversation context for subsequent prompts on the one hand and focusing on new chunks found based on new prompts at the expense of context awareness. What are alternative approaches to tackle the issue.Creating a knowledge base from heterogeneous file sources

# Material:

## Data
documents in ```/material/```

## links
|Service| URL| user | password|
|-|-|-|-|
|RAGflow|https://blissful-diffie.46-4-9-235.plesk.page|intern@ifii.eu|4!-Haxx0r-25


