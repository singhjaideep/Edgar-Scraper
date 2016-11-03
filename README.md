# Edgar-scraper

This is a script that parses fund holdings pulled from EDGAR, given a ticker or CIK. E.g if run like this:

python edgarparse.py 1166559

It will produce two files: 13FHR_1166559_20161031.txt and 13F-HRA_1166559_20161031.txt

The output files format is : FilingType_CIK_Date.txt

The script should work for all Tickers/CIK, but might fail with some with weird edge cases.

I dealt primarily with two formats 13F-HR and 13F-HR/A:
13F-HR : This was a xml format, so I used lxml to parse the data accordingly. There were a lot of hair tearing problems with
parsing, but I used the simplest, straightforward way that gets the job done in the limited time I had.
13F-HR/A: This was a tabular format, so I had to artfully get the offset for the elements in each line. Again, not the ideal
solution, but get the job done for this specific example.

# Future
Ideally, instead of creating custom hand crafted parsers for each file type, which is time consuming and doesn't scale; I wouldv'e
gone with some natural Language processing. I would use the nltk library, and use a custom tokenizer to figure out, what part of
document would strongly coorelate to Name Of Issuer or Title of class of shares etc.