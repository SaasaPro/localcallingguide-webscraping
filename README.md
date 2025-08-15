# localcallingguide-webscraping
Python script to get data from localcallingguide.com webpage

It is set to look up for effective records within the past 7 days (1 week).  

<ins>Actions performed when running</ins>

1. Scan the page and scroll pagination 1 by 1
2. Remove rows where BLOCK is a non numeric character
3. Build the lerg file with the lerg template structure.
4. Build the rate file with the rate template structure.
5. Remove duplicate entries.
6. Save the csv generated files in the same directory as the script file is.



