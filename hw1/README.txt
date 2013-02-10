README
======

This read me is divided into the following brief sections:
	1. Files included in the zip
	2. Brief description and approx run time
	3. Usage of the search engine
	4. Sample runs


1. Files included in the zip:
-----------------------------

The files included in hw1_nitesh.zip are:

  1. search.py -- The main program which performs searches. It calls the below modules to build the indices.
  2. inverted_index_builder.py -- Builds the inverted index in memory, and pickles it if needed.
  3. positional_index_builder.py -- Builds the positional index in memory, and pickles it if needed.
  4. kgram_index_builder.py -- Builds the kgram index in memory, and pickles it if needed.


2. Brief description:
---------------------

A search engine has been built that indexes the given documents using three techniques: Inverted indexing, Positional indexing and K-gram indexing(with k=2). The indexes are built in memory upon start-up and used from memory itself. There is an option to pickle these indexes to the disk that can be given during start-up. The pickled files are not used for anything though.

The approximate index creation times are:

Without pickling: 20 seconds
With pickling: 45 seconds

After the indices have been created, the program provides a command prompt for the user to start giving queries.


3. Usage of the search engine:
------------------------------

The main file to be executed to build indices and perform searches is search.py. Its usage is shown below:

	Usage: python search.py <doc_directory> [--pickle]

Here, <doc_directory> is the path to the directory containing the documents, whose names are assumed to be of the same format as provided, i.e. <doc_id>.txt. The path can be relative or absolute. Please make sure that the program is given the permissions to execute commands, as it reads the documents in ascending order of doc_id by executing the command 'ls <directory_path> | sort -n' internally.

The option [--pickle] is optional and if provided, pickles the indices to the disk. The index creation time is a bit longer if this option is provided as well. Please make sure that file-write permissions are present if pickling is needed. 

Hit Ctrl+C to exit the program. 


4. Sample runs:
---------------

Run 1:
------

nitsood@neptune$ python search.py books/books/

Building positional index..
Done
Building inverted index..
Done
Building kgram index..
Done

>> j*h balt* *rick

23  119  245  376  543  693  712  820 

>> "mark twain" "what is man"

70  119 

>> "and the part he"

471  712 

>> acbxyz xt

No match

>> ^C
Bye


Run 2:
------

nitsood@neptune$ python search.py books/books/ --pickle

Building positional index..
Done
Index pickled to file pos_index.pick
Building inverted index..
Done
Index pickled to file inv_index.pick
Building kgram index..
Done
Index pickled to file kgram_index.pick

>> ^C     
Bye

==========================================================================

