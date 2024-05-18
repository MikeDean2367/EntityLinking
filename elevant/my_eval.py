import jsonlines
dataset_postfix = [
    ".oke-2015-eval.linked_articles.jsonl",
    ".oke-2016-eval.linked_articles.jsonl",
    ".reuters-128.linked_articles.jsonl",
    ".msnbc-updated.linked_articles.jsonl",
    ".spotlight.linked_articles.jsonl",
    ".aida-conll-test.linked_articles.jsonl",
    ".kore50.linked_articles.jsonl",
]
gt_datasets = [
    ("benchmarks/oke-2015-eval.benchmark.jsonl"),
    ("benchmarks/oke-2016-eval.benchmark.jsonl"),
    ("benchmarks/reuters-128.benchmark.jsonl"),
    ("benchmarks/msnbc-updated.benchmark.jsonl"),
    ("benchmarks/spotlight.benchmark.jsonl"),
    ("benchmarks/aida-conll-test.benchmark.jsonl"),
    ("benchmarks/kore50.benchmark.jsonl"), 
    # ("benchmarks/rss-500.benchmark.jsonl", "rss_model.jsonl")
]


def my_f1(gt, pred):
    new_gt = []
    gt_map = {}
    for item in gt:
        if item in gt_map:
            gt_map[item] += 1
        else:
            gt_map[item] = 0
        new_gt.append(
            f"{gt_map[item]}-{item}"
        )
    new_pred = []
    pred_map = {}
    for item in pred:
        if item in pred_map:
            pred_map[item] += 1
        else:
            pred_map[item] = 0
        new_pred.append(
            f"{pred_map[item]}-{item}"
        )
    # print(new_gt, new_pred)
    gt_set = set(new_gt)
    pred_set = set(new_pred)

    # 计算true positives (TP)
    true_positives = len(gt_set & pred_set)
    
    # 计算false positives (FP) 和 false negatives (FN)
    false_positives = len(pred_set - gt_set)
    false_negatives = len(gt_set - pred_set)

    # 计算precision, recall 和 F1 score
    if true_positives == 0:  # 避免除零错误
        precision = 0
        recall = 0
        f1_score = 0
    else:
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1_score = 2 * (precision * recall) / (precision + recall)
    return precision, recall, f1_score
 

def evaluate():
    folder = "evaluation-results/"
    baselines = [
        folder+"refined/refined.aida", 
        folder+"rel/rel.2014", 
        folder+"rel/rel.2019",
        folder+"tagme/tagme", 
        folder+"neural_el/neural_el",
        folder+"genre/genre.yago",
        folder+"dbpedia-spotlight/dbpedia_spotlight"
    ]
    assert len(baselines) == len(gt_datasets)
    assert len(baselines) == len(dataset_postfix)
    for baseline in baselines:
        output_str = f"{baseline}"
        for i in range(len(gt_datasets)):
            # Step 1. 读取文档
            model_file_path = f"{baseline}{dataset_postfix[i]}"
            gt_file_path = f"{gt_datasets[i]}"
            # print(model_file_path, gt_file_path)
            pred_items = []
            gt_items = []
            with jsonlines.open(model_file_path, "r") as pred_reader:
                for item in pred_reader:
                    pred_items.append(item)
            with jsonlines.open(gt_file_path, "r") as gt_reader:
                for item in gt_reader:
                    gt_items.append(item)
            assert len(gt_items) == len(pred_items)
            
            # Step 2. 提取内容
            gt_result = []
            pred_result = []
            for doc_id, (pred_item, gt_item) in enumerate(zip(pred_items, gt_items)):
                text = pred_item['text']
                assert text == gt_item['text']
                # 先处理gt
                for mention in gt_item['labels']:
                    if mention["entity_id"] == "Unknown":
                        continue
                    start, end = mention['span']
                    surface_form = text[start:end]
                    qid = mention['entity_id']
                    gt_result.append(
                        (doc_id, surface_form, qid)
                    )
                # 再处理pred
                if 'entity_mentions' not in pred_item:
                    continue
                for mention in pred_item['entity_mentions']:
                    start, end = mention['span']
                    surface_form = text[start:end]
                    if 'id' not in mention:
                        continue
                        qid = None
                    else:
                        qid = mention['id']
                    pred_result.append(
                        (doc_id, surface_form, qid)
                    )
            
            # Step 3. 评估
            precision, recall, f1_score = my_f1(gt_result, pred_result)
            output_str = f"{output_str}, {f1_score}"
        print(output_str)

if __name__ == '__main__':
    evaluate()