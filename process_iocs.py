#!/usr/bin/env python3

import datetime
import os.path
import warnings
import re
import yaml

from yaml.loader import SafeLoader
from cybox.objects.address_object import Address
from cybox.objects.domain_name_object import DomainName
from cybox.objects.email_message_object import EmailMessage
from cybox.objects.file_object import File
from cybox.objects.uri_object import URI
from jinja2 import Environment, FileSystemLoader, select_autoescape
from stix.core import STIXPackage

# Prevent warning messages from the STIX libraries
warnings.filterwarnings("ignore", category=UserWarning)

# Create sets to store the data parsed from the xml files
ib = set()
ipv4 = set()
ipv6 = set()
urls = set()
fqdns = set()
email_senders = set()
hash_md5 = set()
hash_sha1 = set()
hash_sha256 = set()

xml_files = []  # xml files to process
# Read the configuration file
current_dir = os.getcwd()
config_filename = os.path.join(current_dir, 'config', 'config.yaml')
with open(config_filename) as f:
    try:
        config_data = yaml.load(f, Loader=SafeLoader)
    except yaml.YAMLError as e:
        print("Error in configuration file:")
        print(e)

# Calculate dates to pass to the templates
today = datetime.date.today()
today_str = today.strftime(config_data['output_dir_date_format'])
seven_days = today + datetime.timedelta(days=7)
fourteen_days = today + datetime.timedelta(days=14)
thirty_days = today + datetime.timedelta(days=30)
sixty_days = today + datetime.timedelta(days=60)
ninety_days = today + datetime.timedelta(days=90)

# Set the paths and environment variables for the output files
input_dir = os.path.join(current_dir, config_data['input_dir'])  # input is the subdirectory name
# Subdirectory containing the Jinja2 templates to process, currently named 'templates'
template_dir = os.path.join(current_dir, config_data['template_dir'])
# Create a subdirectory in the output directory containing today's date if it doesn't exist
output_dir = os.path.join(current_dir, 'output', today_str)
ioc_input_filename = os.path.join(input_dir, config_data['ioc_input_filename'])
ioc_error_filename = os.path.join(output_dir, config_data['ioc_error_filename'])

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for f in os.listdir(input_dir):
    file_path = os.path.join(input_dir, f)
    if not os.path.isfile(file_path):
        continue
    if file_path.lower().endswith('.xml'):
        xml_files.append(file_path)

for fn in xml_files:  # Process each xml file
    print("Processing input file: " + fn)
    stix_package = STIXPackage.from_xml(fn)  # Use STIXPackage to parse the xml file

    ib.add(stix_package.stix_header.title.split()[0])  # Title
    for indicator in stix_package.indicators:
        for o in indicator.observables:  # Parse data from indicator:observable tags
            props = o.object_.properties
            if isinstance(props, URI):
                # The URI object contains FQDNs and URLs, verify the type and assign to the correct set
                if props.type_ == "URL":  # URL
                    urls.add(props.value.value)
                if props.type_ == "Domain Name":  # FQDN
                    fqdns.add(props.value.value)
            if isinstance(props, EmailMessage):  # Email
                if props.from_:
                    email_senders.add(props.from_.address_value.value)
                if props.sender:
                    email_senders.add(props.sender.address_value.value)
            if isinstance(props, Address):
                if props.category == "ipv4-addr":
                    ipv4.add(props.address_value.value)  # IPv4 Address
                if props.category == "ipv6-addr":
                    ipv6.add(props.address_value.value)  # IPv6 Address
            if isinstance(props, File):  # Hashes
                if props.hashes.md5:  # Hashes: MD5
                    hash_md5.add(props.hashes.md5.value)
                if props.hashes.sha1:  # Hashes: SHA1
                    hash_sha1.add(props.hashes.sha1.value)
                if props.hashes.sha256:  # Hashes: SHA256
                    hash_sha256.add(props.hashes.sha256.value)
            if isinstance(props, DomainName):
                fqdns.add(props.value.value)  # FQDN

# Process <ioc_input_filename> if it exists
if os.path.isfile(ioc_input_filename):
    with open(ioc_input_filename, 'r') as reader:
        print("Processing ioc file: " + ioc_input_filename)
        ioc_errors = ''
        for line in reader:
            # remove the whitespace, tabs and newline characters
            line = line.strip()
            if not line:  # Skip blank lines / empty strings
                continue
            elif re.fullmatch(config_data['md5_regex'], line):  # md5
                hash_md5.add(line)
            elif re.fullmatch(config_data['sha1_regex'], line):  # sha1
                hash_sha1.add(line)
            elif re.fullmatch(config_data['sha256_regex'], line):  # sha256
                hash_sha256.add(line)
            elif re.fullmatch(config_data['ipv4_regex'], line):  # ipv4
                ipv4.add(line)
            elif re.fullmatch(config_data['ipv6_regex'], line):  # ipv6
                ipv6.add(line)
            elif re.fullmatch(config_data['email_regex'], line):  # email address
                email_senders.add(line)
            elif re.fullmatch(config_data['url_regex'], line): # url
                urls.add(line)
            elif re.fullmatch(config_data['domain_regex'], line):  # domain
                fqdns.add(line)
            else: # log the error
                print("Error processing IOC: " + line)
                ioc_errors = ioc_errors + line + "\n"  #  Use \n for newlines on Windows
        if len(ioc_errors) > 0:
            with open(ioc_error_filename, 'w') as writer:
                writer.write("Unable to detect the type of the these IOCs from the input file ioc.txt\n")
                writer.writelines(ioc_errors)

jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape()
)

#  Sort the sets before passing the data to the templates
ib = sorted(ib)
urls = sorted(urls)
email_senders = sorted(email_senders)
ipv4 = sorted(ipv4)
ipv6 = sorted(ipv6)
hash_md5 = sorted(hash_md5)
hash_sha1 = sorted(hash_sha1)
hash_sha256 = sorted(hash_sha256)
fqdns = sorted(fqdns)

for template_file in os.listdir(template_dir):
    file_path = os.path.join(template_dir, template_file)
    if not os.path.isfile(file_path):
        continue
    template = jinja_env.get_template(template_file)
    # The output file will use the same filename as the Jinja2 template file
    output_file_name = os.path.join(output_dir, template_file)
    # If there is no data to output, you'll get an empty output file so you know the template was processed
    # Existing output files will be overwritten
    of = open(output_file_name, "w")
    of.write(template.render(
        ib=ib,
        urls=urls,
        email_senders=email_senders,
        ipv4=ipv4,
        ipv6=ipv6,
        hash_md5=hash_md5,
        hash_sha1=hash_sha1,
        hash_sha256=hash_sha256,
        fqdns=fqdns,
        today=today,
        seven_days=seven_days,
        fourteen_days=fourteen_days,
        thirty_days=thirty_days,
        sixty_days=sixty_days,
        ninety_days=ninety_days
    ))
    of.close()
print("\nCompleted processing the files, the output was written to: " + output_dir)
if len(ioc_errors) > 0:
    print("\n####################")
    print("Errors were found in the ioc.txt input file and logged to " + ioc_error_filename)
    print("####################")
