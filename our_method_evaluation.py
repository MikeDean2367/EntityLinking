
def extract_mentions(text) -> list:
    # 定义正则表达式以匹配格式为 <MENTION>...</MENTION> 的内容
    pattern = re.compile(r'<MENTION>(.*?)</MENTION>\[LK\]\[_CONTINUE_\]', re.DOTALL)
    
    # 使用正则表达式查找所有匹配项
    matches = pattern.findall(text)
    
    return matches

def evaluate_one_file(file_name:str):
    gt = list()
    pred = list()
    with jsonlines.open(file_name, 'r') as reader:
        doc_id = 0
        for item in reader:
            text = item['text']
            filtered_entity = list()
            
            for label in item["labels"]:
                start, end = label['span']
                if label['entity_id'] == 'Unknown':
                    # 不在库里的不考虑
                    filtered_entity.append(text[start:end].strip())
                else:
                    gt.append(
                        (doc_id, text[start:end].strip(), label["entity_id"])
                    )
            _predicted = extract_mentions(item["output"])   #, pattern=r"<MENTION>(.*?)</MENTION>"
            predicted = list()
            # print(len(filtered_entity),"->",end="")
            # assert len(_predicted) == len(item['output_qid']), \
            #     f"{len(_predicted)} == {len(item['output_qid'])}"
            for mention, qid in zip(_predicted, item['output_qid']):
                if mention.strip() in filtered_entity:
                    filtered_entity.remove(mention.strip())
                else:
                    predicted.append((doc_id, mention.strip(), qid))
            pred.extend(predicted)
            # print(len(filtered_entity))
            doc_id += 1
    
    # print(len(gt), len(pred))
    precision, recall, f1_score = my_f1(gt, pred)
    return f1_score, precision, recall
        