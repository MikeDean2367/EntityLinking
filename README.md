# EntityLinking

> pip install jsonlines

- 需要帮忙check一下评估代码是否有问题。我们的方法的评估的代码在根目录的`our_method_evaluation.py`，baseline的评估代码在`elevant/my_eval.py`。baseline的评估代码是可以直接运行的。简单说下我的评估思路吧：
```python
"""
1. 对于每个mention以 (doc_id, surface_form, qid)三部分构成，一个数据集的都放在一个list中。
2. 在评估的时候，回考虑list的位置，即我们会给`(doc_id, surface_form, qid)`进行编号，最后转换成`(doc_id, surface_form, qid, count)`，其中count是出现的次数，转换的代码在`my_f1()`中
"""
```
关键的问题是，在`my_eval.py`的第124～126行的代码，如下所示：
```pythoon
if 'id' not in mention:
    continue
    # qid = None
```
由于candidate召回率的问题，对于refine的基线而言，如果candidate的打分都很低的话，他会被过滤掉，在字段中表现为`id`字段不显示，一个例子是：`elevant/evaluation-results/refined/refined.aida.kore50.linked_articles.jsonl`的第一个case，可以看到第一个mention是`steve`，但是并没有被识别出来，因为candidate中没有且打分都很低。而在我们的代码中，是一定会从candidate中选一个的：
```python
{
    "id": 0, 
    "title": "Business 01", 
    "text": "After the death of Steve, the former CEO of Apple, his commencement speech at Stanford was watched thousands of times.", 
    "entity_mentions": [
        {"span": [19, 24], "recognized_by": "ReFinED", "linked_by": "ReFinED", "candidates": ["Q1146031", "Q126513", "Q1999447", "Q2347016", "Q2418017", "Q2532395", "Q29564079", "Q314397", "Q3498875", "Q3499048", "Q3499112", "Q39069862", "Q41616", "Q554164", "Q606595", "Q6119718", "Q735048", "Q7611742", "Q7612189", "Q7612363", "Q7613381", "Q7613482", "Q7613526", "Q7613544", "Q7614217", "Q7614223", "Q934752", "Q939194", "Q943812", "Q957940"]}, 
        {"span": [44, 49], "id": "Q312", "recognized_by": "ReFinED", "linked_by": "ReFinED", "candidates": ["Q104819", "Q104850348", "Q1754545", "Q1984161", "Q20056642", "Q201652", "Q213710", "Q2248280", "Q228968", "Q284115", "Q2894504", "Q3017175", "Q312", "Q368215", "Q3854082", "Q421253", "Q4781101", "Q4781117", "Q4781217", "Q48814561", "Q532100", "Q618355", "Q618389", "Q621231", "Q621254", "Q621267", "Q62446736", "Q89", "Q96984443", "Q97358625"]}, 
        {"span": [78, 86], "id": "Q41506", "recognized_by": "ReFinED", "linked_by": "ReFinED", "candidates": ["Q16981298", "Q16981307", "Q173813", "Q18746517", "Q19877521", "Q22078065", "Q2742675", "Q28451043", "Q29101171", "Q2938060", "Q3132713", "Q3250385", "Q368264", "Q41506", "Q4564767", "Q4574166", "Q4614831", "Q4618464", "Q4622484", "Q4626835", "Q4629886", "Q534426", "Q61997859", "Q7598724", "Q7598725", "Q7598726", "Q7598727", "Q8012895", "Q951131", "Q964886"]}
    ], 
    "evaluation_span": [0, 118], 
    "labels": [
        {"id": 0, "span": [19, 24], "entity_id": "Q19837", "name": "Steve Jobs", "parent": null, "children": [], "optional": false, "type": "Q215627"}, 
        {"id": 1, "span": [78, 86], "entity_id": "Q41506", "name": "Stanford University", "parent": null, "children": [], "optional": false, "type": "Q43229"}, 
        {"id": 2, "span": [44, 49], "entity_id": "Q312", "name": "Apple", "parent": null, "children": [], "optional": false, "type": "Q2424752|Q431289|Q43229"}
    ]
}
```

所以上面的代码，如果使用continue，则不会考虑这种情况（对我们有害），如果使用`qid = None`，则在评估其他baseline的时候，会发现refined的结果不是最高，REL才是最高的。所以需要决定选择哪个情况。