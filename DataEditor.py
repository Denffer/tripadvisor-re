import glob, re, sys, os

class DataEditor:
    """ This little program helps to edit the content of the entire dataset, if needed """
    def __init__(self):
        self.src = sys.argv[1]

    def walk(self):
        """ load all reviews in data/backend_reviews/ and merge them """
        corpus = []
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            corpus = []
            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + str(file_list)

                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath+f)
                        break
                    else:
                        print "Editting " + str(dirpath) + "/" + str(f)
                        with open(dirpath + "/" + f) as file:
                            text = file.read()
                            text = self.edit(text)
                            filepath = str(dirpath) + "/" + str(f)
                            self.save(text, filepath)

                print "-"*60

            else:
                print "No file is found"
                print "-"*60

    def edit(self, text):
        """ Edit data and return """
        #attraction_name = re.search('"attraction_name": "(.*)"', text).group(1).replace("_"," ").title()
        #text = re.sub(r'"attraction_name": "(.*)"', r'"attraction_name": "' + attraction_name + '"', text)
        location = re.search('"location": "(.*)"', text).group(1).title()
        text = re.sub(r'"location": "(.*)"', r'"location": "' + location + '"', text)

        return text

    def save(self, text, f):
        """ save and replace the original file"""
        f_out = open(f, "w")
        f_out.write(text)
        f_out.close()

if __name__ == '__main__':
    editor = DataEditor()
    editor.walk()

