Created by Aaron Garland and Joe Diver, with CSIRC at the USEPA

The program process_iocs extracts IOCs manually added to ioc.txt and from STIX XML files that are located in the input directory.  It uses the files in the templates directory to create the output files which are typically queries or .csv files.  The templates use Jinja2 syntax.  Instructions for creating and modifying templates will be added later.

You can manually add IOCs for processing into ioc.txt.  Supported IOC types are: MD5, SHA1, SHA256, domain, URL, IPv4 address, IPv6 address, email address.

To run process_iocs:
 1. In Windows Explorer, open the input subdirectory
    ex. process_iocs\input
 2. Place the your STIX XML files to be processed in this directory
 3. Edit ioc.txt in the input directory
    ex. process_iocs\input\ioc.txt
    * Delete unwanted entries from the last run
    * Paste new IOCs into the text file
    * Each IOC must be on a separate line
    * Blank lines are allowed
    * Tabs and extra spaces should be removed
    * The IOCs are not modified.  If they contain text to keep it from hyperlinking, 
      such as [.], [dot], [@], you will want to remove that before running the program,
      otherwise it will be included in the output files.
 3. In Windows Explorer, navigate up to the program directory, process_iocs
 4. Run the file process_iocs.bat
 5. When complete, it will open a new Explorer window in the output directory

Notes:
 Delete any old STIX XML files from the input subdirectory
 Update the contents of ioc.txt in the input subdirectory
 process_iocs.exe is a compiled python program.  When run, it will extract files into your temp directory and delete them when it finishes.

Files in the output directory:
 defender_domain_url.txt		Defender ATP query for domains and URLs
 defender_indicator_hash_import.csv	Defender ATP hash indicators to import
 defender_indicator_ip_import.csv	Defender ATP IP address indicators to import
 defender_indicator_url_import.csv	Defender ATP Domain and URL indicators to import
 defender_ipv4.txt			Defender ATP query for IPv4 addresses
 defender_ipv6.txt			Defender ATP query for IPv6 addresses
 defender_md5.txt			Defender ATP query for MD5 hashes
 defender_sha1.txt			Defender ATP query for SHA1 hashes
 defender_sha256.txt			Defender ATP query for SHA256 hashes
 ioc_summary.txt			Contains the list of IOCs extracted from ioc.txt and the STIX XML files
 splunk_destipv4.txt			Splunk query for Destination IPv4 addresses
 splunk_destipv6.txt			Splunk query for Destination IPv6 addresses
 splunk_hostname.txt			Splunk query for Hostnames
 splunk_srcipv4.txt			Splunk query for Source IPv4 addresses
 splunk_srcipv6.txt			Splunk query for Source IPv6 addresses

Disclaimer: The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.
