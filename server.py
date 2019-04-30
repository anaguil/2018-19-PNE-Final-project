import http.client
import http.server
import socketserver
import json
from seq import Seq

socketserver.TCPServer.allow_reuse_address = True

# -- API information
HOSTNAME = "rest.ensembl.org"
METHOD = "GET"
ENDPOINT = ""
CONTENT_TYPE = "?content-type=application/json"
PORT = 8000

# -- Advanced level only done in basic level


def connection(ENDPOINT):
    # -- Here we can define special headers if needed
    headers = {'User-Agent': 'http-client'}
    # -- Connect to the server
    conn = http.client.HTTPSConnection(HOSTNAME)
    # -- Send the request. No body (None)
    # -- Use the defined headers
    conn.request(METHOD, ENDPOINT + CONTENT_TYPE, None, headers)
    # -- Wait for the server's response
    r1 = conn.getresponse()
    # -- Print the status
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    # -- Read the response's body and close the connection
    text_json = r1.read().decode("utf-8")
    conn.close()
    # -- Create a variable with the data from the JSON received
    json_object = json.loads(text_json)
    return json_object


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        json_request = False
        json_dict = {}
        contents = ''
        print("Path:", self.path)
        # If the client requests the "/" endpoint open the main page
        if self.path == "/":
            resp_code = 200
            f = open("main.html", 'r')
            contents = f.read()
            content_type = 'text/html'
# --1   If the client requests the list of species
        elif self.path == "/listSpecies" or self.path == "/listSpecies?json=1":
            resp_code = 200
            # List of each specie a dictionary
            species = connection("/info/species")['species']
            number_species = len(species)
            list_species = "<ul>"
            for i, specie in enumerate(species):
                name = specie['display_name']
                list_species += "<li>" + name + "</li>"
                json_dict.update({str(i+1): name})
            html_1 = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Species</title>
            </head>
            <body>"""
            html_2 = "<p><b>Number of species:</b> {}</p>".format(number_species)
            html_3 = "<p><b>List of all the species:</b> {}</p></body></html>".format(list_species)
            f = open("listSpecies.html", 'w')
            f.write(html_1 + html_2 + html_3)
            f.close()
            f = open("listSpecies.html")
            contents = f.read()
            content_type = 'text/html'


# --a   If the client requests the list of species with a limit
        elif self.path.startswith("/listSpecies?limit="):
            try:
                resp_code = 200
                i = self.path.find("limit=") + len("limit=")
                if 'json=1' in self.path:
                    json_request = True
                    j = self.path.find("&")
                    limit = self.path[i:j]
                else:
                    limit = self.path[i:]
                # -- List of species with a limit (each specie is a dictionary)
                species = connection("/info/species")['species']
                number_species = len(species)
                if int(limit) > number_species:
                    limit = number_species
                elif int(limit) < 0:
                    limit = "a"
                list_species = "<ul>"
                for n, specie in enumerate(species):
                    if limit == "0":
                        break
                    elif n != 0 and n == int(limit):
                        break
                    name = specie['display_name']
                    list_species += "<li>" + name + "</li>"
                    json_dict.update({str(n + 1): name})
                html_1 = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Species</title>
                </head>
                <body>"""
                html_2 = "<p><b>Number of species:</b> {}</p>".format(limit)
                html_3 = "<p><b>List of the species:</b> {}</p></body></html>".format(list_species)
                f = open("listSpecies.html", 'w')
                f.write(html_1 + html_2 + html_3)
                f.close()
                f = open("listSpecies.html")
                contents = f.read()
                content_type = 'text/html'
            # If the limit is not correct
            except IndexError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'Cannot process your request. The limit is incorrect'})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
            # If the limit is not a number
            except ValueError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'Cannot process your request. The limit must be an integer'})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'

# --2   If the user requests the Karyotype
        elif self.path.startswith("/karyotype"):
            resp_code = 200
            i = self.path.find("specie=") + len("specie=")
            if "json=1" in self.path:
                json_request = True
                j = self.path.find("&")
                name_specie = self.path[i:j]
            else:
                name_specie = self.path[i:]
            if "+" in name_specie:
                name_specie = name_specie.replace("+", "_")
            try:
                # List with the name of the chromosomes
                kary = connection("/info/assembly/" + name_specie)['karyotype']
                list_chrom = "<ul>"
                for n, chrom in enumerate(kary):
                    list_chrom += "<li>" + chrom + "</li>"
                    json_dict.update({str(n): chrom})
                html_1 = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Karyotype</title>
                </head>
                <body>"""
                html_2 = "<p><b>List of the karyotype of the specie {}:</b> {}</p>".format(name_specie, list_chrom)
                html_3 = "</body></html>"
                f = open("karyotype.html", 'w')
                f.write(html_1 + html_2 + html_3)
                f.close()
                f = open("karyotype.html")
                contents = f.read()
                content_type = 'text/html'
            # If the name of the specie is not found
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the specie {} is not found'.format(name_specie)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'

# --3   If the user requests the chromosome length
        elif self.path.startswith("/chromosomeLength"):
            resp_code = 200
            i = self.path.find("specie=") + len("specie=")
            j = self.path.find("chromo=") + len("chromo=")
            name_specie = self.path[i:self.path.find("&chromo")]
            if 'json=1' in self.path:
                json_request = True
                k = self.path.find('&json')
                name_chromosome = self.path[j:k]
            else:
                name_chromosome = self.path[j:]
            if "+" in name_specie:
                name_specie = name_specie.replace("+", "_")
            try:
                loop = True
                length_chromosome = ''
                # List with dictionaries that contain the name and length of the chromosomes
                length_chromosomes = connection("/info/assembly/" + name_specie)['top_level_region']
                for dicti in length_chromosomes:
                    n_chromosome = dicti['name']
                    if n_chromosome == name_chromosome:
                        length_chromosome = dicti['length']
                        loop = False
                        break
                if loop is True:
                    if json_request is True:
                        json_dict.update({'error': 'The chromosome {} is not found'.format(name_chromosome)})
                    else:
                        f = open("error_parameter.html", 'r')
                        contents = f.read()
                        content_type = 'text/html'
                else:
                    json_dict.update({'Chromosome': name_chromosome, 'Length': length_chromosome})
                    html_1 = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Chromosome length</title>
                    </head>
                    <body>"""
                    html_2 = "<p><b>Length of the chromosome {}".format(name_chromosome)
                    html_3 = " of the specie {}:</b> {}</p>".format(name_specie, length_chromosome)
                    html_4 = "</body></html>"
                    f = open("chromosomeLength.html", 'w')
                    f.write(html_1 + html_2 + html_3 + html_4)
                    f.close()
                    f = open("chromosomeLength.html")
                    contents = f.read()
                    content_type = 'text/html'
            # If the name of the chromosome is not found
            except UnboundLocalError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the chromosome {} is not found'.format(name_chromosome)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
            # If the specie is not found
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the specie {} is not found'.format(name_specie)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
# -- MEDIUM LEVEL
# --4   If the user requests the sequence of a gene
        elif self.path.startswith("/geneSeq"):
            try:
                resp_code = 200
                k = self.path.find("gene=") + len("gene=")
                if "json=1" in self.path:
                    l = self.path.find("&json")
                    gene = self.path[k:l]
                else:
                    gene = self.path[k:]
                id_gene = connection("/homology/symbol/human/" + gene)['data'][0]['id']
                sequence_gene = connection("sequence/id/" + id_gene)['seq']
                json_dict.update({'Sequence': sequence_gene})
                html_1 = """<!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <title>Sequence of a gene</title>
                </head>
                <body>"""
                html_2 = "<p><b>Sequence of the gene {}:</b> {}</p>".format(gene, sequence_gene)
                html_3 = "</body></html>"
                f = open("geneSeq.html", 'w')
                f.write(html_1 + html_2 + html_3)
                f.close()
                f = open("geneSeq.html")
                contents = f.read()
                content_type = 'text/html'
            # If the gene is wrong or not found
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the gene {} is not found'.format(gene)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
# --5
        elif self.path.startswith("/geneInfo"):
            try:
                resp_code = 200
                k = self.path.find("gene=") + len("gene=")
                if 'json=1' in self.path:
                    l = self.path.find("&json")
                    gene = self.path[k:l]
                else:
                    gene = self.path[k:]
                id_gene = connection("/homology/symbol/human/" + gene)['data'][0]['id']
                sequence_gene = connection("/sequence/id/" + id_gene)['seq']
                info_gene = connection("/lookup/id/" + id_gene)
                chromo = info_gene['seq_region_name']
                end = info_gene['end']
                start = info_gene['start']
                sequence_gene = Seq(sequence_gene)
                length_seq = sequence_gene.len()
                json_dict.update({'Start': start, 'End': end, 'Length sequence': length_seq, 'Id of gene': id_gene, 'Chromosome': chromo})
                html_1 = """<!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <title>Gene information</title>
                </head>
                <body>"""
                html_2 = "<p><b>Start of the gene:</b> {}".format(start)
                html_3 = "<br><b>End of the gene:</b> {}".format(end)
                html_4 = "<br><b>Length of the gene:</b> {}".format(length_seq)
                html_5 = "<br><b>Id of the gene:</b> {}".format(id_gene)
                html_6 = "<br><b>Chromosome that contains the gene:</b> {}".format(chromo)
                html_7 = "</body></html>"
                f = open("geneSeq.html", 'w')
                f.write(html_1 + html_2 + html_3 + html_4 + html_5 + html_6 + html_7)
                f.close()
                f = open("geneSeq.html")
                contents = f.read()
                content_type = 'text/html'
            # If the gene is wrong or not found
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the gene {} is not found'.format(gene)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'

# --6   If the user requests calculations on the sequence of a gene
        elif self.path.startswith("/geneCalc"):
            try:
                resp_code = 200
                k = self.path.find("gene=") + len("gene=")
                if 'json=1' in self.path:
                    l = self.path.find("&json")
                    gene = self.path[k:l]
                else:
                    gene = self.path[k:]
                id_gene = connection("/homology/symbol/human/" + gene)['data'][0]['id']
                sequence_gene = connection("/sequence/id/" + id_gene)['seq']
                sequence_gene = Seq(sequence_gene)
                length_seq = sequence_gene.len()
                perc_print = ""
                json_dict.update({'Length': length_seq})
                for base in 'ACGT':
                    perc = sequence_gene.perc(base)
                    perc_print += "<br>The percentage of the base {} is: {}% <br>".format(base, perc)
                    json_dict.update({'{}'.format(base): '{}%'.format(perc)})
                html_1 = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Calculations on sequence of a gene</title>
                </head>
                <body>"""
                html_2 = "<b>Total length of the sequence of the gene {}:</b> {}".format(gene, length_seq)
                html_3 = "<p>{}</p></body></html>".format(perc_print)
                f = open("geneCalc.html", 'w')
                f.write(html_1 + html_2 + html_3)
                f.close()
                f = open("geneCalc.html")
                contents = f.read()
                content_type = 'text/html'
            # If the gene is wrong or not found, doesn't work in json
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'The name of the gene {} is not found'.format(gene)})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
# --7   # If the user requests names of the genes located in the chromosome "chromo" from the start to end positions
        elif self.path.startswith("/geneList"):
            try:
                resp_code = 200
                i = self.path.find("start=") + len("start=")
                j = self.path.find("&end")
                region_start = self.path[i:j]
                k = self.path.find("end=") + len("end=")
                if 'json=1' in self.path:
                    l = self.path.find('&json')
                    region_end = self.path[k:l]
                else:
                    region_end = self.path[k:]
                region = region_start + "-" + region_end
                n = self.path.find("chromo=") + len("chromo=")
                m = self.path.find("&start")
                chromo = self.path[n:m]
                ENDPOINT = "/overlap/region/human/" + str(chromo) + ":" + str(region)
                CONTENT_TYPE = "?content-type=application/json;feature=gene;feature=transcript;feature=cds;feature=exon"
                headers = {'User-Agent': 'http-client'}
                conn = http.client.HTTPSConnection(HOSTNAME)
                conn.request(METHOD, ENDPOINT + CONTENT_TYPE, None, headers)
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                # -- Read the response's body and close the connection
                text_json = r1.read().decode("utf-8")
                conn.close()
                # -- Create a variable with the data from the JSON received
                json_object = json.loads(text_json)
                json_dict.update({'Start': region_start, 'End': region_end, 'Chromosome': chromo})
                list_genes = "<ul>"
                list_genes_json = []
                for gene in json_object:
                    type_gene = gene['feature_type']
                    if type_gene == "gene":
                        gene_id = gene['id']
                        list_genes += "<li>" + gene_id + "</li>"
                        list_genes_json.append(gene_id)
                    else:
                        pass
                json_dict.update({'List genes': list_genes_json})
                html_1 = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Names of the genes</title>
                    </head>
                    <body>"""
                html_2 = "<p><b>Start:</b> {}</p><p><b>End:</b> {}</p>".format(region_start, region_end)
                html_3 = "<p><b>Chromosome:</b> {}</p></body></html>".format(chromo)
                html_4 = "<p><b>List of genes:</b> {}</p>".format(list_genes)
                f = open("geneList.html", 'w')
                f.write(html_1 + html_2 + html_3 + html_4)
                f.close()
                f = open("geneList.html")
                contents = f.read()
                content_type = 'text/html'
            # If the chromosome is wrong or not found, doesn't work in json
            except KeyError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'Could not process the request'})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    content_type = 'text/html'
            except TypeError:
                resp_code = 404
                if json_request is True:
                    json_dict.update({'error': 'Could not process the request'})
                else:
                    f = open("error_parameter.html", 'r')
                    contents = f.read()
                    f.close()
                    content_type = 'text/html'
# If the resource requested from the client is incorrect, send an error message
        else:
            resp_code = 404
            f = open("error.html", 'r')
            contents = f.read()
            content_type = 'text/html'
# -- ADVANCED LEVEL
        if 'json=1' in self.path:
            content_type = 'application/json'
            # Encode the information to pass it to the server, you can't pas a dict
            contents = json.dumps(json_dict)

        # Sending the response to the client
        self.send_response(resp_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()
        # Sending the body of the response message
        self.wfile.write(str.encode(contents))
        return


# -- Main program
with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
    print("Serving at PORT: {}".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Stopped by the user")
print("The server is stopped")
