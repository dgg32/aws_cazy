import requests
import re
from datetime import datetime
from threading import Thread
import queue, sys
import argparse
from lxml import etree
import os

in_queue = queue.Queue()


records_per_page = 1000

prefix = "http://www.cazy.org/"

fivefamilies = {"GH": "Glycoside-Hydrolases.html", "GT": "GlycosylTransferases.html", "PL": "Polysaccharide-Lyases.html", "CE": "Carbohydrate-Esterases.html", "CBM": "Carbohydrate-Binding-Modules.html", "AA": "Auxiliary-Activities.html"}
#fivefamilies = ["Auxiliary-Activities.html"]

rx_member = re.compile(r'<option value="(\S+?)">\w+</option>')
rx_kingdom = re.compile(r'<a href="(http://www\.cazy\.org/\w+_(archaea|bacteria|eukaryota|viruses|characterized|structure)\.html)">\w+</a> (?:&#40;|\()(\d+).*(?:&#41;|\))</span>')
rx_subfamilies_exist = re.compile(r'http://www\.cazy\.org/\w+_subfamilies\.html">Subfamilies')
rx_ncbi = re.compile(r'http://www\.ncbi\.nlm\.nih\.gov/entrez/viewer\.fcgi\?db=protein\S+val=(\S+)"')
acc_cazy = {}

cazy_acc = {}

characterized = set()
structure = set()

exclusion_list = set()


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--excl", help='Textfile with families that are no longer needed', required=False)
parser.add_argument("-f", "--fam", help='family', required=False, default="all")
parser.add_argument("-o", "--out", help='Fasta output', required=True)
parser.add_argument("-l", "--lst", help='Text output with families processed', required=True)

args = parser.parse_args()
argsdict = vars(args)

if argsdict["excl"] and os.path.isfile(argsdict["excl"]):
    for line in open(argsdict["excl"], 'r'):
        exclusion_list.add(line.strip())


thisTime = []

if argsdict["fam"] in list(fivefamilies.keys()):
    thisTime.append(fivefamilies[argsdict["fam"]])

if len(thisTime) == 0:
    thisTime = [fivefamilies[x] for x in fivefamilies]


def work():
    while True:
        url = in_queue.get()
        #try:
        #f = urlopen(address).read().decode('utf-8')
        page = requests.get(url).content.decode('iso8859-1')
        #page = urllib2.urlopen(url).read()
        cazy_name = re.findall("http://www\.cazy\.org/(\w+)\.html", url)[0]
        #print (cazy_name)
        #print (url)
        sub_family_exist = False            
        if rx_subfamilies_exist.search(page):
            sub_family_exist = True
        taxonurl = []
        
        for taxon in rx_kingdom.findall(page):
            taxonurl.append(taxon[0])
            
            
            amount = int(taxon[2])
            #print taxon.group(1), amount
            subpages_minus_one = int((amount-1)/records_per_page)
            
            for i in range(subpages_minus_one):
                taxonurl_address = prefix + "/" +  cazy_name + "_" + taxon[1] +  ".html?debut_PRINC=" + str((i+1)*1000) + "#pagination_PRINC"
                #print taxonurl_address
                taxonurl.append(taxonurl_address)
        
        
        for taxonurl_address in taxonurl:
            charac = False
            structu = False
                
            
            if  "characterized" in taxonurl_address:
                charac = True
            if  "structure" in taxonurl_address:
                structu = True
                
            taxonpage = requests.get(taxonurl_address).content.decode('iso8859-1')
            tree = etree.HTML(taxonpage)
            trs = tree.xpath("//tr")
            for tr in trs:
                #contents = etree.HTML(etree.tostring(tr)).xpath("//td")
                #print etree.tostring(tr)
                tds = etree.HTML(etree.tostring(tr)).xpath("//td")
                
                accession = ""
                family_subfamily =cazy_name 
                for td in tds:
                    #print etree.tostring(td)
                    
                    search_ncbi = rx_ncbi.search(etree.tostring(td).decode())

                    if search_ncbi:
                        accession = search_ncbi.group(1).strip()
                        #print accession


                
                    if sub_family_exist:         
                        sub_family = re.search(r'<td id="separateur2" align="center">(\d+)</td>',etree.tostring(td).decode())
                    
                        if sub_family:
                            family_subfamily +=   "-subfamily_" + sub_family.group(1)
                if accession != "" and family_subfamily not in exclusion_list:
                    #print (exclusion_list)

                    if accession not in acc_cazy:
                        acc_cazy[accession] = set()
                    acc_cazy[accession].add(family_subfamily)
            
                    if family_subfamily not in cazy_acc:
                        cazy_acc[family_subfamily] = set()
                    cazy_acc[family_subfamily].add(accession)
    
                    if charac == True:
                        characterized.add(accession)
                    
                    if structu == True:
                        structure.add(accession)

    # except:
    #     pass
    
    # finally:
        in_queue.task_done()


for i in range(70):
    t = Thread(target=work)
    t.daemon = True
    t.start()
    

for family in thisTime:
    address = prefix + family
    #print (family)
    
    
    f = requests.get(address).content.decode('iso8859-1')

    for member in rx_member.findall(f):

        cazy_name = re.findall("http://www\.cazy\.org/(\w+)\.html", member)[0]


        in_queue.put(member)
        



in_queue.join()


#print "now writing, wish me luck"
prefix = "https://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&rettype=fasta&id="
id_per_request = 200


def getSeq (id_list):
    url = prefix + id_list[:len(id_list)-1]

    temp_content = ""
    try:
    	temp_content += requests.get(url).content.decode('iso8859-1')
        #temp_content += urllib2.urlopen(url).read()

    except:
        for id in id_list[:len(id_list)-1].split(","):
            url = prefix + id
    #print url
            try:
            	temp_content += requests.get(url).content.decode('iso8859-1')
                #temp_content += urllib2.urlopen(url).read()
            except:
            #print id
                pass
    return temp_content

done = set()

for cazy_name in sorted(cazy_acc.keys()):
    content = ""
    #print cazy_name
    temp_content = ""
    id_list = ""
    counter = 0
    
    for acc in cazy_acc[cazy_name]:
        if acc not in done:
            done.add(acc)
        #if str.isdigit(acc[0]):
        #    continue

            id_list += acc + ","
            counter += 1
        
            if counter == id_per_request:
                try:
                    counter = 0
                    temp_content += getSeq(id_list)
                    id_list = ""
                except:
                    pass
    
        if id_list != "":
            try:
                temp_content += getSeq(id_list)
                id_list = ""
            except:
                pass
            
    for line in temp_content.splitlines():
        #print (line, cazy_acc)
        
        if ">" in line:
            print (str(datetime.now()), line)
            content += line
            for acc in cazy_acc[cazy_name]:
                try:
                    if acc in  line[1:].split(" ")[0]:
                        content += "|cazy"
                        for cazy in acc_cazy[acc]:
                            content += "|" + cazy
                    
                
                        if acc in characterized:
                            content += "_characterized"
                
                        if acc in structure:
                            content += "_structure"
                        
                        found = True
                        break
                except:
                    print (line)
                    sys.exit()
            
            #if found == False:
            #    print line + " no acc found in cazy_acc"
            content += "\n"
        else:
            content += line.strip() + "\n"
    #print (content)

    

    with open(argsdict["out"], "a") as myfile:
        myfile.write(content)


    with open(argsdict["lst"], "a") as myfile:
        myfile.write(cazy_name + "\n")