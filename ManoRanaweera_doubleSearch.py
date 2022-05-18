#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import pymysql
#from getpass import getpass
#pswd = getpass()

#the next two lines are useful for debugging
#they cause errors during execution to be sent back to the browser
import cgitb
cgitb.enable()

#the next line gives us a convenient way to insert values into strings
from string import Template 

#form = cgi.FieldStorage(keep_blank_values=True) #tested line for debugging

html_form = """
            <html>
	<head>
		<title>miRNA Database Query</title>
	</head>
<body>
	<h1> Please provide the names of two genes of your choice to see what miRNA targets they share, along with target scores of the corresponding gene for each miRNA.  Examples of gene names include: A1CF, A2LD1, BRCA1, etc.</h1>
	<form name="myForm" action="https://bioed.bu.edu/cgi-bin/students_22/mranawee/ManoRanaweera_doubleSearch.py" method="get">
		Gene 1: <input type="text" name="gene_name_1"><br>
		Gene 2: <input type="text" name="gene_name_2"><br>
		<input type="submit" value="Submit"><br> 
    <h2> The program will return a list of all miRNAs that target both genes. :)</h2>
    </form> 
    </body>
    </html>
            """


#retrieve form data from the web server
form = cgi.FieldStorage(keep_blank_values=True) 


#next line is always required as first part of html output
print("Content-type: text/html\n") #made this only content type print statement to see if form shows on URL

print(html_form)

if(form):
    #get individual values from the form data
    #use getvalue when there is only one instance of the key in the query string
    gene_name_1 = form.getvalue('gene_name_1')
    gene_name_2 = form.getvalue('gene_name_2')
    
    connection = pymysql.connect(host='bioed.bu.edu', 
                                 port=4253, 
                                 user='mranawee', 
                                 database='miRNA', 
                                 password = 'Megaspyguy4')
    
    cursor = connection.cursor()
    query = """
            select symbol, name, term_type, acc, genus, species
            from term join species using (id) join gene_product using (id)
            where symbol = %s
            """

    try:
        cursor.execute(query, [gene_name_1, gene_name_2]) #change to brackets
    except pymysql.error as e:
        print(e)
    
    results = cursor.fetchall()
    
    
    miRNA_count = len(results)
    
    #checking if genes exist in database
    if (len(results) != 0):
        print('Gene {} and gene {} are both targeted by {} miRNAs.'.format(gene_name_1, gene_name_2, miRNA_count))
        
        html_table ="""
                     <html>
                     <body>
                         <head>
                         </head>
                    
                             <table>
                                 <thead>
                                     <tr>
                                         <th>miRNA name</th>
                                         <th>Target score for %s</th>
                                         <th>Target score for %s</th>
                                     </tr>
                                 </thead>
                                 <tbody>
                    """%(gene_name_1,gene_name_2)

        #now add rows to the table, using string substitution
        for row in results:
            html_table += """
                          <tr>
                              <td>%s</td>
                              <td>%s</td>
                              <td>%s</td>
                          </tr>
                          """ %(row[0], row[1], row[2])
        #close table
        html_table += """  
                    </tbody>
                </table>
            </body>
        </html>
        """

        print(Template(html_table).safe_substitute(gene_name_1=gene_name_1, gene_name_2=gene_name_2)) #added template and .safe_substitute
    else:
        query2 = """
                select name
                from gene
                where name = %s or name = %s
                """
        try:
            cursor.execute(query2, [gene_name_1, gene_name_2])
        except pymysql.error as e:
            print(e)
        
        results2 = cursor.fetchall()
        if (len(results2) == 2):  #proceed with zero rows
            print('Gene {} and gene {} are both targeted by 0 miRNAs.'.format(gene_name_1, gene_name_2))
            
            html_table ="""
                         <html>
                         <body>
                             <head>
                             </head>
                                 <table>
                                     <thead>
                                         <tr>
                                             <th>miRNA name</th>
                                             <th>target score for %s</th>
                                             <th>target score for %s</th>
                                         </tr>
                                     </thead>
                                     <tbody>
                        """%(gene_name_1,gene_name_2)
            #now add rows to the table, using string substitution
            for row in results:
                html_table += """
                              <tr>
                                  <td>%s</td>
                                  <td>%s</td>
                                  <td>%s</td>
                              </tr>
                              """ %(row[0], row[1], row[2])
            #close table
            html_table += """  
                        </tbody>
                    </table>
                </body>
            </html>
            """


            print(Template(html_table).safe_substitute(gene_name_1=gene_name_1, gene_name_2=gene_name_2)) #added template and .safe_substitute
        elif (len(results2)==1):
            print('One of the genes does not exist, or was not submitted')
        elif (len(results2)==0):
            print("Genes do not exist") #Let user know genes don't exist in database
    
    cursor.close()
    connection.close()

else:
    html_table = """
    <html>
        <body>
        <head>
            <title>OOPS!</title>
        </head>
        <h1>OOPS!</h1>
            <p>
            Not enough genes submitted...
            </p>
        </body>
    </html> 
                 """
    #print the html
    #nothing to substitute here
    print(Template(html_table).safe_substitute())

    


