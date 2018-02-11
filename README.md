# Insight Data Engineering Coding Challenge
This is my solution to Insight Data Engineering [coding challenge](https://github.com/InsightDataScience/donation-analytics). Very concisely, the challenge is to generate cleaned up data on the fly for repeat donors to campaign contributions using raw data. 

### Dependencies

* Python 2.7+ (or Python 3)

### Approach

The first step is extracting relevant fields from each line in the raw data and performing checks to ensure that fields are valid. Following checks are performed (see `Parser.parse_line` function in `src/parser.py`):

*  `CMTE_ID` should be string and not be empty.
* `ZIP_CODE` is required to have a length of at least 5 and be digits. All entries not satisfying this criteria are ignored. Only the first five digits of zip-code are used from here on.
* `TRANSACTION_DT` should be a valid date, we use the python in-built `datetime.strptime` function for converting string to `datetime` object. If an exception is raised during this conversion, that entry is regarded as malformed and ignored. 
* `TRANSACTION_AMT` is first converted from string to float and then rounded to integer. Any exceptions raised during this process, possibly due to the field being empty or malformed, results in the entry being ignored. 
* `OTHER_ID` is required to empty, if not then the entry is ignored.

For identifying repeat donors, we create a list of all donors identified by their name and zip-code. For example, a donor with name `FOLEY, JOSEPH` and zip code `04105` is assigned a (hopefully unique) tag `FOLEY, JOSEPH-04105`. For each entry in raw data, this tag is searched for in the list of all donors. If not found, a new donor is created with this tag. On the other hand, if a donor with same tag already exists, that donor is identified as repeat donor. The only exception to this rule is when the date of donation in the current entry is *earlier* than the date of donation in a previous entry by the same donor. In this case, the entry is ignored. For this exception, we keep a track of latest year of donation for each donor. The implementation for this step can be found in `Parser.add_update_donor` function (unless  otherwise stated, all functions can be found in `src/parser.py`).

There is another data structure which keeps a list of recipients as Python dictionary such that the the recipients are identified by their  `CTME_ID`. For each recipient, a sub-dictionary is created with (year, zip-code) tuple as the keys. The values for the keys is a list of donation amounts (updated with each entry) for the corresponding (year, zip-code).  This part of the code can be found in `Parser.add_update_recipient`. To keep the list of amounts sorted, Python in-built module `bisect` is employed. Note that the recipient is only added  if the donor is identified as a rpeat donor from previous step. 

Finally, the last step is to compute the requested quantities and combine them into the final string that is to be written to file. The only non-trivial quantity is the percentile calculation. Nearest-rank method for percentile can be found in `get_percentile` function in `src/utils.py`. 


### Run instructions

Assuming the directory structure is as follows:

    ├── README.md 
    ├── run.sh
    ├── src
    │   └── parser.py
    |   └── utils.py
    ├── input
    │   └── percentile.txt
    │   └── itcont.txt
    ├── output
    |   └── repeat_donors.txt
    ├── insight_testsuite
        └── run_tests.sh
        └── tests
            └── test_1
            |   ├── input
            |   │   └── percentile.txt
            |   │   └── itcont.txt
            |   |__ output
            |   │   └── repeat_donors.txt
            ├── test_2
                ├── input
                │   └── percentile.txt
                │   └── itcont.txt
                |__ output
                │   └── repeat_donors.txt

i.e. if the input files `percentile.txt` and `itcont.txt` are located inside `input` directory, then running the code is as simple as:

```./run.sh``` 

The output will be created in `output/repeat_donors.txt`.  

If the input files are not in their default directories, you can specify their locations in `run.sh`. 
