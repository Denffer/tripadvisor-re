import glob, re, sys, os

""" This little program helps to edit the content of the entire dataset, if needed """
document_index = []
for document_name in os.listdir(sys.argv[1]):
    document_path = sys.argv[1] + "/" + document_name

    text = ""
    for document in glob.glob(document_path):
        with open(document) as f:
            text = f.read()

        location = re.search('"location": "(.*)"', text).group(1).title()
        #attraction_name = re.search('"attraction_name": "(.*)"', text).group(1).replace(" ","_")
        text = re.sub(r'"location": "(.*)"', r'"location": "' + location + '"', text)
        #text = re.sub(r'"attraction_name": "(.*)"', r'"attraction_name": "' + attraction_name + '"', text)
        f1 = open(document_path, "w")
        f1.write(text)
        f1.close()



