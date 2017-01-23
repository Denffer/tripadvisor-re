import pandas as pd
import os, json, re, sys
import xlsxwriter

input_source = sys.argv[1]
filename = re.search("data/results/([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)", input_source).group(1)
print filename
results = []
for dirpath, dir_list, file_list in os.walk("data/results/" + filename + "/"):
    print "Walking into directory: " + str(dirpath)

    # in case there is a goddamn .DS_Store file
    if len(file_list) > 0:
        print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

        file_cnt = 0
        length = len(file_list)
        for f in file_list:
            if str(f) == ".DS_Store":
                print "Removing " + dirpath + str(f)
                os.remove(dirpath + "/" +f)
                break
            else:
                file_cnt += 1
                #print "Found " + str(dirpath) + "/" + str(f)
                with open(dirpath +"/"+ f) as file:
                    results.append(json.load(file))

    else:
        print "No file is found"
        print "-"*80

type_list = []
threshold_list, topN_list, topN_max_list, window_size_list, min_count_list, ranking_function_list = [], [], [], [], [], []
spearmanr_list1, spearmanr_list2, kendalltau_list1, kendalltau_list2, ndcg5_list1, ndcg5_list2, ndcg10_list1, ndcg10_list2 = [], [], [], [], [], [], [], []
for result in results:
    for result_dict in result:
        #print result_dict
        type_list.append(result_dict["type"])
        threshold_list.append(result_dict["threshold"])
        topN_list.append(result_dict["topN"])
        #topN_max_list.append(result_dict["topN_max"])
        window_size_list.append(result_dict["window_size"])
        min_count_list.append(result_dict["min_count"])
        ranking_function_list.append(result_dict["ranking_function"])
        spearmanr_list1.append(result_dict["computed_vs_reranked_spearmanr"])
        spearmanr_list2.append(result_dict["computed_vs_original_spearmanr"])
        kendalltau_list1.append(result_dict["computed_vs_reranked_kendalltau"])
        kendalltau_list2.append(result_dict["computed_vs_original_kendalltau"])
        ndcg5_list1.append(result_dict["computed_vs_reranked_ndcg@5"])
        ndcg5_list2.append(result_dict["computed_vs_original_ndcg@5"])
        ndcg10_list1.append(result_dict["computed_vs_reranked_ndcg@10"])
        ndcg10_list2.append(result_dict["computed_vs_original_ndcg@10"])

# Create a Pandas dataframe from some data.
df = pd.DataFrame(
        {'type': type_list,
            'threshold': threshold_list,
            'topN': topN_list,
            #'topN_max': topN_max_list,
            'window_size': window_size_list,
            'min_count': min_count_list,
            'ranking_function': ranking_function_list,
            'computed_vs_reranked_spearmanr': spearmanr_list1,
            'computed_vs_original_spearmanr': spearmanr_list2,
            'computed_vs_reranked_kendalltau': kendalltau_list1,
            'computed_vs_original_kendalltau': kendalltau_list2,
            'computed_vs_reranked_ndcg@5': ndcg5_list1,
            'computed_vs_original_ndcg@5': ndcg5_list2,
            'computed_vs_reranked_ndcg@10': ndcg10_list1,
            'computed_vs_original_ndcg@10': ndcg10_list2
    })
df = df[['type', 'threshold', 'topN', 'window_size', 'min_count', 'ranking_function',
    'computed_vs_reranked_spearmanr',
    'computed_vs_original_spearmanr',
    'computed_vs_reranked_kendalltau',
    'computed_vs_original_kendalltau',
    'computed_vs_reranked_ndcg@5',
    'computed_vs_original_ndcg@5',
    'computed_vs_reranked_ndcg@10',
    'computed_vs_original_ndcg@10'
    ]]

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('data/excel/' + filename + '.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1', header = True)
#writer.sheets['Sheet1'].column_dimensions['A'].width = 15

# Close the Pandas Excel writer and output the Excel file.
writer.save()
